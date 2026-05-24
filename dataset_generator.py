"""
dataset_generator.py
Generates realistic synthetic student profiles → career labels.
Run once:  python dataset_generator.py
Produces:  data/student_profiles.csv  (500 rows, 10 features, 1 label)
"""
from __future__ import annotations
import os, random, csv
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "student_profiles.csv")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ── Feature option sets ───────────────────────────────────────────────────────
STREAMS        = ["Science", "Commerce", "Arts", "Other"]
SCIENCE_FOCUS  = ["Medical", "Non-Medical", "None"]
FIELDS = {
    "Science":  ["Medical & Healthcare","Engineering & Technology",
                 "Research & Development","Data Science & Analytics"],
    "Commerce": ["Finance & Accounting Path","Business & Management",
                 "Economics & Data","Banking & Government Services"],
    "Arts":     ["Law & Legal Services","Psychology & Counseling",
                 "Media & Journalism","Design & Creative Arts"],
    "Other":    ["Government Services","Defense","Sports","Other"],
}
HOBBIES = [
    "Logic & Problem Solving", "Creativity & Design",
    "People Interaction",       "Business & Money",
    "Science & Experiments",    "Technology & Computers",
    "Law & Policy",             "Environment & Nature",
    "Sports & Fitness",         "Media & Communication",
    "Innovation & Future Tech", "Helping & Community",
]
FREE_TIME_OPTIONS = [
    "Coding/Technical Projects",
    "Online Courses/Learning",
    "Reading/Books",
    "Designing/Creative Work",
]
SUBJECTS = [
    "Computer Science","Mathematics","Physics","Chemistry","Biology",
    "Economics","Business Management","Design/Arts","Law","Psychology",
    "AI/ML/Data Science","Political Science",
]
GRADES    = ["A+","A","B+","B","C"]

