"""CareerGuidanceAI v2 — Premium Streamlit Web App"""
from __future__ import annotations
import configparser, os, pathlib, random, smtplib, string, time
import json as _json, urllib.request, math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

st.set_page_config(page_title="CareerGuidanceAI", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

from career_data   import (CAREER_MAPPINGS, ENHANCED_CAREER_DETAILS,
                            HOBBY_OPTIONS, FREE_TIME_OPTIONS, SUBJECT_OPTIONS)
from career_engine import build_embeddings, get_recommendations, load_embed_model
from resume_builder import generate_resume_pdf
from nlp_engine    import full_pipeline, tfidf_explain, ENTITY_COLOR
from database      import (init_db, register_user, verify_login, save_session,
                            add_bookmark, remove_bookmark, get_bookmarks,
                            is_bookmarked, save_feedback, get_avg_rating,
                            get_top_careers_overall, get_stream_distribution,
                            get_session_count, get_user_count, log_career_view,
                            get_most_viewed, get_feedback_count)

init_db()

# ── Config persistence ────────────────────────────────────────────────────────
_CFG = pathlib.Path(__file__).parent / ".api_config.ini"

def _load_keys():
    cfg = configparser.ConfigParser()
    if _CFG.exists():
        cfg.read(_CFG)
        for env, key in [("OPENAI_API_KEY","openai"),("SMTP_EMAIL","smtp_email"),("SMTP_PASSWORD","smtp_password")]:
            v = cfg["keys"].get(key, "") if "keys" in cfg else ""
            if v and not os.environ.get(env, ""):
                os.environ[env] = v

def _save_keys(openai, smtp_e, smtp_p):
    cfg = configparser.ConfigParser()
    cfg["keys"] = {"openai": openai, "smtp_email": smtp_e, "smtp_password": smtp_p}
    with open(_CFG, "w") as f:
        cfg.write(f)

_load_keys()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#060b18!important;color:#e2e8f0;font-family:'Inter',sans-serif}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1526 0%,#060b18 100%)!important;border-right:1px solid rgba(59,130,246,.2)}
[data-testid="stHeader"]{background:transparent!important}
section[data-testid="stSidebar"] .block-container{padding-top:0}

/* Hero */
.hero{background:linear-gradient(135deg,#1e3a8a 0%,#1e1b4b 40%,#0f172a 100%);
      border-radius:24px;padding:52px 40px;text-align:center;margin-bottom:32px;
      border:1px solid rgba(99,102,241,.25);position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;
  background:radial-gradient(circle,rgba(99,102,241,.08) 0%,transparent 70%);pointer-events:none}
.hero h1{font-size:2.8rem;font-weight:900;margin:0 0 12px;color:#fff;letter-spacing:-1px}
.hero p{color:#94a3b8;font-size:1.1rem;margin:0}
.hero-badge{display:inline-block;background:rgba(99,102,241,.2);border:1px solid rgba(99,102,241,.4);
  color:#a5b4fc;border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600;margin-bottom:16px}

/* Glass cards */
.glass{background:rgba(255,255,255,.03);backdrop-filter:blur(20px);
       border:1px solid rgba(255,255,255,.08);border-radius:20px;
       padding:24px;margin-bottom:16px;transition:all .25s}
.glass:hover{border-color:rgba(99,102,241,.4);box-shadow:0 8px 32px rgba(99,102,241,.15);
             transform:translateY(-2px)}
.glass-blue{background:linear-gradient(135deg,rgba(59,130,246,.08),rgba(99,102,241,.05));
            border-color:rgba(59,130,246,.2)}
.glass-purple{background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(99,102,241,.05));
              border-color:rgba(139,92,246,.2)}
.glass-green{background:linear-gradient(135deg,rgba(16,185,129,.08),rgba(5,150,105,.05));
             border-color:rgba(16,185,129,.2)}
.glass-orange{background:linear-gradient(135deg,rgba(245,158,11,.08),rgba(217,119,6,.05));
              border-color:rgba(245,158,11,.2)}

/* Metric tiles */
.metric{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
        border-radius:16px;padding:20px;text-align:center;position:relative;overflow:hidden}
.metric::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#3b82f6,#7c3aed)}
.metric .ico{font-size:2rem;margin-bottom:8px}
.metric .val{font-size:2rem;font-weight:800;color:#60a5fa;line-height:1}
.metric .lbl{font-size:.78rem;color:#64748b;margin-top:6px;font-weight:500;text-transform:uppercase;letter-spacing:.5px}

/* Match bar */
.bar-wrap{background:rgba(255,255,255,.06);border-radius:8px;height:8px;margin:8px 0 16px}
.bar{border-radius:8px;height:8px;background:linear-gradient(90deg,#3b82f6,#7c3aed)}

/* Pills */
.pill{display:inline-block;border-radius:20px;padding:3px 11px;font-size:12px;font-weight:500;margin:2px 3px}
.pill-blue  {background:rgba(59,130,246,.15);color:#93c5fd;border:1px solid rgba(59,130,246,.3)}
.pill-green {background:rgba(16,185,129,.12);color:#6ee7b7;border:1px solid rgba(16,185,129,.3)}
.pill-red   {background:rgba(239,68,68,.12); color:#fca5a5;border:1px solid rgba(239,68,68,.3)}
.pill-purple{background:rgba(139,92,246,.12);color:#c4b5fd;border:1px solid rgba(139,92,246,.3)}
.pill-orange{background:rgba(245,158,11,.12);color:#fcd34d;border:1px solid rgba(245,158,11,.3)}

/* Steps */
.step{display:flex;align-items:flex-start;gap:14px;margin:10px 0;padding:10px;
      background:rgba(255,255,255,.02);border-radius:10px}
.step-num{flex-shrink:0;width:28px;height:28px;border-radius:50%;
  background:linear-gradient(135deg,#3b82f6,#7c3aed);color:#fff;
  font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center}
.step-text{color:#cbd5e1;font-size:14px;padding-top:4px}

/* Section header */
.shdr{font-size:1.2rem;font-weight:700;color:#93c5fd;
      border-left:3px solid #3b82f6;padding-left:12px;margin:20px 0 14px}

/* NLP token chips */
.token{display:inline-block;background:rgba(99,102,241,.15);color:#a5b4fc;
       border:1px solid rgba(99,102,241,.25);border-radius:8px;
       padding:3px 10px;font-size:12px;margin:2px;font-family:monospace}

/* OTP */
.otp-wrap{background:rgba(59,130,246,.08);border:2px solid rgba(59,130,246,.3);
          border-radius:16px;padding:28px;text-align:center}
.otp-code{font-size:3rem;font-weight:900;letter-spacing:16px;color:#60a5fa;
          font-family:monospace;text-shadow:0 0 30px rgba(96,165,250,.5)}

/* Sidebar nav buttons */
div.stButton>button{
  background:rgba(255,255,255,.04)!important;color:#94a3b8!important;
  border:1px solid rgba(255,255,255,.07)!important;border-radius:10px!important;
  font-weight:500!important;transition:all .2s!important;text-align:left!important}
div.stButton>button:hover{
  background:rgba(59,130,246,.12)!important;color:#93c5fd!important;
  border-color:rgba(59,130,246,.3)!important}

/* Primary action buttons */
.stButton.primary>button, div[data-testid="stFormSubmitButton"]>button{
  background:linear-gradient(135deg,#3b82f6,#6366f1)!important;
  color:#fff!important;border:none!important;font-weight:600!important}

/* Inputs */
.stSelectbox>div>div,.stTextArea>div>div,.stTextInput>div>div{
  background:rgba(255,255,255,.04)!important;border-color:rgba(255,255,255,.1)!important;
  border-radius:10px!important;color:#e2e8f0!important}
label{color:#64748b!important;font-size:.85rem!important;font-weight:500!important}
div[data-testid="stExpander"]{background:rgba(255,255,255,.02)!important;
  border:1px solid rgba(255,255,255,.07)!important;border-radius:14px!important}

/* Table */
.stDataFrame{border-radius:12px!important;overflow:hidden!important}

/* Divider */
hr{border-color:rgba(255,255,255,.06)!important}

/* Stat highlight */
.stat-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.stat-chip{background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);
           border-radius:10px;padding:8px 16px;font-size:13px;color:#a5b4fc}
.stat-chip b{color:#fff}
</style>""", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────────────────────
_DEF = {
    "logged_in":False,"username":"","user_email":"","page":"home",
    "recommendations":[],"last_inputs":{},
    "chat_history":[],
    "auth_tab":"login","registered_users":{},
    "pending_otp":"","pending_email":"","otp_at":0.0,
    "openai_key":os.environ.get("OPENAI_API_KEY",""),
    "smtp_email":os.environ.get("SMTP_EMAIL",""),
    "smtp_password":os.environ.get("SMTP_PASSWORD",""),
    "nlp_result":None,"nlp_input":"",
}
for k,v in _DEF.items():
    if k not in st.session_state: st.session_state[k]=v
st.session_state.openai_key   = st.session_state.openai_key   or os.environ.get("OPENAI_API_KEY","")
st.session_state.smtp_email   = st.session_state.smtp_email   or os.environ.get("SMTP_EMAIL","")
st.session_state.smtp_password= st.session_state.smtp_password or os.environ.get("SMTP_PASSWORD","")

# ── Resource cache ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🧠 Loading AI models…")
def _load():
    m = load_embed_model()
    e = build_embeddings(m)
    return m, e

embed_model, embeddings = _load()

# ── Knowledge base ────────────────────────────────────────────────────────────
FULL_KB = [
    (("software","coding","programming","developer","web","frontend","backend"),
"""💻 **Software Engineering**

• **Education:** B.Tech CSE / BCA / B.Sc CS
• **Entrance:** JEE Main / BITSAT / State CETs
• **Key Skills:** Python, Java/C++, DSA, SQL, Git
• **Salary:** ₹6–25 LPA (top: ₹15–40 LPA)
• **Top Companies:** Google, Microsoft, Amazon, TCS, Infosys

**Roadmap:** Python → DSA (LeetCode) → Projects → Internships → Placements

**Top Colleges:** IITs, NITs, BITS Pilani, VIT, Manipal"""),

    (("neet","doctor","medical","mbbs","bds","dentist"),
"""🏥 **Medical Career (NEET)**

• **Entrance:** NEET-UG (MBBS/BDS/BAMS)
• **Duration:** MBBS = 5.5 years + specialisation 3 years
• **Salary:** ₹10–50 LPA (specialists earn more)
• **Top Colleges:** AIIMS Delhi, CMC Vellore, KMC Manipal

**Preparation:** NCERT PCB → HC Verma → Mock tests → Target 650+/720
**Specialisations:** Cardiology, Neurology, Dermatology, Surgery"""),

    (("data","data science","analyst","analytics","sql","tableau","power bi"),
"""📊 **Data Science / Analytics**

• **Education:** B.Tech CS / B.Sc Statistics
• **Key Skills:** Python, SQL, ML, Statistics, Power BI/Tableau
• **Salary:** ₹4–30 LPA
• **Top Recruiters:** Amazon, Flipkart, KPMG, Deloitte

**Roadmap:** Python → SQL → Stats → ML → Projects → Kaggle"""),

    (("ai","machine learning","ml","deep learning","neural","llm","nlp","artificial intelligence"),
"""🤖 **AI / Machine Learning**

• **Education:** B.Tech CS/AI / M.Tech / M.S. Abroad
• **Key Skills:** Python, PyTorch/TF, Linear Algebra, MLOps
• **Salary:** ₹12–50 LPA

**Roadmap:** Python → Maths → ML Fundamentals → DL (PyTorch) → Research

**Certifications:** DeepLearning.AI, fast.ai, Hugging Face"""),

    (("ca","chartered accountant","cma","icai","accountant","accounting","audit"),
"""📈 **Chartered Accountant (CA)**

• **Path:** Foundation → Intermediate → Final (ICAI)
• **Duration:** 4–5 years + 3-year articleship
• **Salary:** Big 4 fresher: ₹8–15 LPA | Experienced: ₹20–40 LPA
• **Pass Rate:** Final ~10–15%

**Roadmap:** Register ICAI → Foundation (4 papers) → Intermediate → Articleship → Final → Big 4"""),

    (("mba","management","cat","iim","xlri","pgdm"),
"""🎓 **MBA Career**

• **Entrance:** CAT / XAT / GMAT / NMAT
• **Top Institutes:** IIM A/B/C/L/K, XLRI, ISB, FMS Delhi
• **Salary:** IIM grads ₹20–40 LPA

**CAT Prep (6 months):** Quant + VARC + DILR
**Specialisations:** Finance, Marketing, HR, Consulting, Operations"""),

    (("jee","iit","nit","engineering","btech","b.tech"),
"""⚙️ **JEE / Engineering**

• **JEE Main:** NITs/IIITs | **JEE Advanced:** IITs
• **State CETs:** MHT-CET, KCET, WBJEE
• **Target:** 150+ (NIT), 250+ (top IIT branch)

**Books:** HC Verma (Physics), MS Chauhan (Chem), RD Sharma (Maths)
**Top Branches 2024:** CS at all IITs, EE IIT Bombay"""),

    (("upsc","ias","ips","civil service","government","ssc","railways"),
"""🏛️ **UPSC / Government Services**

• **UPSC CSE:** Prelims → Mains → Interview (PT)
• **Age Limit:** 21–32 years (General) + relaxations
• **Salary:** ₹56,100–₹2,50,000/month + perks

**Books:** Laxmikant (Polity), Spectrum (History), Shankar IAS (Environment)
**Daily:** The Hindu/Indian Express + test series after 8–10 months"""),

    (("law","llb","clat","lawyer","advocate","legal"),
"""⚖️ **Law Career**

• **Entrance:** CLAT (NLUs) | AILET (NLU Delhi) | LSAT India
• **Duration:** BA LLB = 5 years | LLB = 3 years (after graduation)
• **Salary:** ₹3–6 LPA (fresher) → ₹15–40 LPA (corporate) → ₹1 Cr+ (top litigator)

**Top Colleges:** NLSIU Bangalore, NLU Delhi, NALSAR Hyderabad
**Specialisations:** Corporate, Criminal, IP, Constitutional, International"""),

    (("design","ux","ui","graphic","nid","nift","fashion","animation"),
"""🎨 **Design Career**

• **Entrance:** NID DAT | NIFT | UCEED (IITs)
• **Courses:** B.Des, BFA, Diploma
• **Salary:** Junior: ₹3–6 LPA | Senior UX: ₹12–25 LPA

**Skills:** Figma, Adobe XD, Photoshop, Illustrator, After Effects
**Portfolio:** Behance, Dribbble | **Top Recruiters:** Zomato, CRED, Razorpay"""),

    (("pharmacy","pharma","bpharma","drug"),
"""💊 **Pharmacy Career**

• **Courses:** D.Pharm / B.Pharm / M.Pharm / Pharm.D
• **Entrance:** GPAT (for M.Pharm/govt) | State pharmacy CETs
• **Salary:** Hospital: ₹3–7 LPA | Industry R&D: ₹8–20 LPA

**Top Recruiters:** Sun Pharma, Cipla, Dr. Reddy's, Lupin, Pfizer India"""),

    (("army","defence","nda","cds","airforce","navy","military"),
"""🪖 **Defence Career**

• **NDA:** After Class 12 — 3 years at NDA Khadakwasla
• **CDS:** After graduation — UPSC exam
• **Salary:** Lieutenant ₹56,100/month + house, medical, canteen, pension

**Preparation:** UPSC NDA & NA Exam + SSB (5-day personality test)"""),

    (("psychology","counselling","mental health","therapist","clinical"),
"""🧠 **Psychology Career**

• **Courses:** BA/BSc → MA/MSc Clinical Psychology → PhD/MPhil
• **Licence:** RCI registration required for clinical practice
• **Salary:** Counsellor: ₹3–6 LPA | Clinical: ₹6–18 LPA

**Growing Demand:** Corporate wellness, mental health startups, school counselling"""),

    (("bcom","commerce","finance","banking","ibps","stock","invest"),
"""💰 **Commerce / Finance**

• **B.Com Specialisations:** Accounting, Finance, Banking, IB
• **Career Tracks:** CA | Banking (IBPS PO/SBI PO) | Stock Market (CFA) | MBA Finance
• **Salary:** Bank PO: ₹8–12 LPA | CA in Big 4: ₹12–20 LPA | Investment Banker: ₹20–50 LPA"""),

    (("class 12","12th","stream","pcm","pcb","arts stream","humanities"),
"""📚 **Choosing Your Stream After Class 10**

• **PCM (Science Non-Medical):** Engineering, CS, Architecture, Merchant Navy
• **PCB (Science Medical):** Doctor, Dentist, Nurse, Pharmacist, Biotechnology
• **Commerce:** CA, MBA, Banking, Finance, Economics
• **Arts/Humanities:** UPSC, Law, Journalism, Psychology, Teaching, Design

**Tip:** Choose based on what you genuinely enjoy studying — not peer/parent pressure!
**Common Mistake:** Taking Science just for prestige → struggles in JEE/NEET later."""),
]

def get_kb_response(question: str) -> str:
    q = question.lower()
    best_score, best = 0, ""
    for keywords, response in FULL_KB:
        score = sum(1 for kw in keywords if kw in q)
        if score > best_score:
            best_score, best = score, response
    return best if best_score > 0 else """🎯 **Career Guidance Tips**

• Identify what you enjoy doing for hours without getting bored
• Research salary benchmarks, job market, and required qualifications
• Build a portfolio: projects, internships, certifications
• Network early — LinkedIn, college fests, hackathons

**Ask me about:** JEE / NEET / CLAT / CAT / UPSC / specific careers / salary info 🚀"""

# ── OTP / SMTP ────────────────────────────────────────────────────────────────
def _send_otp(email, otp, name):
    se, sp = st.session_state.smtp_email, st.session_state.smtp_password
    if se and sp:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "🔐 Your CareerGuidanceAI OTP"
            msg["From"] = f"CareerGuidanceAI <{se}>"
            msg["To"]   = email
            html = f"""<div style="font-family:Arial;max-width:480px;margin:auto;background:#0f172a;
color:#e2e8f0;border-radius:16px;overflow:hidden">
<div style="background:linear-gradient(135deg,#3b82f6,#7c3aed);padding:28px;text-align:center">
<h1 style="margin:0;color:white;font-size:22px">🎯 CareerGuidanceAI</h1></div>
<div style="padding:32px"><p>Hello <b>{name}</b>,</p>
<div style="background:#1e293b;border:2px solid #3b82f6;border-radius:12px;padding:24px;text-align:center">
<span style="font-size:40px;font-weight:900;letter-spacing:14px;color:#60a5fa">{otp}</span></div>
<p style="color:#64748b;font-size:13px">Expires in 10 minutes.</p></div></div>"""
            msg.attach(MIMEText(html, "html"))
            s = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
            s.ehlo(); s.starttls(); s.ehlo(); s.login(se, sp)
            s.sendmail(se, email, msg.as_string()); s.quit()
            st.success(f"📧 OTP sent to **{email}**!")
            return
        except Exception as ex:
            st.warning(f"Email failed ({ex}). Dev mode OTP shown below.")
    st.markdown(f'<div class="otp-wrap"><p style="color:#94a3b8;margin:0 0 8px">📬 Dev Mode OTP</p>'
                f'<div class="otp-code">{otp}</div>'
                f'<p style="color:#64748b;font-size:12px;margin:8px 0 0">Configure SMTP in Settings for real emails</p></div>',
                unsafe_allow_html=True)

def _gen_otp():
    otp = "".join(random.choices(string.digits, k=6))
    st.session_state.pending_otp = otp
    st.session_state.otp_at = time.time()
    return otp

def _ask_openai(messages, system, key):
    try:
        payload = _json.dumps({"model":"gpt-4o-mini","max_tokens":800,"temperature":0.7,
            "messages":[{"role":"system","content":system}]+messages}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
            data=payload, headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"},
            method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            return _json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception:
        return None

# ── Sidebar ───────────────────────────────────────────────────────────────────
def _sidebar():
    with st.sidebar:
        st.markdown("""<div style="padding:24px 0 16px;text-align:center">
<div style="background:linear-gradient(135deg,#3b82f6,#7c3aed);width:52px;height:52px;
border-radius:14px;display:inline-flex;align-items:center;justify-content:center;
font-size:1.6rem;margin-bottom:10px">🎯</div>
<h2 style="margin:0;color:#fff;font-size:1.1rem;font-weight:700">CareerGuidanceAI</h2>
<p style="color:#475569;font-size:.75rem;margin:4px 0 0">v2.0 — AI Powered</p></div>""",
            unsafe_allow_html=True)

        if st.session_state.logged_in:
            has_ai   = bool(st.session_state.openai_key)
            has_smtp = bool(st.session_state.smtp_email)
            status   = "🟢 Full AI" if has_ai else ("🟡 Offline Mode" if not has_smtp else "🟡 SMTP only")
            st.markdown(f"""<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
border-radius:12px;padding:12px 14px;margin-bottom:12px">
<div style="color:#fff;font-weight:600;font-size:.9rem">👤 {st.session_state.username}</div>
<div style="color:#64748b;font-size:.75rem">{st.session_state.user_email}</div>
<div style="color:#94a3b8;font-size:.72rem;margin-top:6px">{status}</div></div>""",
                unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)
        nav = [
            ("🏠","Home","home"),
            ("🎯","Career Guidance","guidance"),
            ("🔬","NLP Analysis","nlp"),
            ("💬","AI Chat","chat"),
            ("📄","Resume Builder","resume"),
            ("🔖","Bookmarks","bookmarks"),
            ("📊","Analytics","analytics"),
            ("🤖","ML Insights","ml_insights"),
            ("⚙️","Settings","settings"),
        ]
        for icon, label, key in nav:
            active = st.session_state.page == key
            style = ("background:linear-gradient(135deg,rgba(59,130,246,.2),rgba(99,102,241,.15))!important;"
                     "color:#93c5fd!important;border-color:rgba(59,130,246,.3)!important") if active else ""
            if st.button(f"  {icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key; st.rerun()

        st.markdown("<div style='margin-top:auto'></div>", unsafe_allow_html=True)
        st.divider()
        if st.session_state.logged_in:
            if st.button("🚪  Logout", use_container_width=True):
                for k in list(st.session_state.keys()): del st.session_state[k]
                for k,v in _DEF.items(): st.session_state[k]=v
                st.rerun()

# ── Login ─────────────────────────────────────────────────────────────────────
def page_login():
    st.markdown("""<div class="hero">
<div class="hero-badge">✨ Final Year Project — B.Tech Computer Science</div>
<h1>🎯 CareerGuidanceAI</h1>
<p>AI-Powered Career Guidance System for Indian Students<br>
<span style="font-size:.9rem;color:#64748b">NLP • Machine Learning • SQLite • REST API • Streamlit</span></p></div>""",
        unsafe_allow_html=True)

    _, col, _ = st.columns([1,1.3,1])
    with col:
        tab = st.session_state.auth_tab
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔑  Login",    use_container_width=True, key="sw_li"): st.session_state.auth_tab="login";    st.rerun()
        with c2:
            if st.button("📝  Register", use_container_width=True, key="sw_rg"): st.session_state.auth_tab="register"; st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if tab == "login":
            with st.container():
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("#### 👋 Welcome Back")
                email = st.text_input("Email", placeholder="you@example.com", key="li_e")
                pwd   = st.text_input("Password", type="password",            key="li_p")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Login →", use_container_width=True, key="do_li"):
                        if email=="demo@career.ai" and pwd=="career123":
                            st.session_state.update(logged_in=True,username="Demo User",user_email=email,page="home"); st.rerun()
                        else:
                            ok, name = verify_login(email, pwd)
                            if ok:
                                st.session_state.update(logged_in=True,username=name,user_email=email,page="home"); st.rerun()
                            else:
                                st.error("Invalid email or password.")
                with c2:
                    if st.button("🔐 OTP Login", use_container_width=True, key="req_otp"):
                        if not email: st.error("Enter email first.")
                        else:
                            st.session_state.pending_email = email
                            otp = _gen_otp()
                            name = st.session_state.registered_users.get(email,{}).get("name","User")
                            _send_otp(email, otp, name)
                            st.session_state.auth_tab="otp"; st.rerun()
                st.caption("Demo: `demo@career.ai` / `career123`")
                st.markdown('</div>', unsafe_allow_html=True)

        elif tab == "register":
            with st.container():
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.markdown("#### 🚀 Create Account")
                name  = st.text_input("Full Name",              key="rg_n")
                email = st.text_input("Email",                  key="rg_e")
                pwd   = st.text_input("Password (min 6 chars)", type="password", key="rg_p")
                if st.button("Register & Get OTP →", use_container_width=True, key="do_rg"):
                    if not all([name.strip(),email.strip(),pwd.strip()]): st.error("Fill all fields.")
                    elif "@" not in email: st.error("Valid email required.")
                    elif len(pwd) < 6: st.error("Password min 6 chars.")
                    else:
                        ok, msg = register_user(name.strip(), email.strip(), pwd)
                        if ok or msg=="email_exists":
                            st.session_state.registered_users[email]={"name":name.strip(),"password":pwd}
                            st.session_state.pending_email = email
                            otp = _gen_otp()
                            _send_otp(email, otp, name.strip())
                            st.session_state.auth_tab="otp"; st.rerun()
                        else: st.error("Registration failed.")
                st.markdown('</div>', unsafe_allow_html=True)

        elif tab == "otp":
            email   = st.session_state.pending_email
            elapsed = int(time.time()-st.session_state.otp_at)
            rem     = max(0, 600-elapsed)
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.markdown(f"#### 🔐 Verify OTP")
            st.caption(f"Sent to **{email}** — expires in {rem//60}m {rem%60}s")
            entered = st.text_input("Enter 6-digit OTP", max_chars=6, key="otp_f")
            c1,c2,c3 = st.columns(3)
            with c1:
                if st.button("✓ Verify", use_container_width=True, key="do_v"):
                    if rem==0: st.error("OTP expired. Resend.")
                    elif entered.strip()==st.session_state.pending_otp:
                        name = st.session_state.registered_users.get(email,{}).get("name",email.split("@")[0].title())
                        st.session_state.update(logged_in=True,username=name,user_email=email,page="home"); st.rerun()
                    else: st.error("Incorrect OTP.")
            with c2:
                if st.button("🔄 Resend", use_container_width=True, key="re_otp"):
                    otp=_gen_otp(); _send_otp(email,otp,st.session_state.registered_users.get(email,{}).get("name","User")); st.rerun()
            with c3:
                if st.button("← Back", use_container_width=True, key="bk_otp"):
                    st.session_state.auth_tab="login"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ── Home ──────────────────────────────────────────────────────────────────────
def page_home():
    name = st.session_state.username
    st.markdown(f"""<div class="hero">
<div class="hero-badge">✨ AI-Powered Career Guidance</div>
<h1>Welcome back, {name}! 👋</h1>
<p>Your personalised career guidance dashboard powered by NLP, ML, and SQLite</p></div>""",
        unsafe_allow_html=True)

    # Live DB metrics
    total_u = get_user_count()
    total_s = get_session_count()
    avg_r   = get_avg_rating()
    total_f = get_feedback_count()

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(ico,lbl,val) in zip([c1,c2,c3,c4,c5],[
        ("🎯","Careers","87+"),("👥","Users",str(total_u) if total_u else "Demo"),
        ("📊","Sessions",str(total_s) if total_s else "Demo"),
        ("⭐","Avg Rating",f"{avg_r}/5" if avg_r else "N/A"),
        ("🧠","AI Engine","TF-IDF+NLP"),
    ]):
        col.markdown(f'<div class="metric"><div class="ico">{ico}</div>'
                     f'<div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                     unsafe_allow_html=True)

    st.markdown('<div class="shdr">🚀 Quick Actions</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    cards = [
        ("glass-blue","🎯","Career Guidance","AI-powered recommendations based on your profile","Start →","guidance"),
        ("glass-purple","🔬","NLP Analysis","Analyse your text with our visible NLP pipeline","Analyse →","nlp"),
        ("glass-green","💬","AI Chat","Expert career counsellor — works offline too","Chat →","chat"),
        ("glass-orange","📄","Resume Builder","Generate a professional PDF résumé in one click","Build →","resume"),
    ]
    for col,(cls,ico,title,desc,btn,target) in zip([c1,c2,c3,c4],cards):
        with col:
            st.markdown(f'<div class="{cls} glass"><div style="font-size:1.8rem;margin-bottom:8px">{ico}</div>'
                        f'<h4 style="color:#fff;margin:0 0 6px;font-size:.95rem">{title}</h4>'
                        f'<p style="color:#64748b;font-size:.82rem;margin:0 0 12px">{desc}</p></div>',
                        unsafe_allow_html=True)
            if st.button(btn, key=f"hc_{target}", use_container_width=True):
                st.session_state.page=target; st.rerun()

    if st.session_state.recommendations:
        st.markdown('<div class="shdr">📌 Your Last Results</div>', unsafe_allow_html=True)
        recs = st.session_state.recommendations[:4]
        cols = st.columns(len(recs))
        for col,(career,score) in zip(cols,recs):
            pct = min(99, int(score*100))
            col.markdown(f'<div class="glass" style="text-align:center">'
                         f'<div style="font-size:1.6rem;font-weight:800;color:#60a5fa">{pct}%</div>'
                         f'<div style="color:#fff;font-weight:600;font-size:.9rem;margin:4px 0">{career}</div>'
                         f'<div class="bar-wrap"><div class="bar" style="width:{pct}%"></div></div></div>',
                         unsafe_allow_html=True)

    # Top careers from DB
    top_db = get_top_careers_overall(5)
    if top_db:
        st.markdown('<div class="shdr">🔥 Most Chosen Careers (All Users)</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-row">'+''.join(f'<div class="stat-chip"><b>{c}</b> — {n} sessions</div>'
            for c,n in top_db)+'</div>', unsafe_allow_html=True)

# ── Guidance ──────────────────────────────────────────────────────────────────
def page_guidance():
    st.markdown('<div class="shdr">🎯 AI Career Guidance</div>', unsafe_allow_html=True)
    st.caption("Fill in your profile. The more detail you give, the better the AI matching.")

    col1,col2 = st.columns(2)
    with col1:
        stream = st.selectbox("📘 Educational Stream", CAREER_MAPPINGS["streams"], key="g_stream")
        science_focus = None
        if stream=="Science":
            sf = st.selectbox("🧬 Science Focus",
                ["— Select —","Medical (Biology)","Non-Medical (Maths)"], key="g_sf")
            if sf=="Medical (Biology)":    science_focus="Medical"
            elif sf=="Non-Medical (Maths)": science_focus="Non-Medical"
        fields = CAREER_MAPPINGS["fields"].get(stream,[])
        fc = st.selectbox("🎯 Career Field", ["— Select —"]+fields, key="g_field")
        field = "" if fc=="— Select —" else fc
        roles = CAREER_MAPPINGS["roles"].get(field,[]) if field else []
        if roles:
            rc = st.selectbox("🧠 Preferred Role", ["— Select —"]+roles, key="g_role")
            role = "" if rc=="— Select —" else rc
        else:
            st.selectbox("🧠 Preferred Role",["← Select a Field first"], key="g_re", disabled=True); role=""
    with col2:
        hobby     = st.selectbox("🎮 Primary Interest", HOBBY_OPTIONS,     key="g_hobby")
        free_time = st.selectbox("⏳ Free Time",         FREE_TIME_OPTIONS, key="g_ft")
        subject   = st.selectbox("📚 Favourite Subject", SUBJECT_OPTIONS,   key="g_subj")

    aspiration = st.text_area("💭 Describe your aspirations",
        placeholder="I enjoy solving complex problems, love maths and programming…",
        height=90, key="g_asp")

    if st.button("🚀  Get My Career Recommendations", use_container_width=True, key="g_go"):
        parts = [f"Stream: {stream}", f"Field: {field}" if field else "",
                 f"Role: {role}" if role else "",
                 f"Interest: {hobby}", f"Free time: {free_time}",
                 f"Subject: {subject}", aspiration.strip()]
        if science_focus: parts.append(f"Focus: {science_focus}")
        user_text = " ".join(filter(None,parts))

        with st.spinner("🧠 Matching your profile with AI…"):
            recs = get_recommendations(embed_model, embeddings, user_text=user_text,
                stream=stream, field=field, role=role, science_focus=science_focus)

        st.session_state.recommendations = recs
        inp = {"stream":stream,"field":field,"role":role,"hobby":hobby,
               "subject":subject,"aspiration":aspiration}
        st.session_state.last_inputs = inp

        # Save to SQLite
        if st.session_state.user_email:
            save_session(st.session_state.user_email, inp, recs)

        # Auto-run NLP
        st.session_state.nlp_input  = user_text
        st.session_state.nlp_result = full_pipeline(user_text)
        st.success(f"✅ Found {len(recs)} personalised matches!  💡 NLP Analysis also updated — check the NLP tab!")

    recs = st.session_state.recommendations
    if not recs: return

    st.markdown('<div class="shdr">📊 Your Career Matches</div>', unsafe_allow_html=True)

    for rank,(career,score) in enumerate(recs,1):
        d   = ENHANCED_CAREER_DETAILS.get(career,{})
        pct = min(99,int(score*100)) if score<1 else int(score*100)
        medal = {1:"🥇",2:"🥈",3:"🥉"}.get(rank,f"#{rank}")
        bookmarked = is_bookmarked(st.session_state.user_email, career) if st.session_state.user_email else False
        bm_ico = "🔖" if bookmarked else "➕"

        with st.expander(f"{medal}  {career}  —  {pct}% Match", expanded=(rank==1)):
            hc1,hc2 = st.columns([5,1])
            with hc1:
                st.markdown(f'<div class="bar-wrap"><div class="bar" style="width:{pct}%"></div></div>'
                            f'<p style="color:#94a3b8;font-size:.9rem;margin-bottom:12px">{d.get("description","")}</p>',
                            unsafe_allow_html=True)
            with hc2:
                if st.button(f"{bm_ico} Bookmark", key=f"bm_{rank}"):
                    if st.session_state.user_email:
                        if bookmarked: remove_bookmark(st.session_state.user_email, career)
                        else:          add_bookmark(st.session_state.user_email, career)
                        log_career_view(career, st.session_state.user_email)
                        st.rerun()

            t1,t2,t3 = st.tabs(["📋 Overview","🗺 Roadmap","⚖️ Pros & Cons"])
            with t1:
                a,b = st.columns(2)
                with a:
                    st.markdown("**🎓 Education**")
                    for e in d.get("education",[]): st.markdown(f"- {e}")
                    st.markdown(f"**💰 Salary**  \n{d.get('salary','N/A')}")
                with b:
                    st.markdown("**🛠 Key Skills**")
                    st.markdown(" ".join(f'<span class="pill pill-blue">{s}</span>' for s in d.get("skills",[])[:6]), unsafe_allow_html=True)
                    st.markdown(f"**📈 Market**  \n{d.get('market','N/A')}")
            with t2:
                for i,step in enumerate(d.get("roadmap",[]),1):
                    st.markdown(f'<div class="step"><div class="step-num">{i}</div><div class="step-text">{step}</div></div>', unsafe_allow_html=True)
            with t3:
                p,c = st.columns(2)
                with p:
                    st.markdown("**✅ Pros**")
                    for x in d.get("pros",[]): st.markdown(f'<span class="pill pill-green">✓ {x}</span>', unsafe_allow_html=True)
                with c:
                    st.markdown("**⚠️ Cons**")
                    for x in d.get("cons",[]): st.markdown(f'<span class="pill pill-red">✗ {x}</span>', unsafe_allow_html=True)

    st.markdown("---")
    a1,a2,a3 = st.columns(3)
    with a1:
        if st.button("🔬 View NLP Analysis",use_container_width=True):  st.session_state.page="nlp";      st.rerun()
    with a2:
        if st.button("💬 Discuss in Chat", use_container_width=True):
            st.session_state.chat_history.append({"role":"user","content":f"Tell me about career as {recs[0][0]}"})
            st.session_state.page="chat"; st.rerun()
    with a3:
        if st.button("📄 Build Resume",     use_container_width=True):  st.session_state.page="resume";   st.rerun()

# ── NLP Analysis ──────────────────────────────────────────────────────────────
def page_nlp():
    import plotly.graph_objects as go
    st.markdown('<div class="shdr">🔬 NLP Analysis Pipeline</div>', unsafe_allow_html=True)
    st.caption("Visible NLP pipeline — tokenization, keyword extraction, TF-IDF scoring, entity tagging, sentiment, and intent classification.")

    default_text = st.session_state.nlp_input or \
        "I love coding Python and machine learning. I enjoy solving complex algorithms and want to work in AI or data science."
    text = st.text_area("Enter text to analyse", value=default_text, height=100, key="nlp_txt")

    if st.button("🔬  Run NLP Pipeline", use_container_width=True, key="nlp_go"):
        with st.spinner("Running NLP pipeline…"):
            result = full_pipeline(text)
        st.session_state.nlp_result = result
        st.session_state.nlp_input  = text

    res = st.session_state.nlp_result
    if not res or "error" in res: return

    st.markdown("---")

    # ── Step 1: Cleaned text ──────────────────────────────────────────────────
    st.markdown('<div class="shdr">Step 1 — Text Cleaning & Tokenization</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Raw Tokens",    res["token_count_raw"])
    c2.metric("Clean Tokens",  res["token_count_clean"])
    c3.metric("Removed",       res["token_count_raw"]-res["token_count_clean"])
    c4.metric("Vocab Density", f"{res['token_count_clean']/max(res['token_count_raw'],1)*100:.0f}%")

    st.markdown("**📝 Cleaned Text:**")
    st.code(res["cleaned_text"], language=None)

    st.markdown("**🔤 Tokens after stopword removal:**")
    st.markdown(" ".join(f'<span class="token">{t}</span>' for t in res["tokens"]), unsafe_allow_html=True)

    st.markdown("**🌱 Stemmed Tokens:**")
    st.markdown(" ".join(f'<span class="token" style="color:#c4b5fd">{t}</span>' for t in res["stemmed_tokens"]), unsafe_allow_html=True)

    st.markdown("---")

    # ── Step 2: Keywords ──────────────────────────────────────────────────────
    st.markdown('<div class="shdr">Step 2 — Keyword Extraction (TF × IDF)</div>', unsafe_allow_html=True)
    kws = res["keywords"]
    if kws:
        words  = [k for k,_ in kws]
        scores = [s for _,s in kws]
        fig = go.Figure(go.Bar(
            x=scores, y=words, orientation="h",
            marker=dict(color=scores, colorscale=[[0,"#1e3a8a"],[1,"#7c3aed"]], showscale=False),
            text=[f"{s:.4f}" for s in scores], textposition="outside",
        ))
        fig.update_layout(paper_bgcolor="#060b18",plot_bgcolor="#0d1526",
            font=dict(color="#e2e8f0"),height=280,margin=dict(t=10,b=10,l=10,r=60),
            xaxis=dict(gridcolor="#1e293b"),yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Step 3: Named entities ─────────────────────────────────────────────────
    st.markdown('<div class="shdr">Step 3 — Named Entity Recognition (NER)</div>', unsafe_allow_html=True)
    entities = res["entities"]
    if entities:
        for label, tokens in entities.items():
            color = ENTITY_COLOR.get(label, "#64748b")
            chips = " ".join(f'<span class="pill" style="background:rgba(0,0,0,.3);color:{color};'
                             f'border-color:{color}">{t.upper()}</span>' for t in tokens)
            st.markdown(f'<div style="margin:6px 0"><span style="color:#64748b;font-size:.8rem;'
                        f'font-weight:600;text-transform:uppercase;letter-spacing:.5px">{label}</span>'
                        f'&nbsp;&nbsp;{chips}</div>', unsafe_allow_html=True)
    else:
        st.info("No career-domain entities detected. Try including subjects, skills, or exam names.")

    st.markdown("---")

    # ── Step 4: Sentiment ─────────────────────────────────────────────────────
    st.markdown('<div class="shdr">Step 4 — Sentiment Analysis (Career Confidence)</div>', unsafe_allow_html=True)
    sent = res["sentiment"]
    sc1,sc2,sc3 = st.columns(3)
    score_pct = int(sent["score"]*100)
    sc1.metric("Confidence Score", f"{score_pct}%")
    sc2.metric("Label",            sent["label"])
    sc3.metric("Positive / Negative Words", f"{sent['positive_words']} / {sent['negative_words']}")
    st.progress(sent["score"])

    st.markdown("---")

    # ── Step 5: Intent ────────────────────────────────────────────────────────
    st.markdown('<div class="shdr">Step 5 — Career-Intent Classification</div>', unsafe_allow_html=True)
    intents = res["intent_scores"]
    labels  = [i for i,_ in intents]
    vals    = [v for _,v in intents]
    fig2 = go.Figure(go.Pie(
        labels=labels, values=vals, hole=.5,
        marker=dict(colors=["#3b82f6","#7c3aed","#059669","#dc2626","#d97706","#0284c7","#64748b"]),
        textinfo="label+percent",
    ))
    fig2.update_layout(paper_bgcolor="#060b18",font=dict(color="#e2e8f0"),
        height=320,margin=dict(t=20,b=20),showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Step 6: TF-IDF vs careers ─────────────────────────────────────────────
    st.markdown('<div class="shdr">Step 6 — TF-IDF Matching Against Career Database</div>', unsafe_allow_html=True)
    st.caption("Shows which careers your text semantically matches using TF-IDF scoring")
    career_docs = {c: d.get("description","")+" "+" ".join(d.get("skills",[]))
                   for c,d in list(ENHANCED_CAREER_DETAILS.items())[:40]}
    tfidf_res = tfidf_explain(text, career_docs, top_n=6)
    if tfidf_res:
        import pandas as pd
        df = pd.DataFrame(tfidf_res)[["career","matched_terms","tf","idf","tfidf"]]
        df.columns = ["Career","Matched Terms","TF","IDF","TF-IDF Score"]
        df["Matched Terms"] = df["Matched Terms"].apply(lambda x: ", ".join(x))
        st.dataframe(df, use_container_width=True, hide_index=True)

# ── Chat ──────────────────────────────────────────────────────────────────────
def page_chat():
    st.markdown('<div class="shdr">💬 AI Career Counsellor</div>', unsafe_allow_html=True)
    api_key = st.session_state.openai_key
    if api_key:
        st.success("⚡ Using OpenAI GPT-4o Mini", icon="✅")
    else:
        st.info("📚 Using built-in knowledge base — covers 15 career domains, works without any API key.", icon="ℹ️")

    SYSTEM = ("You are CareerGuidanceAI, an expert Indian career counsellor. "
              "Help with career decisions, JEE/NEET/CAT/UPSC/CLAT, college admissions, "
              "salary expectations, and skill development. Be concise, encouraging, "
              "specific to the Indian education system. Use bullet points and markdown.")

    def _reply(msg):
        if api_key:
            hist = [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history[:-1]]+[{"role":"user","content":msg}]
            ctx  = ""
            if st.session_state.recommendations:
                tops = [c for c,_ in st.session_state.recommendations[:3]]
                ctx  = f" Student top matches: {', '.join(tops)}."
            r = _ask_openai(hist, SYSTEM+ctx, api_key)
            if r: return r
        return get_kb_response(msg)

    if not st.session_state.chat_history:
        st.markdown("**💡 Suggested questions:**")
        prompts = [
            "How to prepare for JEE Advanced?",
            "What is the salary for a Data Scientist?",
            "How to become a CA in India?",
            "NEET preparation tips?",
            "IIT vs NIT — which is better for CS?",
            "What skills do I need for AI/ML?",
        ]
        for row in [prompts[:3], prompts[3:]]:
            cols = st.columns(3)
            for col,p in zip(cols,row):
                with col:
                    if st.button(p, key=f"cp_{p[:15]}"):
                        st.session_state.chat_history.append({"role":"user","content":p})
                        with st.spinner("Thinking…"):
                            rep = _reply(p)
                        st.session_state.chat_history.append({"role":"assistant","content":rep})
                        st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"]=="user" else "🤖"):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask anything about careers, exams, salaries…")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="🧑‍🎓"): st.markdown(user_input)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🧠 Thinking…"):
                rep = _reply(user_input)
            st.markdown(rep)
        st.session_state.chat_history.append({"role":"assistant","content":rep})

    if st.session_state.chat_history:
        if st.button("🗑 Clear Chat", key="clr_chat"):
            st.session_state.chat_history=[]; st.rerun()

# ── Resume ─────────────────────────────────────────────────────────────────────
def page_resume():
    st.markdown('<div class="shdr">📄 AI Resume Builder</div>', unsafe_allow_html=True)
    st.caption("Auto-generates a professional PDF résumé tailored to your target career.")
    career_opts = list(ENHANCED_CAREER_DETAILS.keys())
    def_idx = 0
    if st.session_state.recommendations:
        top = st.session_state.recommendations[0][0]
        if top in career_opts: def_idx = career_opts.index(top)
    with st.form("rf"):
        c1,c2 = st.columns(2)
        with c1:
            name     = st.text_input("Full Name",    value=st.session_state.username)
            email    = st.text_input("Email",         placeholder="you@example.com")
            phone    = st.text_input("Phone",         placeholder="+91 98765 43210")
            linkedin = st.text_input("LinkedIn (optional)")
        with c2:
            location = st.text_input("City / Location", placeholder="New Delhi, India")
            stream   = st.selectbox("Educational Stream", CAREER_MAPPINGS["streams"])
            target   = st.selectbox("Target Career",      career_opts, index=def_idx)
        extra = st.text_input("Additional Skills",     placeholder="Docker, Figma, Public Speaking…")
        ach   = st.text_area("Achievements",           placeholder="Google Certificate\nHackathon winner", height=80)
        gen   = st.form_submit_button("📄  Generate PDF Resume", use_container_width=True)
    if gen:
        if not name.strip(): st.error("Enter your name."); return
        d = ENHANCED_CAREER_DETAILS.get(target,{})
        with st.spinner("Generating résumé…"):
            pdf = generate_resume_pdf(name=name, email=email, phone=phone, location=location,
                stream=stream, career=target, career_details=d, extra_skills=extra, achievements=ach)
        st.success("✅ Resume ready!")
        st.download_button("⬇️  Download PDF Resume", data=pdf,
            file_name=f"{name.replace(' ','_')}_Resume.pdf", mime="application/pdf",
            use_container_width=True)

# ── Bookmarks ─────────────────────────────────────────────────────────────────
def page_bookmarks():
    st.markdown('<div class="shdr">🔖 Saved Careers</div>', unsafe_allow_html=True)
    email = st.session_state.user_email
    if not email:
        st.info("Log in with a registered account to use bookmarks.")
        return
    bms = get_bookmarks(email)
    if not bms:
        st.info("No bookmarks yet. Explore careers in the Guidance page and click ➕ Bookmark!")
        return
    for bm in bms:
        career = bm["career"]
        d = ENHANCED_CAREER_DETAILS.get(career,{})
        with st.expander(f"🔖 {career}"):
            c1,c2 = st.columns([3,1])
            with c1:
                st.markdown(f"**📝** {d.get('description','')}")
                st.markdown(f"**💰 Salary:** {d.get('salary','N/A')}")
                st.markdown(f"**📅 Saved:** {bm['created_at'][:10]}")
            with c2:
                if st.button("❌ Remove", key=f"rb_{career}"):
                    remove_bookmark(email, career); st.rerun()
                if st.button("📄 Resume", key=f"rr_{career}"):
                    st.session_state.page="resume"; st.rerun()

# ── Analytics ─────────────────────────────────────────────────────────────────
def page_analytics():
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd

    st.markdown('<div class="shdr">📊 Analytics Dashboard</div>', unsafe_allow_html=True)

    # ── Platform stats from DB ─────────────────────────────────────────────────
    st.markdown("#### 🗄️ Live Database Statistics (SQLite)")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Registered Users",  get_user_count())
    c2.metric("Guidance Sessions", get_session_count())
    c3.metric("Avg Rating",        f"{get_avg_rating()}/5 ⭐")
    c4.metric("Feedback Count",    get_feedback_count())

    col1,col2 = st.columns(2)
    with col1:
        top_db = get_top_careers_overall(8)
        if top_db:
            names,counts = zip(*top_db)
            fig = go.Figure(go.Bar(x=list(names),y=list(counts),
                marker=dict(color=list(counts),colorscale=[[0,"#1e3a8a"],[1,"#7c3aed"]],showscale=False),
                text=list(counts),textposition="outside"))
            fig.update_layout(title="Most Chosen Careers",paper_bgcolor="#060b18",plot_bgcolor="#0d1526",
                font=dict(color="#e2e8f0"),height=320,margin=dict(t=40,b=20),
                xaxis=dict(gridcolor="#1e293b"),yaxis=dict(gridcolor="#1e293b"))
            st.plotly_chart(fig,use_container_width=True)

    with col2:
        streams_db = get_stream_distribution()
        if streams_db:
            fig2 = go.Figure(go.Pie(labels=list(streams_db.keys()),values=list(streams_db.values()),hole=.45,
                marker=dict(colors=["#3b82f6","#7c3aed","#059669","#d97706"]),textinfo="label+percent"))
            fig2.update_layout(title="Stream Distribution",paper_bgcolor="#060b18",
                font=dict(color="#e2e8f0"),height=320,margin=dict(t=40,b=20),showlegend=False)
            st.plotly_chart(fig2,use_container_width=True)

    st.divider()
    st.markdown("#### 📈 India Job Market Trends")

    # ── India salary chart ─────────────────────────────────────────────────────
    salary_data = {
        "Career":  ["AI/ML Engineer","Software Engineer","Data Scientist","CA","IAS Officer",
                    "Doctor (Specialist)","MBA Graduate","UX Designer","Lawyer (Corporate)","Data Analyst"],
        "Fresher": [12,6,8,8,6,10,15,5,3,4],
        "Senior":  [50,25,30,35,25,50,45,25,40,18],
    }
    df_sal = pd.DataFrame(salary_data)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Fresher (LPA)",x=df_sal["Career"],y=df_sal["Fresher"],
        marker_color="#3b82f6",text=df_sal["Fresher"],textposition="outside"))
    fig3.add_trace(go.Bar(name="Senior (LPA)",  x=df_sal["Career"],y=df_sal["Senior"],
        marker_color="#7c3aed",text=df_sal["Senior"],textposition="outside"))
    fig3.update_layout(title="India Salary Benchmarks (₹ LPA)",barmode="group",
        paper_bgcolor="#060b18",plot_bgcolor="#0d1526",font=dict(color="#e2e8f0"),
        height=380,legend=dict(bgcolor="#0d1526",bordercolor="#334155"),
        xaxis=dict(gridcolor="#1e293b",tickangle=-30),yaxis=dict(gridcolor="#1e293b",title="₹ LPA"))
    st.plotly_chart(fig3,use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        # Growth rate chart
        growth = {"AI/ML":35,"Cloud":28,"Cybersecurity":26,"Data Science":24,"UX Design":20,
                  "DevOps":18,"Blockchain":15,"Full Stack":20}
        fig4 = go.Figure(go.Bar(
            y=list(growth.keys()),x=list(growth.values()),orientation="h",
            marker=dict(color=list(growth.values()),colorscale=[[0,"#059669"],[1,"#3b82f6"]],showscale=False),
            text=[f"{v}%" for v in growth.values()],textposition="outside"))
        fig4.update_layout(title="India Tech Job Growth Rate (%)",paper_bgcolor="#060b18",plot_bgcolor="#0d1526",
            font=dict(color="#e2e8f0"),height=320,margin=dict(t=40,b=20,r=60),
            xaxis=dict(gridcolor="#1e293b"),yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig4,use_container_width=True)

    with col4:
        # Radar for user's recs
        recs = st.session_state.recommendations
        if recs:
            _RADAR = {
                "Software Engineer":[9,9,9,7,6],"Data Scientist":[9,8,9,7,6],
                "Doctor":[8,9,6,4,5],"AI Engineer":[10,8,10,6,7],
                "IAS Officer":[6,10,5,8,5],"Entrepreneur / Startup Founder":[8,6,10,4,10],
                "Chartered Accountant (CA)":[8,9,6,7,5],"Lawyer / Advocate":[8,7,6,5,6],
            }
            cats = ["Salary","Job Security","Growth","Work-Life","Creativity"]
            fig5 = go.Figure()
            for c,s in recs[:3]:
                v = _RADAR.get(c,[6,7,7,7,6])
                fig5.add_trace(go.Scatterpolar(r=v+[v[0]],theta=cats+[cats[0]],
                    fill="toself",name=c,opacity=0.7))
            fig5.update_layout(polar=dict(bgcolor="#0d1526",
                radialaxis=dict(visible=True,range=[0,10],gridcolor="#1e293b",color="#64748b"),
                angularaxis=dict(gridcolor="#1e293b",color="#94a3b8")),
                paper_bgcolor="#060b18",font=dict(color="#e2e8f0"),
                title="Career Attribute Radar",height=320,
                legend=dict(bgcolor="#0d1526",bordercolor="#1e293b"))
            st.plotly_chart(fig5,use_container_width=True)
        else:
            st.info("Run Guidance first to see your career radar chart.")

    # Most viewed careers
    viewed = get_most_viewed(6)
    if viewed:
        st.markdown("#### 👀 Most Viewed Careers")
        v_careers, v_counts = zip(*viewed)
        fig6 = go.Figure(go.Bar(x=list(v_careers),y=list(v_counts),
            marker_color="#059669",text=list(v_counts),textposition="outside"))
        fig6.update_layout(paper_bgcolor="#060b18",plot_bgcolor="#0d1526",
            font=dict(color="#e2e8f0"),height=280,margin=dict(t=20,b=20),
            xaxis=dict(gridcolor="#1e293b"),yaxis=dict(gridcolor="#1e293b"))
        st.plotly_chart(fig6,use_container_width=True)

    # Feedback section
    st.divider()
    st.markdown("#### ⭐ Leave Feedback")
    with st.form("fb_form"):
        fc1,fc2 = st.columns(2)
        with fc1:
            rating  = st.slider("Rating",1,5,5)
            feature = st.selectbox("Feature",["Overall","Career Guidance","NLP Analysis","Resume Builder","AI Chat"])
        with fc2:
            comment = st.text_area("Comment (optional)", height=80)
        if st.form_submit_button("Submit Feedback", use_container_width=True):
            save_feedback(st.session_state.user_email or "anonymous", rating, comment, feature)
            st.success(f"✅ Thank you for the {rating}⭐ rating!")

# ── Settings ──────────────────────────────────────────────────────────────────
def page_settings():
    st.markdown('<div class="shdr">⚙️ Settings</div>', unsafe_allow_html=True)

    st.markdown("### 🤖 OpenAI API Key")
    st.caption("Optional — adds GPT-4o Mini to AI Chat. Without it, the built-in KB works fine.")
    openai_k = st.text_input("OpenAI Key", value=st.session_state.openai_key, type="password", placeholder="sk-proj-…", key="s_oa")

    st.markdown("### 📧 Gmail SMTP  *(Real OTP Emails)*")
    st.caption("Use a Gmail App Password (not your regular password). Enable 2FA → myaccount.google.com/apppasswords → Generate.")
    sc1,sc2 = st.columns(2)
    with sc1: smtp_e = st.text_input("Gmail Address", value=st.session_state.smtp_email, key="s_se")
    with sc2: smtp_p = st.text_input("App Password", value=st.session_state.smtp_password, type="password", key="s_sp")

    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("💾 Save All", use_container_width=True):
            st.session_state.openai_key=openai_k.strip()
            st.session_state.smtp_email=smtp_e.strip()
            st.session_state.smtp_password=smtp_p.strip()
            os.environ["OPENAI_API_KEY"]=openai_k.strip()
            os.environ["SMTP_EMAIL"]=smtp_e.strip()
            os.environ["SMTP_PASSWORD"]=smtp_p.strip()
            _save_keys(openai_k.strip(),smtp_e.strip(),smtp_p.strip())
            st.success("✅ Saved to disk — persists after restart.")
    with c2:
        if st.button("🧪 Test OpenAI", use_container_width=True):
            if not openai_k.strip(): st.error("Enter key first.")
            else:
                with st.spinner("Testing…"):
                    r = _ask_openai([{"role":"user","content":"Say: connected"}],"You are a test bot.", openai_k.strip())
                st.success(f"✅ {r[:60]}") if r else st.error("❌ Failed — check key.")
    with c3:
        if st.button("🧪 Test SMTP", use_container_width=True):
            if not smtp_e or not smtp_p: st.error("Enter SMTP credentials.")
            else:
                with st.spinner("Sending test email…"):
                    from app import _send_otp
                    pass
                st.info("SMTP test — enter OTP screen to trigger a real send.")

    st.divider()
    st.markdown("### 🔬 Flask REST API")
    st.markdown("""Run the REST API alongside the Streamlit app:
```bash
# Terminal 1 — Streamlit
python -m streamlit run app.py

# Terminal 2 — Flask API
python api.py
```
Then test it:
```bash
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/recommend \\
     -H "Content-Type: application/json" \\
     -d '{"text":"I love coding Python","stream":"Science"}'
curl -X POST http://localhost:5000/api/nlp/analyze \\
     -H "Content-Type: application/json" \\
     -d '{"text":"I enjoy machine learning and data science"}'
```""")

    st.divider()
    st.markdown("### ℹ️ Tech Stack")
    st.markdown("""
| Component | Technology |
|---|---|
| UI Framework | Streamlit 1.35+ |
| ML Engine | TF-IDF + Cosine Similarity (scikit-learn) |
| NLP Pipeline | Custom tokenizer, stemmer, TF-IDF, NER, sentiment |
| Database | SQLite (users, sessions, bookmarks, feedback) |
| REST API | Flask + Flask-CORS |
| PDF Generator | ReportLab |
| Charts | Plotly |
| Auth | OTP via Gmail SMTP + password hashing (SHA-256) |
""")

    st.markdown("### 🔄 Session Controls")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("🗑 Clear Recommendations", use_container_width=True):
            st.session_state.recommendations=[]; st.success("Cleared.")
    with c2:
        if st.button("💬 Clear Chat", use_container_width=True):
            st.session_state.chat_history=[]; st.success("Cleared.")


# ── ML Insights ───────────────────────────────────────────────────────────────
def page_ml_insights():
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    import pandas as pd, json, os

    st.markdown('<div class="shdr">🤖 ML Model Insights</div>', unsafe_allow_html=True)
    st.caption("Full evaluation of 3 trained classifiers — Random Forest, Logistic Regression, SVM.")

    REPORT_PATH = os.path.join(os.path.dirname(__file__), "model", "ml_report.json")
    if not os.path.exists(REPORT_PATH):
        st.warning("Model not trained yet.")
        if st.button("🏋️ Train Models Now"):
            with st.spinner("Training 3 classifiers (~30s)…"):
                import ml_trainer; ml_trainer.train()
            st.success("Done! Reloading…"); st.rerun()
        return

    with open(REPORT_PATH) as f:
        rep = json.load(f)

    best = rep["best_model"]
    st.success(f"🏆 Best Model: **{best}** | Accuracy: **{rep['best_accuracy']*100:.2f}%** | F1: **{rep['best_f1']*100:.2f}%** | CV: **{rep['best_cv_mean']*100:.2f}% ± {rep['best_cv_std']*100:.2f}%**")

    # Section 1: Comparison
    st.markdown('<div class="shdr">📊 Section 1 — Algorithm Comparison</div>', unsafe_allow_html=True)
    comp    = rep["comparison"]
    metrics = ["accuracy","precision","recall","f1_score","cv_mean"]
    labels  = ["Accuracy","Precision","Recall","F1 Score","CV Score"]
    colors  = {"Random Forest":"#3b82f6","Logistic Regression":"#10b981","Support Vector Machine":"#7c3aed"}
    fig1 = go.Figure()
    for row in comp:
        fig1.add_trace(go.Bar(name=row["model"], x=labels,
            y=[row[m]*100 for m in metrics],
            marker_color=colors.get(row["model"],"#64748b"),
            text=[f"{row[m]*100:.1f}%" for m in metrics], textposition="outside"))
    fig1.update_layout(barmode="group", title="Model Performance (%)",
        paper_bgcolor="#060b18", plot_bgcolor="#0d1526", font=dict(color="#e2e8f0"),
        height=400, yaxis=dict(range=[0,110], gridcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"), legend=dict(bgcolor="#0d1526"))
    st.plotly_chart(fig1, use_container_width=True)
    df_comp = pd.DataFrame([{
        "Model": r["model"]+(" ✓" if r["model"]==best else ""),
        "Accuracy":  f"{r['accuracy']*100:.2f}%",
        "Precision": f"{r['precision']*100:.2f}%",
        "Recall":    f"{r['recall']*100:.2f}%",
        "F1 Score":  f"{r['f1_score']*100:.2f}%",
        "CV Mean":   f"{r['cv_mean']*100:.2f}% ± {r['cv_std']*100:.2f}%",
    } for r in sorted(comp, key=lambda x: x["f1_score"], reverse=True)])
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    st.divider()

    # Section 2: Confusion Matrix
    st.markdown('<div class="shdr">🔢 Section 2 — Confusion Matrix</div>', unsafe_allow_html=True)
    st.caption("Diagonal = correct predictions. Off-diagonal = misclassifications.")
    classes = rep["classes"]
    cm      = rep["confusion_matrix"]
    abbrev  = [c[:13]+"…" if len(c)>13 else c for c in classes]
    fig2 = ff.create_annotated_heatmap(
        z=cm, x=abbrev, y=abbrev,
        colorscale=[[0,"#060b18"],[0.4,"#1e3a8a"],[1,"#7c3aed"]],
        showscale=True, font_colors=["white"])
    fig2.update_layout(paper_bgcolor="#060b18", font=dict(color="#e2e8f0", size=8),
        height=580, margin=dict(t=30,b=130,l=130,r=20),
        xaxis=dict(tickangle=-45, side="bottom"))
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Section 3: Per-class
    st.markdown('<div class="shdr">📋 Section 3 — Per-Class Precision / Recall / F1</div>', unsafe_allow_html=True)
    per = rep["per_class_metrics"]
    pc  = [{"Career":c, "Precision":round(per[c]["precision"]*100,1),
             "Recall":round(per[c]["recall"]*100,1),
             "F1":round(per[c]["f1-score"]*100,1),
             "Support":int(per[c]["support"])}
           for c in classes if c in per]
    df_pc = pd.DataFrame(pc).sort_values("F1", ascending=False)
    fig3 = go.Figure()
    for metric, color in [("Precision","#3b82f6"),("Recall","#10b981"),("F1","#7c3aed")]:
        fig3.add_trace(go.Bar(name=metric, x=df_pc["Career"], y=df_pc[metric], marker_color=color, opacity=0.85))
    fig3.update_layout(barmode="group", paper_bgcolor="#060b18", plot_bgcolor="#0d1526",
        font=dict(color="#e2e8f0"), height=400,
        xaxis=dict(tickangle=-35, gridcolor="#1e293b"),
        yaxis=dict(range=[0,110], gridcolor="#1e293b"), legend=dict(bgcolor="#0d1526"))
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(df_pc.reset_index(drop=True), use_container_width=True, hide_index=True)

    st.divider()

    # Section 4: Feature Importance
    fi = rep.get("feature_importance",[])
    if fi:
        st.markdown('<div class="shdr">🔍 Section 4 — Feature Importance</div>', unsafe_allow_html=True)
        df_fi = pd.DataFrame(fi[:15])
        fig4 = go.Figure(go.Bar(y=df_fi["feature"], x=df_fi["importance"], orientation="h",
            marker=dict(color=df_fi["importance"],
                colorscale=[[0,"#1e3a8a"],[1,"#7c3aed"]], showscale=False),
            text=[f"{v:.4f}" for v in df_fi["importance"]], textposition="outside"))
        fig4.update_layout(title="Top 15 Features (One-Hot Encoded)",
            paper_bgcolor="#060b18", plot_bgcolor="#0d1526", font=dict(color="#e2e8f0"),
            height=460, margin=dict(l=20,r=60,t=50,b=20),
            xaxis=dict(gridcolor="#1e293b"), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # Section 5: Cross-Validation
    st.markdown('<div class="shdr">📈 Section 5 — 5-Fold Cross-Validation</div>', unsafe_allow_html=True)
    models = [r["model"] for r in comp]
    means  = [r["cv_mean"]*100 for r in comp]
    stds   = [r["cv_std"]*100  for r in comp]
    fig5 = go.Figure(go.Bar(x=models, y=means,
        error_y=dict(type="data", array=stds, visible=True, color="#f59e0b"),
        marker_color=["#3b82f6","#10b981","#7c3aed"],
        text=[f"{m:.1f}%±{s:.1f}%" for m,s in zip(means,stds)], textposition="outside"))
    fig5.update_layout(title="CV Accuracy (Mean ± Std Dev)",
        paper_bgcolor="#060b18", plot_bgcolor="#0d1526", font=dict(color="#e2e8f0"),
        height=340, yaxis=dict(range=[0,110],gridcolor="#1e293b"), xaxis=dict(gridcolor="#1e293b"))
    st.plotly_chart(fig5, use_container_width=True)
    cv1,cv2,cv3 = st.columns(3)
    for col,r in zip([cv1,cv2,cv3], comp):
        gap = abs(r["accuracy"]-r["cv_mean"])*100
        col.metric(r["model"].split()[0],
            "✅ Good Fit" if gap<5 else ("⚠️ Slight Overfit" if gap<10 else "❌ Overfit"),
            f"Test-CV gap: {gap:.1f}%")

    st.divider()

    # Section 6: Dataset summary
    st.markdown('<div class="shdr">🗂️ Section 6 — Dataset & Training Summary</div>', unsafe_allow_html=True)
    d1,d2,d3,d4 = st.columns(4)
    d1.metric("Total Samples",  rep["train_size"]+rep["test_size"])
    d2.metric("Training Set",   rep["train_size"])
    d3.metric("Test Set",       rep["test_size"])
    d4.metric("Career Classes", rep["n_classes"])
    st.markdown("**Input Features:**")
    st.markdown(" ".join(f'<span class="pill pill-purple">{f}</span>' for f in rep["features"]), unsafe_allow_html=True)
    st.markdown("**Target Classes (Careers):**")
    st.markdown(" ".join(f'<span class="pill pill-blue">{c}</span>' for c in rep["classes"]), unsafe_allow_html=True)

    st.divider()
    st.info("💡 **Viva tip:** Hybrid engine = 60% trained ML model + 40% TF-IDF semantic matching. "
            "ML handles structured profile inputs; TF-IDF handles free-text aspirations. "
            "Combined approach outperforms either alone.")

# ── Router ─────────────────────────────────────────────────────────────────────
def main():
    _sidebar()
    if not st.session_state.logged_in:
        page_login(); return
    {
        "home":      page_home,
        "guidance":  page_guidance,
        "nlp":       page_nlp,
        "chat":      page_chat,
        "resume":    page_resume,
        "bookmarks":   page_bookmarks,
        "analytics":   page_analytics,
        "ml_insights": page_ml_insights,
        "settings":    page_settings,
    }.get(st.session_state.page, page_home)()

if __name__ == "__main__":
    main()
