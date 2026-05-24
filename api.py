"""
api.py — Flask REST API for CareerGuidanceAI
Run separately:  python api.py  (default port 5000)

Endpoints:
  GET  /api/health                    → system status
  POST /api/recommend                 → career recommendations
  POST /api/nlp/analyze               → full NLP pipeline
  GET  /api/careers                   → list all careers
  GET  /api/careers/<name>            → career details
  GET  /api/stats                     → platform statistics (SQLite)
  POST /api/feedback                  → submit feedback
  POST /api/bookmark                  → add bookmark
  GET  /api/bookmarks/<email>         → get user bookmarks
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

from career_data   import CAREER_MAPPINGS, ENHANCED_CAREER_DETAILS
from career_engine import build_embeddings, get_recommendations, load_embed_model
from nlp_engine    import full_pipeline
from database      import (
    init_db, save_session, get_top_careers_overall, get_stream_distribution,
    get_user_count, get_session_count, get_feedback_count, get_avg_rating,
    save_feedback, add_bookmark, get_bookmarks, log_career_view,
)

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for front-end integration

# Load models once at startup
print("🔄 Loading AI models…")
_model   = load_embed_model()
_embeds  = build_embeddings(_model)
init_db()
print("✅ API ready")

def _ok(data: dict, status: int = 200):
    return jsonify({"status": "success", "data": data}), status

def _err(message: str, status: int = 400):
    return jsonify({"status": "error", "message": message}), status


# ── GET /api/health ───────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return _ok({
        "service":   "CareerGuidanceAI",
        "version":   "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": True,
        "careers_indexed": len(ENHANCED_CAREER_DETAILS),
        "database": "SQLite connected",
    })


# ── POST /api/recommend ───────────────────────────────────────────────────────
@app.route("/api/recommend", methods=["POST"])
def recommend():
    """
    Body: {
        "text":          "I love coding and maths",
        "stream":        "Science",
        "field":         "Engineering & Technology",   (optional)
        "role":          "Software Engineer",          (optional)
        "science_focus": "Non-Medical",                (optional)
        "top_n":         6,                            (optional)
        "user_email":    "user@example.com"            (optional, for saving)
    }
    """
    data = request.get_json(silent=True) or {}
    text   = data.get("text",   "").strip()
    stream = data.get("stream", "Other")
    field  = data.get("field",  "")
    role   = data.get("role",   "")
    focus  = data.get("science_focus", None)
    top_n  = min(int(data.get("top_n", 6)), 10)
    email  = data.get("user_email", "")

    recs = get_recommendations(
        _model, _embeds,
        user_text=text, stream=stream, field=field,
        role=role, science_focus=focus, top_n=top_n,
    )

    # Persist to SQLite
    if email:
        save_session(email, {"stream": stream, "field": field, "role": role,
                              "aspiration": text}, recs)

    results = [
        {
            "rank":        i + 1,
            "career":      career,
            "match_score": round(score, 4),
            "match_pct":   min(99, int(score * 100)),
            "salary":      ENHANCED_CAREER_DETAILS.get(career, {}).get("salary", "N/A"),
            "description": ENHANCED_CAREER_DETAILS.get(career, {}).get("description", ""),
        }
        for i, (career, score) in enumerate(recs)
    ]
    return _ok({"query": text, "stream": stream, "recommendations": results,
                "total": len(results)})


# ── POST /api/nlp/analyze ─────────────────────────────────────────────────────
@app.route("/api/nlp/analyze", methods=["POST"])
def nlp_analyze():
    """
    Body: {"text": "I enjoy coding and problem solving"}
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return _err("text field is required")
    result = full_pipeline(text)
    return _ok(result)


# ── GET /api/careers ──────────────────────────────────────────────────────────
@app.route("/api/careers", methods=["GET"])
def list_careers():
    stream = request.args.get("stream", "")
    field  = request.args.get("field", "")

    if field and field in CAREER_MAPPINGS["roles"]:
        careers = CAREER_MAPPINGS["roles"][field]
    elif stream and stream in CAREER_MAPPINGS["fields"]:
        careers = []
        for f in CAREER_MAPPINGS["fields"][stream]:
            careers += CAREER_MAPPINGS["roles"].get(f, [])
    else:
        careers = list(ENHANCED_CAREER_DETAILS.keys())

    return _ok({"careers": careers, "total": len(careers)})


# ── GET /api/careers/<name> ───────────────────────────────────────────────────
@app.route("/api/careers/<path:name>", methods=["GET"])
def career_detail(name: str):
    details = ENHANCED_CAREER_DETAILS.get(name)
    if not details:
        return _err(f"Career '{name}' not found", 404)
    log_career_view(name)
    return _ok({"career": name, **details})


# ── GET /api/stats ────────────────────────────────────────────────────────────
@app.route("/api/stats", methods=["GET"])
def stats():
    return _ok({
        "total_users":        get_user_count(),
        "total_sessions":     get_session_count(),
        "avg_rating":         get_avg_rating(),
        "feedback_count":     get_feedback_count(),
        "top_careers":        get_top_careers_overall(5),
        "stream_distribution":get_stream_distribution(),
        "careers_in_db":      len(ENHANCED_CAREER_DETAILS),
    })


# ── POST /api/feedback ────────────────────────────────────────────────────────
@app.route("/api/feedback", methods=["POST"])
def feedback():
    data    = request.get_json(silent=True) or {}
    email   = data.get("user_email", "anonymous")
    rating  = data.get("rating")
    comment = data.get("comment", "")
    feature = data.get("feature", "general")
    if not rating or not (1 <= int(rating) <= 5):
        return _err("rating must be 1–5")
    save_feedback(email, int(rating), comment, feature)
    return _ok({"message": "Feedback saved"})


# ── POST /api/bookmark ────────────────────────────────────────────────────────
@app.route("/api/bookmark", methods=["POST"])
def bookmark():
    data   = request.get_json(silent=True) or {}
    email  = data.get("user_email", "")
    career = data.get("career", "")
    notes  = data.get("notes", "")
    if not email or not career:
        return _err("user_email and career are required")
    added = add_bookmark(email, career, notes)
    return _ok({"bookmarked": added, "career": career})


# ── GET /api/bookmarks/<email> ────────────────────────────────────────────────
@app.route("/api/bookmarks/<email>", methods=["GET"])
def bookmarks(email: str):
    items = get_bookmarks(email)
    return _ok({"bookmarks": items, "total": len(items)})


# ── GET /api/streams ──────────────────────────────────────────────────────────
@app.route("/api/streams", methods=["GET"])
def streams():
    return _ok({
        "streams": CAREER_MAPPINGS["streams"],
        "fields":  CAREER_MAPPINGS["fields"],
    })


if __name__ == "__main__":
    print("\n🎯 CareerGuidanceAI REST API")
    print("=" * 40)
    print("Endpoints:")
    print("  GET  http://localhost:5000/api/health")
    print("  POST http://localhost:5000/api/recommend")
    print("  POST http://localhost:5000/api/nlp/analyze")
    print("  GET  http://localhost:5000/api/careers")
    print("  GET  http://localhost:5000/api/stats")
    print("=" * 40)
    app.run(debug=True, port=5000)