# ── Career → feature profile mappings ────────────────────────────────────────
# Each career has a probability distribution over features.
# This makes the synthetic data realistic and learnable.
CAREER_PROFILES: dict[str, dict] = {
    "Software Engineer": {
        "streams":     ["Science"],
        "fields":      ["Engineering & Technology","Data Science & Analytics"],
        "hobbies":     ["Technology & Computers","Logic & Problem Solving","Innovation & Future Tech"],
        "free_times":  ["Coding/Technical Projects","Online Courses/Learning"],
        "subjects":    ["Computer Science","Mathematics","AI/ML/Data Science"],
        "science_focus": ["Non-Medical"],
    },
    "Data Scientist": {
        "streams":     ["Science","Commerce"],
        "fields":      ["Data Science & Analytics","Engineering & Technology"],
        "hobbies":     ["Technology & Computers","Logic & Problem Solving","Business & Money"],
        "free_times":  ["Coding/Technical Projects","Online Courses/Learning"],
        "subjects":    ["Mathematics","Computer Science","AI/ML/Data Science","Economics"],
        "science_focus": ["Non-Medical","None"],
    },
    "AI Engineer": {
        "streams":     ["Science"],
        "fields":      ["Engineering & Technology","Data Science & Analytics"],
        "hobbies":     ["Technology & Computers","Innovation & Future Tech","Logic & Problem Solving"],
        "free_times":  ["Coding/Technical Projects","Online Courses/Learning"],
        "subjects":    ["Computer Science","Mathematics","AI/ML/Data Science","Physics"],
        "science_focus": ["Non-Medical"],
    },
    "Doctor": {
        "streams":     ["Science"],
        "fields":      ["Medical & Healthcare"],
        "hobbies":     ["Science & Experiments","Helping & Community","People Interaction"],
        "free_times":  ["Online Courses/Learning","Reading/Books"],
        "subjects":    ["Biology","Chemistry","Physics"],
        "science_focus": ["Medical"],
    },
    "Dentist": {
        "streams":     ["Science"],
        "fields":      ["Medical & Healthcare"],
        "hobbies":     ["Science & Experiments","Helping & Community"],
        "free_times":  ["Online Courses/Learning","Reading/Books"],
        "subjects":    ["Biology","Chemistry"],
        "science_focus": ["Medical"],
    },
    "Research Scientist": {
        "streams":     ["Science"],
        "fields":      ["Research & Development"],
        "hobbies":     ["Science & Experiments","Logic & Problem Solving","Innovation & Future Tech"],
        "free_times":  ["Online Courses/Learning","Reading/Books"],
        "subjects":    ["Physics","Chemistry","Biology","Mathematics"],
        "science_focus": ["Non-Medical","Medical"],
    },
    "Chartered Accountant (CA)": {
        "streams":     ["Commerce"],
        "fields":      ["Finance & Accounting Path"],
        "hobbies":     ["Business & Money","Logic & Problem Solving"],
        "free_times":  ["Online Courses/Learning","Reading/Books"],
        "subjects":    ["Economics","Business Management","Mathematics"],
        "science_focus": ["None"],
    },
    "MBA Leadership Roles": {
        "streams":     ["Commerce","Science","Arts"],
        "fields":      ["Business & Management"],
        "hobbies":     ["Business & Money","People Interaction","Innovation & Future Tech"],
        "free_times":  ["Reading/Books","Online Courses/Learning"],
        "subjects":    ["Business Management","Economics","Mathematics"],
        "science_focus": ["None","Non-Medical"],
    },
    "Business Analyst": {
        "streams":     ["Commerce","Science"],
        "fields":      ["Economics & Data","Business & Management"],
        "hobbies":     ["Business & Money","Logic & Problem Solving","Technology & Computers"],
        "free_times":  ["Online Courses/Learning","Coding/Technical Projects"],
        "subjects":    ["Economics","Business Management","Computer Science","Mathematics"],
        "science_focus": ["None","Non-Medical"],
    },
    "IAS Officer": {
        "streams":     ["Arts","Commerce","Science"],
        "fields":      ["Government Services","Law & Policy"],
        "hobbies":     ["Law & Policy","People Interaction","Helping & Community"],
        "free_times":  ["Reading/Books","Online Courses/Learning"],
        "subjects":    ["Political Science","Economics","Law"],
        "science_focus": ["None"],
    },
    "Lawyer / Advocate": {
        "streams":     ["Arts","Commerce"],
        "fields":      ["Law & Legal Services"],
        "hobbies":     ["Law & Policy","People Interaction","Media & Communication"],
        "free_times":  ["Reading/Books","Online Courses/Learning"],
        "subjects":    ["Law","Political Science","Economics"],
        "science_focus": ["None"],
    },
    "Clinical Psychologist": {
        "streams":     ["Arts","Science"],
        "fields":      ["Psychology & Counseling"],
        "hobbies":     ["Helping & Community","People Interaction"],
        "free_times":  ["Reading/Books","Online Courses/Learning"],
        "subjects":    ["Psychology","Biology"],
        "science_focus": ["None","Medical"],
    },
    "Journalist": {
        "streams":     ["Arts","Commerce"],
        "fields":      ["Media & Journalism"],
        "hobbies":     ["Media & Communication","Creativity & Design","People Interaction"],
        "free_times":  ["Reading/Books","Designing/Creative Work"],
        "subjects":    ["Political Science","Economics","Psychology"],
        "science_focus": ["None"],
    },
    "Graphic Designer": {
        "streams":     ["Arts","Commerce"],
        "fields":      ["Design & Creative Arts"],
        "hobbies":     ["Creativity & Design","Media & Communication"],
        "free_times":  ["Designing/Creative Work","Online Courses/Learning"],
        "subjects":    ["Design/Arts"],
        "science_focus": ["None"],
    },
    "UX/UI Designer": {
        "streams":     ["Arts","Science","Commerce"],
        "fields":      ["Design & Creative Arts"],
        "hobbies":     ["Creativity & Design","Technology & Computers","Logic & Problem Solving"],
        "free_times":  ["Designing/Creative Work","Coding/Technical Projects"],
        "subjects":    ["Design/Arts","Computer Science"],
        "science_focus": ["None","Non-Medical"],
    },
    "Mechanical Engineer": {
        "streams":     ["Science"],
        "fields":      ["Engineering & Technology"],
        "hobbies":     ["Innovation & Future Tech","Logic & Problem Solving","Science & Experiments"],
        "free_times":  ["Coding/Technical Projects","Online Courses/Learning"],
        "subjects":    ["Physics","Mathematics"],
        "science_focus": ["Non-Medical"],
    },
    "Civil Engineer": {
        "streams":     ["Science"],
        "fields":      ["Engineering & Technology"],
        "hobbies":     ["Logic & Problem Solving","Environment & Nature"],
        "free_times":  ["Online Courses/Learning","Coding/Technical Projects"],
        "subjects":    ["Physics","Mathematics"],
        "science_focus": ["Non-Medical"],
    },
    "Entrepreneur / Startup Founder": {
        "streams":     ["Commerce","Science","Arts"],
        "fields":      ["Business & Management"],
        "hobbies":     ["Business & Money","Innovation & Future Tech","Technology & Computers"],
        "free_times":  ["Online Courses/Learning","Coding/Technical Projects"],
        "subjects":    ["Business Management","Economics","Computer Science"],
        "science_focus": ["None","Non-Medical"],
    },
    "Data Analyst": {
        "streams":     ["Commerce","Science"],
        "fields":      ["Economics & Data","Data Science & Analytics"],
        "hobbies":     ["Logic & Problem Solving","Business & Money","Technology & Computers"],
        "free_times":  ["Coding/Technical Projects","Online Courses/Learning"],
        "subjects":    ["Mathematics","Economics","Computer Science"],
        "science_focus": ["None","Non-Medical"],
    },
    "Pharmacist": {
        "streams":     ["Science"],
        "fields":      ["Medical & Healthcare"],
        "hobbies":     ["Science & Experiments","Helping & Community"],
        "free_times":  ["Online Courses/Learning","Reading/Books"],
        "subjects":    ["Chemistry","Biology"],
        "science_focus": ["Medical"],
    },
}

