"""
nlp_engine.py — Visible NLP pipeline for CareerGuidanceAI
Covers: text cleaning, tokenization, stopword removal, keyword extraction,
        TF-IDF scoring, named entity tagging, sentiment proxy, and
        career-intent classification — all explainable for viva.
"""
from __future__ import annotations
import re, math, string
from collections import Counter
from typing import Optional

# ── Stopwords (lightweight — no NLTK download needed) ────────────────────────
STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","he","him","his","himself","she","her","hers","herself","it",
    "its","itself","they","them","their","theirs","themselves","what","which",
    "who","whom","this","that","these","those","am","is","are","was","were",
    "be","been","being","have","has","had","having","do","does","did","doing",
    "a","an","the","and","but","if","or","because","as","until","while","of",
    "at","by","for","with","about","against","between","into","through",
    "during","before","after","above","below","to","from","up","down","in",
    "out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more",
    "most","other","some","such","no","nor","not","only","own","same","so",
    "than","too","very","s","t","can","will","just","don","should","now","d",
    "ll","m","o","re","ve","y","ain","aren","couldn","didn","doesn","hadn",
    "hasn","haven","isn","ma","mightn","mustn","needn","shan","shouldn",
    "wasn","weren","won","wouldn","want","like","love","enjoy","really",
    "also","would","could","one","get","got","let","also","even","much",
    "well","good","great","sure","think","know","feel","need","make","look",
    "go","come","take","work","career","job","profession","field",
}

# ── Career-domain vocabulary for entity tagging ───────────────────────────────
CAREER_ENTITIES = {
    "STREAM":   {"science","commerce","arts","humanities","pcm","pcb"},
    "SUBJECT":  {"maths","mathematics","physics","chemistry","biology","botany",
                 "zoology","economics","accountancy","business","computer","cs",
                 "statistics","psychology","history","geography","political"},
    "EXAM":     {"jee","neet","cat","clat","upsc","gate","gmat","nda","cds",
                 "afcat","ibps","ielts","gre","sat","bitsat","mhtcet","kcet"},
    "SKILL":    {"python","java","c++","sql","excel","figma","autocad","matlab",
                 "tensorflow","pytorch","react","nodejs","aws","ml","ai","nlp",
                 "data","coding","programming","design","drawing","writing"},
    "TRAIT":    {"creative","analytical","logical","empathetic","leader",
                 "problem","solving","communication","teamwork","research",
                 "innovative","curious","patient","disciplined","organised"},
}

ENTITY_COLOR = {
    "STREAM":  "#7c3aed", "SUBJECT": "#0284c7", "EXAM":   "#dc2626",
    "SKILL":   "#059669", "TRAIT":   "#d97706",
}

# ── 1. Text cleaning ─────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ── 2. Tokenize ───────────────────────────────────────────────────────────────
def tokenize(text: str) -> list[str]:
    return clean_text(text).split()

# ── 3. Remove stopwords ───────────────────────────────────────────────────────
def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

# ── 4. Simple stemmer (suffix stripping — no NLTK) ───────────────────────────
def stem(word: str) -> str:
    suffixes = ["ing","tion","ness","ment","ful","ous","ive","ity","er","ed","ly","al","ic"]
    for s in sorted(suffixes, key=len, reverse=True):
        if word.endswith(s) and len(word) - len(s) >= 3:
            return word[:-len(s)]
    return word

def stem_tokens(tokens: list[str]) -> list[str]:
    return [stem(t) for t in tokens]

# ── 5. Keyword extraction (TF score × IDF proxy) ─────────────────────────────
def extract_keywords(text: str, top_n: int = 10) -> list[tuple[str, float]]:
    tokens  = remove_stopwords(tokenize(text))
    if not tokens:
        return []
    freq    = Counter(tokens)
    total   = len(tokens)
    # IDF proxy: rare words in general English score higher
    common  = {"want","like","study","career","work","job","good","going",
               "year","time","college","india","student","people"}
    scores  = {}
    for word, count in freq.items():
        tf  = count / total
        idf = 1.0 if word in common else (1.5 if len(word) <= 4 else 2.2)
        scores[word] = round(tf * idf, 4)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

# ── 6. Named-entity tagging ───────────────────────────────────────────────────
def tag_entities(text: str) -> dict[str, list[str]]:
    tokens  = set(clean_text(text).split())
    found: dict[str, list[str]] = {k: [] for k in CAREER_ENTITIES}
    for label, vocab in CAREER_ENTITIES.items():
        for token in tokens:
            if token in vocab:
                found[label].append(token)
    return {k: v for k, v in found.items() if v}

# ── 7. Sentiment proxy (career confidence score) ─────────────────────────────
_POSITIVE = {"love","enjoy","passionate","excited","motivated","confident","great",
             "excellent","talented","strong","best","expert","skilled","good"}
_NEGATIVE = {"confused","unsure","difficult","hard","worried","afraid","weak",
             "struggle","uncertain","lost","bad","poor"}

