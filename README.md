# 🎯 CareerGuidanceAI — Web App

AI-powered career guidance system for Indian students. 
Built with Streamlit, sentence-transformers, and ReportLab.

---

## 🚀 Deploy & Share (FREE — Streamlit Cloud)

### Step 1 — Push to GitHub

```bash
# Create a new GitHub repo named  CareerGuidanceAI
# Then inside this folder:
git init
git add .
git commit -m "Initial deploy"
git remote add origin https://github.com/YOUR_USERNAME/CareerGuidanceAI.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Click **"New app"**
3. Select your GitHub repo → branch `main` → main file `app.py`
4. Click **"Deploy"**
5. In ~3 minutes you get a **public shareable link** like:  
   `https://YOUR_USERNAME-careerguidanceai-app-xxxxxx.streamlit.app`

> That link is all you need to share with testers and reviewers!

---

## 🏃 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
App opens at **http://localhost:8501**

---

## 🧪 Run Tests

```bash
pip install pytest
pytest tests/ -v
```

Expected: **50 tests** across data, engine, resume builder, and integration.

---

## 📁 Project Structure

```
CareerGuidanceAI/
├── app.py              ← Main Streamlit app (all 6 pages)
├── career_data.py      ← Career database, mappings, option lists
├── career_engine.py    ← AI recommendation engine (sentence-transformers)
├── resume_builder.py   ← PDF resume generator (ReportLab)
├── requirements.txt    ← Python dependencies
├── pytest.ini          ← Test config
├── .streamlit/
│   └── config.toml     ← Dark theme + server config
├── model/              ← Trained ML model files (pkl/json)
└── tests/
    └── test_career_guidance.py  ← 50 unit + integration tests
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 Career Guidance | Semantic AI matching using `all-MiniLM-L6-v2` |
| 💬 AI Chat | GPT-4o Mini (optional key) + offline fallback |
| 📄 Resume Builder | Auto-generate professional PDF résumé |
| 📊 Analytics | Plotly bar chart + radar chart + salary table |
| 🔐 Auth | Demo login (name + email) — no password needed |

---

## 🔑 Optional: Add OpenAI Key for AI Chat

In the deployed app → **Settings** page → paste your `sk-...` key.  
Or set the env variable in Streamlit Cloud:  
`OPENAI_API_KEY = sk-your-key`

---

## 📝 Feedback for Testers

Please test and review at the shared link and check:
- [ ] Login works
- [ ] Career recommendations feel relevant
- [ ] Resume PDF downloads correctly
- [ ] Chat answers make sense
- [ ] Analytics charts display