TARGET_CAREERS = list(CAREER_PROFILES.keys())  # 20 classes


def _sample_profile(career: str) -> dict:
    p = CAREER_PROFILES[career]

    stream = random.choice(p["streams"])
    field  = random.choice(p["fields"])
    hobby  = random.choice(p["hobbies"])
    # Add noise: 15% chance of a random hobby
    if random.random() < 0.15:
        hobby = random.choice(HOBBIES)
    free_time = random.choice(p["free_times"])
    subject   = random.choice(p["subjects"])
    # Add noise: 10% chance of a random subject
    if random.random() < 0.10:
        subject = random.choice(SUBJECTS)
    sf = random.choice(p.get("science_focus", ["None"]))
    grade = random.choices(GRADES, weights=[20,30,25,15,10])[0]
    age   = random.randint(16, 22)

    return {
        "stream":        stream,
        "science_focus": sf,
        "field":         field,
        "hobby":         hobby,
        "free_time":     free_time,
        "subject":       subject,
        "grade":         grade,
        "age":           age,
        "career":        career,
    }


def generate_dataset(n: int = 600) -> pd.DataFrame:
    rows = []
    per_class = n // len(TARGET_CAREERS)
    extra     = n % len(TARGET_CAREERS)

    for i, career in enumerate(TARGET_CAREERS):
        count = per_class + (1 if i < extra else 0)
        for _ in range(count):
            rows.append(_sample_profile(career))

    random.shuffle(rows)
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    print("⚙️  Generating student profiles dataset…")
    df = generate_dataset(600)
    df.to_csv(OUT_PATH, index=False)
    print(f"✅ Saved {len(df)} profiles → {OUT_PATH}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Careers: {df['career'].nunique()} classes")
    print(f"   Class distribution:\n{df['career'].value_counts().to_string()}")