def sentiment_score(text: str) -> dict:
    tokens  = set(tokenize(text))
    pos     = len(tokens & _POSITIVE)
    neg     = len(tokens & _NEGATIVE)
    total   = pos + neg
    if total == 0:
        label, score = "Neutral", 0.5
    elif pos >= neg:
        score = round(0.5 + 0.5 * (pos / max(total, 1)), 2)
        label = "Positive 😊" if score >= 0.7 else "Slightly Positive 🙂"
    else:
        score = round(0.5 - 0.5 * (neg / max(total, 1)), 2)
        label = "Negative 😟" if score <= 0.3 else "Slightly Negative 😐"
    return {"label": label, "score": score, "positive_words": pos, "negative_words": neg}

# ── 8. Career-intent classifier ───────────────────────────────────────────────
_INTENT_MAP = {
    "Engineering & Technology":  ["software","coding","programming","tech","computer","algorithm",
                                   "robotics","mechanical","civil","electrical","aerospace","circuit"],
    "Medical & Healthcare":      ["doctor","medical","neet","biology","mbbs","hospital","nurse",
                                   "pharmacy","health","anatomy","surgery","patient"],
    "Data Science & Analytics":  ["data","analysis","ml","ai","statistics","python","machine",
                                   "learning","analytics","tableau","sql","visualization"],
    "Finance & Business":        ["finance","accounting","ca","mba","business","money","bank",
                                   "investment","economics","commerce","audit","tax"],
    "Law & Government":          ["law","upsc","ias","clat","legal","government","policy",
                                   "constitution","advocate","judge","civil"],
    "Design & Creative":         ["design","creative","art","drawing","ux","ui","graphic",
                                   "fashion","animation","photography","content"],
    "Research & Science":        ["research","physics","chemistry","lab","experiment","thesis",
                                   "scientist","theory","paper","journal","discovery"],
}

def classify_intent(text: str) -> list[tuple[str, float]]:
    tokens = set(remove_stopwords(tokenize(text)))
    scores: dict[str, float] = {}
    for domain, keywords in _INTENT_MAP.items():
        hits = len(tokens & set(keywords))
        if hits:
            scores[domain] = round(hits / len(keywords), 4)
    if not scores:
        return [("General / Undecided", 0.5)]
    total = sum(scores.values())
    return sorted(
        [(d, round(s / total, 3)) for d, s in scores.items()],
        key=lambda x: x[1], reverse=True
    )

# ── 9. Full pipeline (one call for the UI) ────────────────────────────────────
def full_pipeline(text: str) -> dict:
    if not text.strip():
        return {"error": "No text provided"}
    tokens_raw      = tokenize(text)
    tokens_clean    = remove_stopwords(tokens_raw)
    tokens_stemmed  = stem_tokens(tokens_clean)
    return {
        "original_text":    text,
        "cleaned_text":     clean_text(text),
        "token_count_raw":  len(tokens_raw),
        "token_count_clean":len(tokens_clean),
        "tokens":           tokens_clean[:20],
        "stemmed_tokens":   tokens_stemmed[:20],
        "keywords":         extract_keywords(text, top_n=8),
        "entities":         tag_entities(text),
        "sentiment":        sentiment_score(text),
        "intent_scores":    classify_intent(text),
    }

# ── 10. TF-IDF explainer (for ML Insights page) ───────────────────────────────
def tfidf_explain(query: str, career_docs: dict[str, str], top_n: int = 5) -> list[dict]:
    """
    Compute TF-IDF scores between query and career documents.
    Returns list of {career, tf, idf, tfidf, matched_terms} for the top careers.
    """
    query_tokens = set(remove_stopwords(tokenize(query)))
    if not query_tokens:
        return []

    # Build document frequency across all careers
    all_tokens: list[set[str]] = []
    for doc in career_docs.values():
        all_tokens.append(set(remove_stopwords(tokenize(doc))))
    N = len(all_tokens)

    results = []
    for career, doc in career_docs.items():
        doc_tokens = remove_stopwords(tokenize(doc))
        if not doc_tokens:
            continue
        freq = Counter(doc_tokens)
        total = len(doc_tokens)
        matched = query_tokens & set(doc_tokens)
        if not matched:
            continue

        tf_sum  = sum(freq[t] / total for t in matched)
        df_sum  = sum(
            sum(1 for dt in all_tokens if t in dt)
            for t in matched
        )
        avg_df  = df_sum / len(matched) if matched else 1
        idf     = round(math.log((N + 1) / (avg_df + 1)) + 1, 4)
        tfidf   = round(tf_sum * idf, 4)

        results.append({
            "career":        career,
            "tf":            round(tf_sum, 4),
            "idf":           idf,
            "tfidf":         tfidf,
            "matched_terms": list(matched)[:6],
        })

    return sorted(results, key=lambda x: x["tfidf"], reverse=True)[:top_n]
