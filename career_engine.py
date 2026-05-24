"""
career_engine.py
Primary:  Trained sklearn Pipeline (SVM / RF / LR) from ml_trainer.py
Fallback: TF-IDF cosine similarity (always works, no model file needed)
"""
from __future__ import annotations
import os, json
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from career_data import CAREER_MAPPINGS, ENHANCED_CAREER_DETAILS, FIELD_ROLE_MAP

_MODEL_DIR  = os.path.join(os.path.dirname(__file__), "model")
_ML_MODEL   = os.path.join(_MODEL_DIR, "ml_model.pkl")
_CLASSES    = os.path.join(_MODEL_DIR, "label_classes.json")

# ── Thin stubs kept for API compatibility with app.py ────────────────────────
class _FakeModel:
    pass

def load_embed_model() -> _FakeModel:
    return _FakeModel()


# ── TF-IDF fallback engine ────────────────────────────────────────────────────
def build_embeddings(_model) -> dict:
    names, docs = [], []

    def _doc(career, details):
        parts = [career, details.get("description",""),
                 " ".join(details.get("skills",[])),
                 " ".join(details.get("education",[])),
                 details.get("market",""),
                 " ".join(details.get("pros",[])),
                 " ".join(FIELD_ROLE_MAP.get(career, set()))]
        return " ".join(filter(None, parts)).lower()

    for career, details in ENHANCED_CAREER_DETAILS.items():
        names.append(career); docs.append(_doc(career, details))

    for field, roles in CAREER_MAPPINGS["roles"].items():
        for career in roles:
            if career not in ENHANCED_CAREER_DETAILS:
                names.append(career)
                docs.append(f"{career} {field}".lower())

    vec = TfidfVectorizer(ngram_range=(1,2), min_df=1, max_features=5000)
    mat = vec.fit_transform(docs)
    return {"vectorizer": vec, "matrix": mat, "names": names}


# ── Filters ───────────────────────────────────────────────────────────────────
_MEDICAL = {"Doctor","Dentist","Nurse","Pharmacist","Medical Researcher",
            "Biotechnologist","Biomedical Scientist","Lab Technician",
            "Clinical Psychologist","Nutritionist / Dietitian"}
_NON_MED = {"Software Engineer","Data Scientist","Mechanical Engineer",
            "Civil Engineer","Electronics Engineer","Aerospace Engineer",
            "AI Engineer","Robotics Engineer","Research Scientist",
            "EV Technology Engineer","Space Scientist"}

def _is_valid_for_stream(career, stream):
    if stream == "Other": return True
    allowed = set(CAREER_MAPPINGS["fields"].get(stream, []))
    return bool(FIELD_ROLE_MAP.get(career, set()) & allowed)

def _is_valid_for_science_focus(career, focus):
    if not focus: return True
    if focus == "Medical":     return career in _MEDICAL or career not in _NON_MED
    if focus == "Non-Medical": return career in _NON_MED or career not in _MEDICAL
    return True


# ── ML model predictor ────────────────────────────────────────────────────────
_ml_pipeline   = None
_label_classes: list[str] = []

def _load_ml_model():
    global _ml_pipeline, _label_classes
    if _ml_pipeline is not None:
        return True
    if not os.path.exists(_ML_MODEL):
        return False
    try:
        _ml_pipeline = joblib.load(_ML_MODEL)
        if os.path.exists(_CLASSES):
            with open(_CLASSES) as f:
                _label_classes = json.load(f)
        return True
    except Exception:
        return False


def _ml_predict(stream: str, field: str, role: str,
                hobby: str, free_time: str, subject: str,
                science_focus: str, top_n: int) -> list[tuple[str, float]]:
    """Use the trained sklearn pipeline to predict career probabilities."""
    if not _load_ml_model():
        return []
    try:
        row = pd.DataFrame([{
            "stream":        stream or "Science",
            "science_focus": science_focus or "None",
            "field":         field or "Engineering & Technology",
            "hobby":         hobby or "Logic & Problem Solving",
            "free_time":     free_time or "Online Courses/Learning",
            "subject":       subject or "Mathematics",
            "grade":         "A",
        }])
        probs   = _ml_pipeline.predict_proba(row)[0]
        classes = _ml_pipeline.classes_

        ranked = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
        return [(c, float(p)) for c, p in ranked[:top_n] if p > 0.001]
    except Exception:
        return []


