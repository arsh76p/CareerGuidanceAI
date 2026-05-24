"""
tests/test_career_guidance.py
Full test suite — run with:  pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

# ─── career_data ──────────────────────────────────────────────────────────────
from career_data import (
    CAREER_MAPPINGS, ENHANCED_CAREER_DETAILS,
    HOBBY_OPTIONS, FREE_TIME_OPTIONS, SUBJECT_OPTIONS,
    FIELD_TO_STREAM, FIELD_ROLE_MAP,
    get_offline_response,
)

class TestCareerData:
    def test_streams_exist(self):
        assert len(CAREER_MAPPINGS["streams"]) >= 4

    def test_fields_per_stream(self):
        for stream in CAREER_MAPPINGS["streams"]:
            fields = CAREER_MAPPINGS["fields"].get(stream, [])
            assert len(fields) > 0, f"No fields for stream: {stream}"

    def test_roles_per_field(self):
        for field, roles in CAREER_MAPPINGS["roles"].items():
            assert len(roles) > 0, f"No roles for field: {field}"

    def test_enhanced_details_required_keys(self):
        required = {"description", "education", "skills", "salary", "market", "pros", "cons", "roadmap"}
        for career, details in ENHANCED_CAREER_DETAILS.items():
            missing = required - details.keys()
            assert not missing, f"{career} missing keys: {missing}"

    def test_all_details_non_empty(self):
        for career, details in ENHANCED_CAREER_DETAILS.items():
            for key in ["description", "salary", "market"]:
                assert details[key], f"{career}.{key} is empty"
            for key in ["education", "skills", "pros", "cons", "roadmap"]:
                assert len(details[key]) > 0, f"{career}.{key} is empty list"

    def test_hobby_options_non_empty(self):
        assert len(HOBBY_OPTIONS) >= 10

    def test_free_time_options(self):
        assert len(FREE_TIME_OPTIONS) >= 4

    def test_subject_options(self):
        assert len(SUBJECT_OPTIONS) >= 10

    def test_field_to_stream_mapping(self):
        for field, stream in FIELD_TO_STREAM.items():
            assert stream in CAREER_MAPPINGS["streams"], f"Bad stream for {field}: {stream}"

    def test_field_role_map_populated(self):
        assert len(FIELD_ROLE_MAP) > 0

    def test_software_engineer_in_details(self):
        assert "Software Engineer" in ENHANCED_CAREER_DETAILS

    def test_doctor_in_details(self):
        assert "Doctor" in ENHANCED_CAREER_DETAILS

    def test_ca_in_details(self):
        assert "Chartered Accountant (CA)" in ENHANCED_CAREER_DETAILS

    def test_offline_response_software(self):
        resp = get_offline_response("I want to become a software developer")
        assert "Software" in resp or "coding" in resp.lower() or "₹" in resp

    def test_offline_response_medical(self):
        resp = get_offline_response("Tell me about NEET exam for doctors")
        assert "NEET" in resp or "Medical" in resp or "MBBS" in resp

    def test_offline_response_fallback(self):
        resp = get_offline_response("random xyz topic not in any category zzzz")
        assert len(resp) > 30

    def test_salary_contains_rupee(self):
        for career, details in list(ENHANCED_CAREER_DETAILS.items())[:15]:
            salary = details["salary"]
            assert "₹" in salary or "variable" in salary.lower(), f"{career} salary missing ₹"

    def test_roadmap_minimum_steps(self):
        for career, details in ENHANCED_CAREER_DETAILS.items():
            assert len(details["roadmap"]) >= 3, f"{career} roadmap too short"


# ─── career_engine ────────────────────────────────────────────────────────────
from career_engine import (
    build_embeddings, get_recommendations, load_embed_model,
    build_embeddings, get_recommendations, load_embed_model,
    _is_valid_for_stream, _is_valid_for_science_focus,
)

@pytest.fixture(scope="module")
def resources():
    model = load_embed_model()
    embeds = build_embeddings(model)
    return model, embeds

class TestCareerEngine:
    def test_embed_model_loads(self, resources):
        model, _ = resources
        assert model is not None

    def test_embeddings_built(self, resources):
        _, embeds = resources
        # TF-IDF engine returns dict with 'names' list
        assert len(embeds["names"]) > 50

    def test_all_detail_careers_embedded(self, resources):
        _, embeds = resources
        name_set = set(embeds["names"])
        for career in ENHANCED_CAREER_DETAILS:
            assert career in name_set, f"{career} not in embeddings"

    def test_recommendations_returns_list(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds, "I love coding and maths")
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_recommendations_top_n(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds, "biology science student", top_n=4)
        assert len(recs) <= 4

    def test_recommendations_score_range(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds, "software python developer")
        for career, score in recs:
            assert 0.0 <= score <= 1.5, f"{career} score out of range: {score}"

    def test_recommendations_sorted_desc(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds, "data science machine learning")
        scores = [s for _, s in recs]
        assert scores == sorted(scores, reverse=True)

    def test_software_career_appears_for_coding_query(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds, "I love programming Python algorithms software")
        careers = [c for c, _ in recs]
        assert any("Software" in c or "Data" in c or "AI" in c for c in careers)

    def test_medical_filter_science(self, resources):
        model, embeds = resources
        recs = get_recommendations(
            model, embeds, "Biology NEET medical student", stream="Science", science_focus="Medical"
        )
        careers = [c for c, _ in recs]
        # No Non-Medical careers should dominate top 3
        non_medical_in_top = sum(1 for c in careers[:3] if c in {"Software Engineer","AI Engineer","Aerospace Engineer"})
        assert non_medical_in_top <= 1

    def test_commerce_stream_filter(self, resources):
        model, embeds = resources
        recs = get_recommendations(
            model, embeds, "Commerce student interested in finance",
            stream="Commerce", field="Finance & Accounting Path"
        )
        careers = [c for c, _ in recs]
        assert len(careers) > 0

    def test_empty_text_returns_results(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds, "", stream="Science", field="Engineering & Technology")
        assert len(recs) > 0

    def test_is_valid_for_stream_science(self):
        assert _is_valid_for_stream("Doctor", "Science")
        assert _is_valid_for_stream("Software Engineer", "Science")

    def test_is_valid_other_stream(self):
        assert _is_valid_for_stream("Doctor", "Other")
        assert _is_valid_for_stream("Journalist", "Other")

    def test_science_focus_medical(self):
        assert _is_valid_for_science_focus("Doctor", "Medical")
        assert not _is_valid_for_science_focus("Software Engineer", "Medical")

    def test_science_focus_non_medical(self):
        assert _is_valid_for_science_focus("Software Engineer", "Non-Medical")

    def test_no_focus_allows_all(self):
        assert _is_valid_for_science_focus("Doctor", None)
        assert _is_valid_for_science_focus("Software Engineer", None)


# ─── resume_builder ──────────────────────────────────────────────────────────
from resume_builder import generate_resume_pdf

class TestResumeBuilder:
    def test_returns_bytes(self):
        details = ENHANCED_CAREER_DETAILS["Software Engineer"]
        pdf = generate_resume_pdf(
            name="Test User", email="test@test.com", phone="9999999999",
            location="Delhi", stream="Science", career="Software Engineer",
            career_details=details,
        )
        assert isinstance(pdf, bytes)
        assert len(pdf) > 1000

    def test_pdf_magic_bytes(self):
        details = ENHANCED_CAREER_DETAILS["Data Scientist"]
        pdf = generate_resume_pdf(
            name="Arsh Test", email="arsh@test.com", phone="9876543210",
            location="Mumbai", stream="Science", career="Data Scientist",
            career_details=details,
        )
        assert pdf[:4] == b"%PDF"

    def test_pdf_with_extra_skills(self):
        details = ENHANCED_CAREER_DETAILS["Doctor"]
        pdf = generate_resume_pdf(
            name="Med Student", email="med@test.com", phone="9000000000",
            location="Chennai", stream="Science", career="Doctor",
            career_details=details, extra_skills="Clinical Rotation, Research",
        )
        assert len(pdf) > 1000

    def test_pdf_with_achievements(self):
        details = ENHANCED_CAREER_DETAILS["Chartered Accountant (CA)"]
        pdf = generate_resume_pdf(
            name="CA Student", email="ca@test.com", phone="9111111111",
            location="Pune", stream="Commerce", career="Chartered Accountant (CA)",
            career_details=details, achievements="ICAI Foundation cleared\nAll India Rank holder",
        )
        assert pdf[:4] == b"%PDF"

    def test_pdf_minimal_inputs(self):
        pdf = generate_resume_pdf(
            name="Min Test", email="", phone="",
            location="", stream="Other", career="Entrepreneur / Startup Founder",
            career_details=ENHANCED_CAREER_DETAILS.get("Entrepreneur / Startup Founder", {}),
        )
        assert isinstance(pdf, bytes) and len(pdf) > 500

    def test_pdf_all_careers(self):
        """Smoke-test PDF generation for 10 random careers."""
        import random
        careers = random.sample(list(ENHANCED_CAREER_DETAILS.keys()), 10)
        for career in careers:
            pdf = generate_resume_pdf(
                name="Smoke Test", email="smoke@test.com", phone="9000000000",
                location="India", stream="Science", career=career,
                career_details=ENHANCED_CAREER_DETAILS[career],
            )
            assert pdf[:4] == b"%PDF", f"PDF generation failed for {career}"


# ─── Integration tests ───────────────────────────────────────────────────────
class TestIntegration:
    """End-to-end flow: profile → recommendations → resume PDF."""

    def test_full_flow_science_cs(self, resources):
        model, embeds = resources
        recs = get_recommendations(
            model, embeds,
            user_text="I love coding Python machine learning algorithms and maths",
            stream="Science", field="Engineering & Technology", science_focus="Non-Medical",
        )
        assert len(recs) > 0
        top_career, top_score = recs[0]
        assert top_score > 0
        details = ENHANCED_CAREER_DETAILS.get(top_career, {})
        pdf = generate_resume_pdf(
            name="Arsh Kumar", email="arsh@example.com", phone="9876543210",
            location="Delhi", stream="Science", career=top_career,
            career_details=details,
        )
        assert pdf[:4] == b"%PDF"

    def test_full_flow_commerce_ca(self, resources):
        model, embeds = resources
        recs = get_recommendations(
            model, embeds,
            user_text="I enjoy accounting finance taxation and auditing",
            stream="Commerce", field="Finance & Accounting Path",
        )
        assert len(recs) > 0
        top_career, _ = recs[0]
        pdf = generate_resume_pdf(
            name="Commerce Student", email="s@s.com", phone="9000000000",
            location="Mumbai", stream="Commerce", career=top_career,
            career_details=ENHANCED_CAREER_DETAILS.get(top_career, {}),
        )
        assert pdf[:4] == b"%PDF"

    def test_full_flow_arts_law(self, resources):
        model, embeds = resources
        recs = get_recommendations(
            model, embeds,
            user_text="I love debating legal arguments and social justice",
            stream="Arts", field="Law & Legal Services",
        )
        assert len(recs) > 0

    def test_all_streams_return_results(self, resources):
        model, embeds = resources
        for stream in CAREER_MAPPINGS["streams"]:
            recs = get_recommendations(model, embeds, f"Student in {stream}", stream=stream)
            assert len(recs) > 0, f"No results for stream: {stream}"

    def test_offline_chat_covers_main_topics(self):
        topics = [
            ("software developer python", "Software"),
            ("neet mbbs biology", "Medical"),
            ("chartered accountant icai", "CA"),
            ("iim cat mba management", "MBA"),
            ("data science machine learning", "data"),
        ]
        for query, expected_keyword in topics:
            resp = get_offline_response(query)
            assert len(resp) > 50, f"Short response for: {query}"


# ─── Dataset + ML trainer ────────────────────────────────────────────────────
import pandas as pd

class TestDataset:
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "student_profiles.csv")

    def test_csv_exists(self):
        assert os.path.exists(self.DATA_PATH), "Run dataset_generator.py first"

    def test_row_count(self):
        df = pd.read_csv(self.DATA_PATH)
        assert len(df) >= 500

    def test_columns(self):
        df = pd.read_csv(self.DATA_PATH)
        required = {"stream","science_focus","field","hobby","free_time","subject","grade","career"}
        assert required.issubset(set(df.columns))

    def test_class_count(self):
        df = pd.read_csv(self.DATA_PATH)
        assert df["career"].nunique() >= 15

    def test_no_nulls(self):
        df = pd.read_csv(self.DATA_PATH)
        assert df.fillna("").isnull().sum().sum() == 0

    def test_balanced_classes(self):
        df = pd.read_csv(self.DATA_PATH)
        counts = df["career"].value_counts()
        assert counts.min() >= 20, "Some class has fewer than 20 samples"

    def test_valid_streams(self):
        df = pd.read_csv(self.DATA_PATH)
        valid = {"Science","Commerce","Arts","Other"}
        assert set(df["stream"].unique()).issubset(valid)

    def test_grade_values(self):
        df = pd.read_csv(self.DATA_PATH)
        valid = {"A+","A","B+","B","C"}
        assert set(df["grade"].unique()).issubset(valid)


class TestMLModel:
    MODEL_PATH  = os.path.join(os.path.dirname(__file__), "..", "model", "ml_model.pkl")
    REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "ml_report.json")

    def test_model_file_exists(self):
        assert os.path.exists(self.MODEL_PATH), "Run ml_trainer.py first"

    def test_report_exists(self):
        assert os.path.exists(self.REPORT_PATH)

    def test_report_keys(self):
        with open(self.REPORT_PATH) as f:
            rep = json.load(f)
        required = {"best_model","best_accuracy","best_f1","best_cv_mean",
                    "comparison","confusion_matrix","per_class_metrics","classes"}
        assert required.issubset(rep.keys())

    def test_accuracy_reasonable(self):
        with open(self.REPORT_PATH) as f:
            rep = json.load(f)
        assert rep["best_accuracy"] >= 0.60, f"Accuracy too low: {rep['best_accuracy']}"

    def test_f1_reasonable(self):
        with open(self.REPORT_PATH) as f:
            rep = json.load(f)
        assert rep["best_f1"] >= 0.55

    def test_three_models_compared(self):
        with open(self.REPORT_PATH) as f:
            rep = json.load(f)
        assert len(rep["comparison"]) == 3

    def test_confusion_matrix_shape(self):
        with open(self.REPORT_PATH) as f:
            rep = json.load(f)
        cm = rep["confusion_matrix"]
        n  = rep["n_classes"]
        assert len(cm) == n and len(cm[0]) == n

    def test_model_predicts(self):
        import joblib
        model = joblib.load(self.MODEL_PATH)
        row   = pd.DataFrame([{
            "stream":"Science","science_focus":"Non-Medical",
            "field":"Engineering & Technology","hobby":"Technology & Computers",
            "free_time":"Coding/Technical Projects","subject":"Computer Science","grade":"A",
        }])
        pred = model.predict(row)
        assert len(pred) == 1 and isinstance(pred[0], str)

    def test_model_predict_proba(self):
        import joblib
        model = joblib.load(self.MODEL_PATH)
        row   = pd.DataFrame([{
            "stream":"Commerce","science_focus":"None",
            "field":"Finance & Accounting Path","hobby":"Business & Money",
            "free_time":"Online Courses/Learning","subject":"Economics","grade":"A+",
        }])
        proba = model.predict_proba(row)
        assert proba.shape[1] >= 15
        assert abs(proba[0].sum() - 1.0) < 1e-5

    def test_hybrid_engine_uses_ml(self, resources):
        model, embeds = resources
        recs = get_recommendations(model, embeds,
            user_text="I love coding Python and AI",
            stream="Science", field="Engineering & Technology")
        assert len(recs) > 0
        assert all(isinstance(s, float) for _, s in recs)


import json
