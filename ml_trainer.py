"""
ml_trainer.py
Trains and evaluates 3 classifiers on student_profiles.csv.
Run once:  python ml_trainer.py
Produces:
  model/ml_model.pkl          — best trained pipeline
  model/ml_report.json        — full evaluation report (accuracy, precision, recall, F1, confusion matrix)
  model/feature_names.json    — ordered feature list (for explainability)
  model/label_classes.json    — ordered class list
"""
from __future__ import annotations
import os, json, joblib, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.ensemble         import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model     import LogisticRegression
from sklearn.svm              import SVC
from sklearn.pipeline         import Pipeline
from sklearn.preprocessing    import LabelEncoder, OneHotEncoder
from sklearn.compose          import ColumnTransformer
from sklearn.model_selection  import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics          import (accuracy_score, precision_score, recall_score,
                                      f1_score, confusion_matrix, classification_report)

DATA_PATH  = os.path.join(os.path.dirname(__file__), "data",  "student_profiles.csv")
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)


# ── Load & preprocess ─────────────────────────────────────────────────────────
def load_data():
    df = pd.read_csv(DATA_PATH)
    FEATURES = ["stream","science_focus","field","hobby","free_time","subject","grade"]
    X = df[FEATURES]
    y = df["career"]
    return X, y, FEATURES


# ── Build preprocessing + classifier pipeline ─────────────────────────────────
def build_pipeline(clf) -> Pipeline:
    cat_features = ["stream","science_focus","field","hobby","free_time","subject","grade"]
    preprocessor = ColumnTransformer([
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
    ])
    return Pipeline([("prep", preprocessor), ("clf", clf)])


# ── Evaluate a single pipeline ────────────────────────────────────────────────
def evaluate(pipe, X_train, X_test, y_train, y_test, name: str) -> dict:
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec  = recall_score(y_test, y_pred,    average="weighted", zero_division=0)
    f1   = f1_score(y_test, y_pred,        average="weighted", zero_division=0)
    cm   = confusion_matrix(y_test, y_pred).tolist()

    # 5-fold cross-validation on full data
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipe, pd.concat([X_train, X_test]),
                                pd.concat([y_train, y_test]),
                                cv=cv, scoring="accuracy")

    # Per-class report
    clf_rep = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    return {
        "model_name":      name,
        "accuracy":        round(acc,  4),
        "precision":       round(prec, 4),
        "recall":          round(rec,  4),
        "f1_score":        round(f1,   4),
        "cv_mean":         round(cv_scores.mean(), 4),
        "cv_std":          round(cv_scores.std(),  4),
        "confusion_matrix":cm,
        "per_class":       clf_rep,
        "pipeline":        pipe,
    }


# ── Feature importance (Random Forest only) ───────────────────────────────────
def get_feature_importance(pipe: Pipeline, feature_names: list[str]) -> list[dict]:
    clf = pipe.named_steps["clf"]
    if not hasattr(clf, "feature_importances_"):
        return []
    ohe   = pipe.named_steps["prep"].named_transformers_["ohe"]
    names = ohe.get_feature_names_out(feature_names)
    imps  = clf.feature_importances_
    pairs = sorted(zip(names, imps), key=lambda x: x[1], reverse=True)
    return [{"feature": str(f), "importance": round(float(i), 5)} for f,i in pairs[:20]]


def train():
    print("=" * 55)
    print("  CareerGuidanceAI — ML Model Training")
    print("=" * 55)

    # ── Load data ─────────────────────────────────────────────────────────────
    print("\n📂 Loading dataset…")
    X, y, features = load_data()
    print(f"   Rows: {len(X)} | Features: {len(features)} | Classes: {y.nunique()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
    classes = sorted(y.unique().tolist())

    # ── Train 3 classifiers ───────────────────────────────────────────────────
    classifiers = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=3,
            class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=1000, C=1.0, solver="lbfgs",
            class_weight="balanced", random_state=42
        ),
        "Support Vector Machine": SVC(
            kernel="rbf", C=2.0, gamma="scale",
            class_weight="balanced", random_state=42, probability=True
        ),
    }

    results = {}
    print("\n🏋️  Training classifiers…\n")

    for name, clf in classifiers.items():
        print(f"   → {name}…", end=" ", flush=True)
        pipe   = build_pipeline(clf)
        result = evaluate(pipe, X_train, X_test, y_train, y_test, name)
        results[name] = result
        print(f"  Acc={result['accuracy']:.4f}  F1={result['f1_score']:.4f}  CV={result['cv_mean']:.4f}±{result['cv_std']:.4f}")

    # ── Compare & pick best ───────────────────────────────────────────────────
    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best      = results[best_name]
    print(f"\n🏆  Best model: {best_name}")
    print(f"   Accuracy : {best['accuracy']*100:.2f}%")
    print(f"   Precision: {best['precision']*100:.2f}%")
    print(f"   Recall   : {best['recall']*100:.2f}%")
    print(f"   F1 Score : {best['f1_score']*100:.2f}%")
    print(f"   CV Mean  : {best['cv_mean']*100:.2f}% ± {best['cv_std']*100:.2f}%")

    # ── Save best pipeline ────────────────────────────────────────────────────
    model_path = os.path.join(MODEL_DIR, "ml_model.pkl")
    joblib.dump(best["pipeline"], model_path)
    print(f"\n💾  Model saved → {model_path}")

    # ── Build serialisable report ─────────────────────────────────────────────
    comparison = []
    for name, r in results.items():
        comparison.append({
            "model":     name,
            "accuracy":  r["accuracy"],
            "precision": r["precision"],
            "recall":    r["recall"],
            "f1_score":  r["f1_score"],
            "cv_mean":   r["cv_mean"],
            "cv_std":    r["cv_std"],
        })

    feat_imp = get_feature_importance(best["pipeline"], features)

    report = {
        "best_model":        best_name,
        "best_accuracy":     best["accuracy"],
        "best_precision":    best["precision"],
        "best_recall":       best["recall"],
        "best_f1":           best["f1_score"],
        "best_cv_mean":      best["cv_mean"],
        "best_cv_std":       best["cv_std"],
        "classes":           classes,
        "n_classes":         len(classes),
        "train_size":        len(X_train),
        "test_size":         len(X_test),
        "features":          features,
        "confusion_matrix":  best["confusion_matrix"],
        "per_class_metrics": best["per_class"],
        "comparison":        comparison,
        "feature_importance":feat_imp,
    }

    report_path = os.path.join(MODEL_DIR, "ml_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"📊  Evaluation report saved → {report_path}")

    # ── Save feature & label info ─────────────────────────────────────────────
    with open(os.path.join(MODEL_DIR, "feature_names.json"), "w") as f:
        json.dump(features, f)
    with open(os.path.join(MODEL_DIR, "label_classes.json"), "w") as f:
        json.dump(classes, f)

    print("\n✅  Training complete!\n")
    print("=" * 55)
    print("  Model Comparison Summary")
    print("=" * 55)
    print(f"  {'Model':<28} {'Acc':>7} {'F1':>7} {'CV':>12}")
    print("  " + "-" * 53)
    for r in sorted(comparison, key=lambda x: x["f1_score"], reverse=True):
        marker = " ✓" if r["model"] == best_name else "  "
        print(f"{marker} {r['model']:<28} {r['accuracy']*100:>6.2f}% "
              f"{r['f1_score']*100:>6.2f}% "
              f"{r['cv_mean']*100:>5.2f}%±{r['cv_std']*100:.2f}%")
    print("=" * 55)

    return report


if __name__ == "__main__":
    train()