# ── TF-IDF fallback predictor ─────────────────────────────────────────────────
def _tfidf_predict(embeddings: dict, user_text: str, stream: str,
                   field: str, science_focus: Optional[str],
                   top_n: int) -> list[tuple[str, float]]:
    vec: TfidfVectorizer = embeddings["vectorizer"]
    mat   = embeddings["matrix"]
    names = embeddings["names"]

    query = " ".join(filter(None,[user_text, field, stream,
        "medical biology" if science_focus=="Medical" else
        "engineering technology maths" if science_focus=="Non-Medical" else ""])).lower() or "general career"

    user_vec = vec.transform([query])
    sims     = cosine_similarity(user_vec, mat).flatten()
    scores   = {name: float(sims[i]) for i, name in enumerate(names)}

    if stream and stream != "Other":
        scores = {c: s for c, s in scores.items() if _is_valid_for_stream(c, stream)}
    if science_focus:
        scores = {c: s for c, s in scores.items() if _is_valid_for_science_focus(c, science_focus)}
    if field:
        fc = set(CAREER_MAPPINGS["roles"].get(field, []))
        scores = {c: (s*1.5 if c in fc else s) for c, s in scores.items()}

    if not scores:
        fallback = list(CAREER_MAPPINGS["roles"].get(field, []))
        if not fallback:
            for f in CAREER_MAPPINGS["fields"].get(stream, []):
                fallback += CAREER_MAPPINGS["roles"].get(f, [])
        scores = {r: 0.5 for r in fallback[:top_n]}

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]


# ── Main public function ──────────────────────────────────────────────────────
def get_recommendations(
    _model,
    embeddings: dict,
    user_text:     str  = "",
    stream:        str  = "Other",
    field:         str  = "",
    role:          str  = "",
    science_focus: Optional[str] = None,
    top_n:         int  = 6,
) -> list[tuple[str, float]]:
    """
    Hybrid prediction:
    1. Try trained ML model (sklearn pipeline) first.
    2. Blend with TF-IDF semantic matching for re-ranking.
    3. Apply stream / science_focus filters.
    Returns list of (career_name, blended_score) sorted descending.
    """
    # ── Extract structured features from user_text where not explicitly given ─
    _hobby     = ""
    _free_time = ""
    _subject   = ""
    for line in user_text.split():
        pass  # structured fields already passed as args

    # Use role as hobby/subject hint if available
    hobby_hint    = role if role else (field if field else "")
    subject_hint  = stream

    # ── ML prediction ─────────────────────────────────────────────────────────
    ml_scores: dict[str, float] = {}
    ml_results = _ml_predict(
        stream=stream, field=field, role=role,
        hobby=hobby_hint, free_time="Online Courses/Learning",
        subject=subject_hint,
        science_focus=science_focus or "None",
        top_n=top_n * 2,
    )
    if ml_results:
        max_p = max(p for _, p in ml_results) or 1.0
        for career, prob in ml_results:
            ml_scores[career] = prob / max_p  # normalise to [0, 1]

    # ── TF-IDF semantic scores ────────────────────────────────────────────────
    tfidf_results = _tfidf_predict(
        embeddings, user_text=user_text, stream=stream,
        field=field, science_focus=science_focus, top_n=top_n * 2,
    )
    tfidf_scores: dict[str, float] = {}
    if tfidf_results:
        max_t = max(s for _, s in tfidf_results) or 1.0
        for career, score in tfidf_results:
            tfidf_scores[career] = score / max_t

    # ── Blend: 60% ML + 40% TF-IDF (or 100% TF-IDF if no ML model) ──────────
    all_careers = set(ml_scores) | set(tfidf_scores)
    if ml_scores:
        blended = {
            c: 0.60 * ml_scores.get(c, 0.0) + 0.40 * tfidf_scores.get(c, 0.0)
            for c in all_careers
        }
    else:
        blended = dict(tfidf_scores)

    # ── Filters ───────────────────────────────────────────────────────────────
    if stream and stream != "Other":
        blended = {c: s for c, s in blended.items() if _is_valid_for_stream(c, stream)}
    if science_focus:
        blended = {c: s for c, s in blended.items() if _is_valid_for_science_focus(c, science_focus)}

    # ── Field boost ───────────────────────────────────────────────────────────
    if field:
        fc = set(CAREER_MAPPINGS["roles"].get(field, []))
        blended = {c: (s * 1.3 if c in fc else s) for c, s in blended.items()}

    # ── Fallback if everything filtered out ───────────────────────────────────
    if not blended:
        fallback = list(CAREER_MAPPINGS["roles"].get(field, []))
        if not fallback:
            for f in CAREER_MAPPINGS["fields"].get(stream, []):
                fallback += CAREER_MAPPINGS["roles"].get(f, [])
        blended = {r: 0.5 for r in fallback[:top_n]}

    ranked = sorted(blended.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # ── Pad to top_n with related careers ────────────────────────────────────
    if len(ranked) < top_n:
        seen = {c for c, _ in ranked}
        for career, score in list(ranked):
            for cf in FIELD_ROLE_MAP.get(career, set()):
                for rel in CAREER_MAPPINGS["roles"].get(cf, []):
                    if rel not in seen and len(ranked) < top_n:
                        ranked.append((rel, score * 0.75))
                        seen.add(rel)

    return ranked[:top_n]
