"""
career_data.py  —  All static career data, mappings, and option lists.
Extracted from the original PySide6 desktop app.
"""

# ── Dropdown Options ──────────────────────────────────────────────────────────

HOBBY_OPTIONS = [
    "🧠 Logic & Problem Solving (Puzzles / Maths / Debugging)",
    "🎨 Creativity & Design (Drawing, Branding, Innovation)",
    "🤝 People Interaction (Guiding, Teaching, Teamwork)",
    "📊 Business & Money (Entrepreneurship, Finance, Markets)",
    "🔬 Science & Experiments (Biology/Chemistry/Physics Labs)",
    "🧩 Technology & Computers (Coding, Hardware, AI, Cybersecurity)",
    "🏛️ Law, Policy & Governance (Debate, Ethics, Justice)",
    "🌍 Environment & Nature (Wildlife, Ecology, Sustainability)",
    "🏋️ Sports & Physical Training (Fitness, Coaching)",
    "🎭 Media & Communication (Content, Writing, Film, PR)",
    "🚀 Innovation & Future Tech (Space, EVs, Robotics, Metaverse)",
    "💗 Helping & Community Impact (Mental Health, NGOs, Social Work)",
]

FREE_TIME_OPTIONS = [
    "Coding/Technical Projects",
    "Online Courses/Learning",
    "Reading/Books",
    "Designing/Creative Work",
]

SUBJECT_OPTIONS = [
    "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology",
    "Botany", "Zoology", "Human Anatomy", "AI/ML/Data Science",
    "Economics/Commerce", "Business Management", "Design/Arts",
    "Law", "Legal Studies", "Political Science", "Civics", "Psychology",
]

# ── Stream / Field / Role Mappings ───────────────────────────────────────────

CAREER_MAPPINGS = {
    "streams": ["Science", "Commerce", "Arts", "Other"],
    "fields": {
        "Science": ["Medical & Healthcare", "Engineering & Technology", "Research & Development", "Data Science & Analytics"],
        "Commerce": [
            "Finance & Accounting Path", "Business & Management", "Economics & Data",
            "Banking & Government Services", "Law & Corporate Governance",
            "Creative + Business Fusion", "Tech + Commerce", "International Career",
        ],
        "Arts": ["Law & Legal Services", "Psychology & Counseling", "Media & Journalism", "Design & Creative Arts"],
        "Other": ["Government Services", "Defense", "Sports", "Other"],
    },
    "roles": {
        "Medical & Healthcare":       ["Doctor", "Dentist", "Nurse", "Pharmacist", "Medical Researcher"],
        "Engineering & Technology":   ["Software Engineer", "Data Scientist", "Mechanical Engineer", "Civil Engineer", "Electronics Engineer", "Aerospace Engineer"],
        "Research & Development":     ["Research Scientist", "Biotechnologist", "Lab Technician", "Biomedical Scientist"],
        "Data Science & Analytics":   ["Data Scientist", "Business Analyst", "AI Engineer", "Data Analyst"],
        "Finance & Accounting Path":  ["Chartered Accountant (CA)", "Cost & Management Accountant (CMA)", "Company Secretary (CS)", "CPA / ACCA Professional"],
        "Business & Management":      ["BBA Graduate (Marketing/HR/Finance/IB)", "MBA Leadership Roles", "Entrepreneur / Startup Founder", "Supply Chain & Logistics Manager", "Hospitality / Hotel Management", "Business Manager / Corporate Strategist"],
        "Economics & Data":           ["BA/BSc Economics Specialist", "Actuarial Scientist", "Business Analytics Professional", "Data Analyst (Business Intelligence)"],
        "Banking & Government Services": ["Banking Officer (IBPS/SBI PO)", "UPSC / SSC / Railways / Defence Accounts", "RBI / SEBI / Finance Officer"],
        "Law & Corporate Governance": ["B.Com + LLB Graduate", "Corporate Lawyer", "Company Secretary (CS)"],
        "Creative + Business Fusion": ["Advertising / Digital Marketing Manager", "Media Management Professional", "Event Management Specialist", "Fashion Business & Retail Strategist"],
        "Tech + Commerce":            ["FinTech Product Specialist", "E-Commerce Manager", "Business IT (BCA with Specialization)", "Cyber Finance Compliance Analyst"],
        "International Career":       ["International Business Manager", "Foreign Service Officer", "Global Supply Chain Analyst"],
        "Law & Legal Services":       ["Lawyer / Advocate", "Judge / Magistrate", "Legal Consultant", "Public Prosecutor"],
        "Psychology & Counseling":    ["Clinical Psychologist", "School Counselor", "Therapist", "HR Specialist"],
        "Media & Journalism":         ["Journalist", "Content Writer", "News Anchor", "Filmmaker"],
        "Design & Creative Arts":     ["Graphic Designer", "UX/UI Designer", "Fashion Designer", "Interior Designer"],
        "Government Services":        ["IAS Officer", "IPS Officer", "IFS Officer", "State Civil Services"],
        "Defense":                    ["Army Officer", "Navy Officer", "Air Force Officer", "Defense Scientist"],
        "Sports":                     ["Professional Athlete", "Sports Coach", "Sports Physiotherapist", "Sports Journalist"],
        "Other":                      ["Entrepreneur", "Social Worker", "NGO Professional", "Content Creator"],
        "Environmental Science":      ["Environmental Scientist", "Wildlife Biologist", "Climate Analyst"],
        "Innovation & Future Tech":   ["AI/ML Engineer", "Robotics Engineer", "Space Scientist", "EV Technology Engineer"],
    },
}

# Build derived maps
FIELD_TO_STREAM: dict[str, str] = {}
for _stream, _fields in CAREER_MAPPINGS["fields"].items():
    for _field in _fields:
        FIELD_TO_STREAM[_field] = _stream

FIELD_ROLE_MAP: dict[str, set] = {}
for _field, _roles in CAREER_MAPPINGS["roles"].items():
    for _role in _roles:
        FIELD_ROLE_MAP.setdefault(_role, set()).add(_field)

# ── Enhanced Career Details ───────────────────────────────────────────────────

ENHANCED_CAREER_DETAILS: dict[str, dict] = {
    "Software Engineer": {
        "description": "Design, develop, and maintain software systems and applications. Work across web, mobile, AI, and enterprise domains.",
        "education": ["Bachelor's in Computer Science", "Bachelor's in Software Engineering", "Master's in Computer Science"],
        "skills": ["Programming", "Algorithms", "Data Structures", "Software Design", "Testing", "Debugging"],
        "salary": "₹6–25 LPA (Fresh: ₹6–12 LPA, Senior: ₹15–25 LPA+)",
        "market": "High demand with 20%+ growth expected. Opportunities in IT services, product companies, startups.",
        "pros": ["High salary potential", "Remote work flexibility", "Global job opportunities", "Fast career growth"],
        "cons": ["Long hours at deadlines", "Constant tech upskilling", "High competition at top firms"],
        "roadmap": [
            "Complete 12th with PCM/CS",
            "Clear JEE/State CET for B.Tech CSE or pursue BCA",
            "Learn programming languages (Python/Java/C++/JavaScript)",
            "Build projects and contribute to GitHub",
            "Intern at IT companies during college",
            "Prepare for technical interviews (DSA, system design)",
            "Start as software developer and grow to senior roles",
        ],
    },
    "Data Scientist": {
        "description": "Extract insights from complex data using ML, statistical analysis, and visualisation techniques.",
        "education": ["B.Tech/B.Sc CS/Statistics", "Master's in Data Science", "MBA in Analytics"],
        "skills": ["Python/R", "Machine Learning", "Statistics", "SQL", "Data Visualisation"],
        "salary": "₹8–30 LPA (Fresh: ₹8–15 LPA, Senior: ₹20–30 LPA+)",
        "market": "Rapidly growing field with high demand across finance, healthcare, and e-commerce.",
        "pros": ["High demand in AI/ML companies", "Excellent compensation", "Work with cutting-edge tech"],
        "cons": ["Requires strong maths background", "Dealing with messy data", "High stakeholder expectations"],
        "roadmap": [
            "Complete 12th with PCM/CS",
            "Pursue B.Tech/B.Sc in CS/Statistics/Mathematics",
            "Learn Python, SQL, and statistics fundamentals",
            "Master ML frameworks (TensorFlow, scikit-learn)",
            "Build data science projects and Kaggle competitions",
            "Pursue internships and ML certifications",
            "Start as data analyst, progress to data scientist",
        ],
    },
    "Doctor": {
        "description": "Medical professional diagnosing and treating illnesses, injuries, and providing healthcare services.",
        "education": ["MBBS (5.5 years)", "MD/MS for specialisation", "Residency Training"],
        "skills": ["Medical Knowledge", "Diagnosis", "Patient Care", "Communication", "Emergency Handling"],
        "salary": "₹10–50 LPA (Junior: ₹10–15 LPA, Specialist: ₹25–50 LPA+)",
        "market": "Always in demand with stable career prospects across hospitals, clinics, and research.",
        "pros": ["Excellent job security", "High respect in society", "Opportunity to save lives", "High earning potential"],
        "cons": ["Very long education period", "Extremely high stress", "Expensive medical education"],
        "roadmap": [
            "Class 11–12 with PCB",
            "Crack NEET-UG to secure MBBS seat",
            "Complete MBBS (5.5 years including internship)",
            "Clear NEET-PG or INI CET for specialisation",
            "Complete MD/MS + residency",
        ],
    },
    "Dentist": {
        "description": "Diagnose and treat dental issues, perform oral surgeries, and provide preventive dental care.",
        "education": ["BDS (Bachelor of Dental Surgery)", "MDS for specialisation"],
        "skills": ["Dental Procedures", "Oral Surgery", "Patient Care", "Manual Dexterity"],
        "salary": "₹6–25 LPA (Fresh: ₹6–10 LPA, Specialist: ₹15–25 LPA+)",
        "market": "Steady demand in private clinics, hospitals, and government dental facilities.",
        "pros": ["Can start own clinic", "Less competition than MBBS", "Shorter education than MBBS"],
        "cons": ["High equipment costs for own practice", "Physical strain", "5-year BDS education"],
        "roadmap": [
            "Complete 12th with PCB",
            "Clear NEET-UG for BDS admission",
            "Complete BDS (5 years including internship)",
            "Register with Dental Council of India",
            "Optionally pursue MDS for specialisation",
            "Start practice or join dental clinic/hospital",
        ],
    },
    "Nurse": {
        "description": "Provide patient care, assist doctors, administer medications, and monitor patient health.",
        "education": ["B.Sc Nursing", "GNM (General Nursing & Midwifery)", "Post Basic B.Sc Nursing"],
        "skills": ["Patient Care", "Medical Procedures", "Communication", "Empathy", "Emergency Response"],
        "salary": "₹3–12 LPA (Staff Nurse: ₹3–6 LPA, Senior Nurse: ₹8–12 LPA)",
        "market": "High demand in hospitals, clinics, nursing homes, and community health centres.",
        "pros": ["Job security", "Opportunity to help people", "Diverse work settings"],
        "cons": ["Physically demanding", "Shift work", "Emotional stress"],
        "roadmap": [
            "Complete 12th with PCB",
            "Qualify for B.Sc Nursing/GNM entrance exams",
            "Complete nursing degree",
            "Register with State Nursing Council",
            "Start as staff nurse and progress to senior roles",
        ],
    },
    "Pharmacist": {
        "description": "Dispense medicines, counsel patients, manage drug inventory, and ensure regulatory compliance.",
        "education": ["D.Pharm", "B.Pharm", "M.Pharm", "Pharm.D"],
        "skills": ["Pharmacology", "Drug Dispensing", "Patient Counseling", "Inventory Management"],
        "salary": "₹3–12 LPA (Retail: ₹3–6 LPA, Hospital: ₹4–8 LPA, Senior: ₹8–12 LPA)",
        "market": "Steady demand across hospitals, retail chains, and pharmaceutical companies.",
        "pros": ["Multiple work settings", "Option to start own medical store", "Lower entry barrier than MBBS"],
        "cons": ["Long hours standing in retail", "Strict regulatory oversight", "Moderate salary in retail"],
        "roadmap": [
            "Study PCB in Class 11–12",
            "Appear for D.Pharm or B.Pharm entrance",
            "Complete internship + register with State Pharmacy Council",
            "Optionally pursue M.Pharm/Pharm.D for advanced roles",
        ],
    },
    "Mechanical Engineer": {
        "description": "Design, develop, and maintain mechanical systems, machinery, and manufacturing processes.",
        "education": ["B.Tech in Mechanical Engineering", "M.Tech for specialisation"],
        "skills": ["CAD/CAM", "Machine Design", "Thermodynamics", "Manufacturing Processes"],
        "salary": "₹5–20 LPA (Fresh: ₹5–8 LPA, Senior: ₹12–20 LPA+)",
        "market": "Stable demand in manufacturing, automotive, energy, and infrastructure sectors.",
        "pros": ["Diverse industry options", "Hands-on work", "Good job stability"],
        "cons": ["Can be physically demanding", "Manufacturing sector fluctuations"],
        "roadmap": [
            "Complete 12th with PCM",
            "Clear JEE/State CET for B.Tech Mechanical",
            "Complete B.Tech (4 years)",
            "Gain internship experience",
            "Optionally pursue M.Tech",
        ],
    },
    "Civil Engineer": {
        "description": "Design, construct, and maintain infrastructure projects like buildings, roads, and bridges.",
        "education": ["B.Tech in Civil Engineering", "M.Tech in Structural/Transportation Engineering"],
        "skills": ["Structural Design", "Construction Management", "AutoCAD", "Project Planning"],
        "salary": "₹4–18 LPA (Fresh: ₹4–7 LPA, Senior: ₹10–18 LPA+)",
        "market": "Consistent demand due to infrastructure development and urbanisation projects.",
        "pros": ["Tangible results", "Job stability", "Government opportunities"],
        "cons": ["Site-based work", "Weather dependent", "Safety risks"],
        "roadmap": [
            "Complete 12th with PCM",
            "Clear JEE/State CET for B.Tech Civil",
            "Complete B.Tech (4 years)",
            "Gain site experience through internships",
            "Start as site engineer or design engineer",
        ],
    },
    "AI Engineer": {
        "description": "Build AI systems, train machine-learning models, and deploy intelligent applications at scale.",
        "education": ["B.Tech CS/AI", "M.Tech/M.S. in AI/ML", "Relevant online certifications"],
        "skills": ["Deep Learning", "Python", "PyTorch/TensorFlow", "MLOps", "Cloud (AWS/GCP/Azure)"],
        "salary": "₹12–50 LPA (Fresh: ₹12–20 LPA, Senior AI/ML: ₹30–50 LPA+)",
        "market": "One of the fastest-growing tech roles globally; demand far exceeds supply.",
        "pros": ["Cutting-edge work", "Extremely high salaries", "Remote-first companies", "Global opportunities"],
        "cons": ["Requires deep maths/stats knowledge", "Rapidly changing landscape", "High expectations"],
        "roadmap": [
            "Complete 12th with PCM/CS",
            "Pursue B.Tech CSE or B.Sc CS/Maths",
            "Master Python, linear algebra, probability, and statistics",
            "Learn ML/DL frameworks (PyTorch, TensorFlow)",
            "Build end-to-end AI projects and publish on GitHub",
            "Contribute to open-source AI research",
            "Join AI-focused companies or research labs",
        ],
    },
    "Data Analyst": {
        "description": "Collect, process, and analyse data to generate actionable business insights.",
        "education": ["B.Tech CS/IT", "B.Sc Statistics/Mathematics", "Business Analytics certifications"],
        "skills": ["Excel", "SQL", "Python/R", "Power BI/Tableau", "Statistical Analysis"],
        "salary": "₹4–18 LPA (Entry: ₹4–7 LPA, Senior: ₹10–18 LPA+)",
        "market": "High demand across banking, e-commerce, healthcare, and consulting.",
        "pros": ["Entry-level accessible", "Wide industry applicability", "Clear career path to Data Scientist"],
        "cons": ["Often junior role", "Repetitive tasks at entry level", "Requires SQL and stats skills"],
        "roadmap": [
            "Complete graduation in any stream (CS/Stats preferred)",
            "Learn Excel, SQL, and a BI tool (Power BI / Tableau)",
            "Learn Python basics for data manipulation",
            "Build analyst portfolio with real datasets",
            "Apply for analyst roles in IT/banking/e-commerce",
        ],
    },
    "Chartered Accountant (CA)": {
        "description": "Provide accounting, auditing, taxation, and financial advisory services to organisations and individuals.",
        "education": ["CA Foundation → Intermediate → Final (ICAI)", "BCom alongside is common"],
        "skills": ["Accounting", "Taxation", "Auditing", "Financial Reporting", "Compliance"],
        "salary": "₹8–30 LPA (Big 4: ₹15–25 LPA, experienced CAs: ₹30 LPA+)",
        "market": "Evergreen demand; every company needs CA services for compliance, audits, and tax filing.",
        "pros": ["High prestige", "Own practice possible", "Diverse industries", "Excellent pay after qualification"],
        "cons": ["Very competitive exam (~10–15% pass rate)", "3+ years articleship", "Long qualification journey"],
        "roadmap": [
            "Complete 10+2 (Commerce preferred)",
            "Register for CA Foundation after Class 12",
            "Clear Foundation → Intermediate → Final exams",
            "Complete 3-year articleship under a practising CA",
            "Join Big 4 firms or set up own CA practice",
        ],
    },
    "MBA Leadership Roles": {
        "description": "Senior management and leadership positions attained after MBA — include product management, consulting, and C-suite tracks.",
        "education": ["MBA from top B-school (IIM, ISB, XLRI)", "BBA/BCom + work experience"],
        "skills": ["Leadership", "Strategy", "Finance", "Operations", "Communication"],
        "salary": "₹15–50 LPA (IIM grads: ₹20–40 LPA, experienced: ₹50 LPA+)",
        "market": "Strong demand for MBA grads in consulting, FMCG, banking, tech, and startups.",
        "pros": ["Rapid career growth", "Access to top company placements", "High compensation"],
        "cons": ["Very competitive CAT/GMAT preparation required", "High course fees (₹20–35 lakhs)", "2 years lost income"],
        "roadmap": [
            "Complete graduation in any discipline",
            "Gain 2–3 years work experience",
            "Prepare for CAT/XAT/GMAT entrance exams",
            "Secure admission to top B-school",
            "Complete 2-year MBA",
            "Start in management trainee or consulting role",
        ],
    },
    "Lawyer / Advocate": {
        "description": "Represent clients in legal matters, draft contracts, provide legal advice, and argue cases in courts.",
        "education": ["BA LLB (5-year integrated)", "LLB (3 years after graduation)", "LLM for specialisation"],
        "skills": ["Legal Research", "Argumentation", "Drafting", "Negotiation", "Communication"],
        "salary": "₹3–40 LPA (Fresh: ₹3–6 LPA, Senior: ₹15–40 LPA+, top litigation lawyers: ₹1 Cr+)",
        "market": "Steady demand across corporate law, litigation, and government legal services.",
        "pros": ["High earning potential at senior levels", "Prestige", "Diverse specialisations"],
        "cons": ["Slow start to career", "Long court hours", "Competitive landscape"],
        "roadmap": [
            "Complete 12th in any stream",
            "Clear CLAT/AILET for integrated BA LLB (5 years)",
            "Or complete graduation + 3-year LLB",
            "Complete internships at law firms and courts",
            "Enrol with Bar Council after degree",
            "Start as junior advocate or join law firm",
        ],
    },
    "IAS Officer": {
        "description": "Top administrative civil servant managing government departments, policy implementation, and district governance.",
        "education": ["Any graduate degree", "UPSC Civil Services Examination"],
        "skills": ["Leadership", "Policy Analysis", "Communication", "Crisis Management", "Decision Making"],
        "salary": "₹56,100–₹2,50,000/month + benefits (effective ₹8–25 LPA equivalent)",
        "market": "Highly selective (0.1% selection rate) but extremely prestigious and secure.",
        "pros": ["Immense power and responsibility", "Job security", "Work-life balance after senior levels", "Prestige"],
        "cons": ["Extremely competitive exam", "2–3 years of intense preparation", "Field postings to remote areas"],
        "roadmap": [
            "Complete graduation in any discipline",
            "Start UPSC preparation (Prelims → Mains → Interview)",
            "Study General Studies, optional subject, and Current Affairs",
            "Attempt UPSC CSE (max 6 attempts for General category)",
            "Complete IAS/IPS/IFS training at LBSNAA",
        ],
    },
    "Journalist": {
        "description": "Research, investigate, and report news stories across print, digital, TV, or radio platforms.",
        "education": ["BA/B.Sc in Journalism & Mass Communication", "PG Diploma in Journalism"],
        "skills": ["Writing", "Interviewing", "Research", "Photography/Video", "Fact-checking"],
        "salary": "₹3–20 LPA (Entry: ₹3–5 LPA, Senior: ₹10–20 LPA at major outlets)",
        "market": "Evolving with digital media growth; demand for digital journalists, fact-checkers, and data journalists.",
        "pros": ["Exciting fieldwork", "Public impact", "Diverse beats (politics, tech, sports, etc.)"],
        "cons": ["Low starting salaries", "Irregular hours", "Job instability at smaller outlets"],
        "roadmap": [
            "Complete 12th in any stream",
            "Pursue BA in Journalism or Mass Communication",
            "Intern at newspapers, TV channels, or news websites",
            "Build a portfolio of published articles",
            "Apply to entry-level reporter roles",
        ],
    },
    "Graphic Designer": {
        "description": "Create visual concepts using design software to communicate ideas through images, typography, and layouts.",
        "education": ["B.Des in Graphic Design", "BFA", "Diploma in Graphic Design", "Self-taught + portfolio"],
        "skills": ["Adobe Photoshop", "Illustrator", "InDesign", "Typography", "Colour Theory"],
        "salary": "₹3–18 LPA (Junior: ₹3–6 LPA, Senior: ₹10–18 LPA, freelance: variable)",
        "market": "Consistent demand from ad agencies, digital companies, startups, and freelance markets.",
        "pros": ["Creative work", "Freelance flexibility", "Portfolio-based hiring (degree not always required)"],
        "cons": ["Highly competitive", "Client revision demands", "Variable freelance income"],
        "roadmap": [
            "Complete 12th in any stream",
            "Pursue B.Des / Diploma in Graphic Design",
            "Master Adobe tools (Photoshop, Illustrator)",
            "Build a strong portfolio on Behance/Dribbble",
            "Intern at design agencies or startups",
            "Start as junior designer or go freelance",
        ],
    },
    "UX/UI Designer": {
        "description": "Design intuitive digital interfaces and user experiences for websites, apps, and software products.",
        "education": ["B.Des in Interaction Design", "HCI courses", "Bootcamps + portfolio"],
        "skills": ["Figma", "User Research", "Prototyping", "Wireframing", "Usability Testing"],
        "salary": "₹5–25 LPA (Junior: ₹5–9 LPA, Senior: ₹15–25 LPA+)",
        "market": "High demand at tech companies, startups, and product firms.",
        "pros": ["Creative + analytical blend", "High demand at tech companies", "Remote-friendly"],
        "cons": ["Requires constant portfolio upkeep", "Stakeholder feedback can be subjective"],
        "roadmap": [
            "Complete graduation in Design / CS / any field",
            "Learn Figma, Adobe XD, and UX research methods",
            "Build a portfolio with 3–5 case studies",
            "Seek internships at product companies",
            "Apply to UX/UI roles at tech startups or agencies",
        ],
    },
    "Clinical Psychologist": {
        "description": "Assess, diagnose, and treat mental health conditions through therapy and psychological interventions.",
        "education": ["BA/BSc Psychology", "MA/MSc Clinical Psychology", "RCI Licence required in India"],
        "skills": ["Therapy Techniques (CBT, DBT)", "Assessment", "Empathy", "Report Writing", "Research"],
        "salary": "₹4–20 LPA (Counselor: ₹4–8 LPA, Senior Clinician: ₹12–20 LPA)",
        "market": "Growing rapidly due to rising mental health awareness in India.",
        "pros": ["High societal impact", "Growing demand", "Private practice option"],
        "cons": ["Long education path", "Emotionally demanding", "Requires RCI registration"],
        "roadmap": [
            "Complete 12th in any stream",
            "Pursue BA/BSc in Psychology",
            "Complete MA/MSc in Clinical Psychology",
            "Register with Rehabilitation Council of India (RCI)",
            "Intern at hospitals/NGOs",
            "Start as counsellor or junior psychologist",
        ],
    },
    "Entrepreneur / Startup Founder": {
        "description": "Build and scale a new business from ideation to revenue, managing product, team, and growth.",
        "education": ["Any degree (MBA helpful, not required)", "Practical experience > formal education"],
        "skills": ["Problem-solving", "Leadership", "Sales/Marketing", "Financial Management", "Resilience"],
        "salary": "Variable: ₹0 in early stages → ₹50 LPA+ if successful",
        "market": "India's startup ecosystem is one of the world's fastest-growing with strong VC funding.",
        "pros": ["Unlimited earning potential", "Creative freedom", "Build something meaningful", "Equity upside"],
        "cons": ["High risk of failure (90%+ startups fail)", "No guaranteed salary", "Extremely high stress"],
        "roadmap": [
            "Gain domain expertise through education/work",
            "Identify a problem worth solving",
            "Validate the idea with real users (MVP)",
            "Secure initial funding (bootstrapped, angel, or VC)",
            "Build a team and iterate rapidly",
            "Scale with product-market fit",
        ],
    },
    "Research Scientist": {
        "description": "Conduct original scientific research to advance knowledge in fields like physics, chemistry, biology, or engineering.",
        "education": ["B.Sc + M.Sc + PhD in relevant field", "Postdoctoral research common"],
        "skills": ["Scientific Method", "Data Analysis", "Technical Writing", "Lab Work", "Critical Thinking"],
        "salary": "₹6–25 LPA (Govt research: ₹6–12 LPA, Industry R&D: ₹12–25 LPA+)",
        "market": "Steady demand in government labs (ISRO, DRDO, CSIR) and pharmaceutical/tech R&D.",
        "pros": ["Intellectual fulfilment", "Job security in govt labs", "Contributing to human knowledge"],
        "cons": ["Long education path", "Competitive PhD admissions", "Slower salary growth"],
        "roadmap": [
            "Complete 12th with PCM/PCB",
            "Pursue B.Sc in relevant field",
            "Clear JAM/CUET for M.Sc admission",
            "Complete M.Sc with strong CGPA",
            "Clear CSIR-NET/GATE for PhD fellowship",
            "Join research institute or industry R&D lab",
        ],
    },
    "Business Analyst": {
        "description": "Bridge the gap between business needs and technology solutions by analysing processes and defining requirements.",
        "education": ["B.Tech CS/IT", "BBA/BCom", "MBA in Systems/Analytics"],
        "skills": ["Requirements Gathering", "SQL", "Excel", "Process Mapping", "Stakeholder Communication"],
        "salary": "₹6–22 LPA (Fresh: ₹6–10 LPA, Senior: ₹14–22 LPA+)",
        "market": "High demand in IT services, banking, consulting, and product companies.",
        "pros": ["Bridge between tech and business", "Clear growth to product management", "Good compensation"],
        "cons": ["Can be repetitive at entry level", "Depends heavily on company size and domain"],
        "roadmap": [
            "Complete graduation in CS, Commerce, or MBA",
            "Learn SQL, Excel, and basic data tools",
            "Get CBAP or agile certifications (optional but helpful)",
            "Apply to IT services or consulting firms as junior BA",
            "Progress to senior BA or product manager",
        ],
    },
    "Aerospace Engineer": {
        "description": "Design, develop, and test aircraft, spacecraft, and related systems and equipment.",
        "education": ["B.Tech in Aerospace Engineering", "M.Tech/M.S. for specialisation"],
        "skills": ["Aerodynamics", "Propulsion", "Structural Analysis", "CAD", "MATLAB/Python"],
        "salary": "₹6–25 LPA (Fresh: ₹6–10 LPA, Senior: ₹15–25 LPA; ISRO/DRDO roles highly competitive)",
        "market": "Niche but growing; demand from ISRO, DRDO, HAL, and global aerospace firms.",
        "pros": ["Prestige of working in space/aviation", "Intellectually challenging", "Government opportunities"],
        "cons": ["Very few companies in India", "Competitive and specialised", "Requires strong physics/maths"],
        "roadmap": [
            "Complete 12th with PCM (strong physics & maths)",
            "Clear JEE for B.Tech Aerospace at IIT/NIT/IIST",
            "Focus on CFD, propulsion, and structures coursework",
            "Intern at HAL, ISRO, or aerospace companies",
            "Apply to ISRO/DRDO or pursue M.S. abroad",
        ],
    },
}

# Fill any role in CAREER_MAPPINGS that's missing from ENHANCED_CAREER_DETAILS with a basic profile
for _field, _roles in CAREER_MAPPINGS["roles"].items():
    for _role in _roles:
        if _role not in ENHANCED_CAREER_DETAILS:
            _fields_for_role = FIELD_ROLE_MAP.get(_role, {_field})
            ENHANCED_CAREER_DETAILS[_role] = {
                "description": f"{_role} — professional in the {_field} sector.",
                "education": ["Relevant Bachelor's Degree", "Industry Certifications"],
                "skills": ["Communication", "Problem-solving", "Domain expertise"],
                "salary": "₹5–20 LPA (varies by experience)",
                "market": "Steady demand in relevant sectors.",
                "pros": ["Career growth opportunities", "Diverse work environments"],
                "cons": ["Competitive field", "Continuous learning required"],
                "roadmap": [
                    "Complete 12th in relevant stream",
                    f"Pursue relevant degree for {_role}",
                    "Gain industry experience through internships",
                    "Obtain relevant certifications",
                    "Start entry-level and grow with experience",
                ],
            }

# ── Offline AI fallback answers ───────────────────────────────────────────────

OFFLINE_RESPONSES = {
    ("software", "coding", "developer", "programmer"): (
        "💻 **Software Engineering Career**\n\n"
        "- **Education:** B.Tech CSE / BCA\n"
        "- **Entrance:** JEE Main / BITSAT / State CETs\n"
        "- **Key Skills:** Python, Java, DSA, SQL\n"
        "- **Salary:** ₹6–25 LPA (top companies: ₹15–40 LPA)\n"
        "- **Top Companies:** Google, Microsoft, Amazon, TCS\n\n"
        "**Roadmap:** Python → DSA → Projects → Internships!"
    ),
    ("neet", "doctor", "medical", "mbbs"): (
        "🏥 **Medical Career (NEET)**\n\n"
        "- **Exam:** NEET-UG for MBBS/BDS\n"
        "- **Duration:** MBBS = 5.5 years\n"
        "- **Salary:** ₹10–50 LPA (specialists earn more)\n"
        "- **Top Colleges:** AIIMS Delhi, CMC Vellore, KMC Manipal\n\n"
        "**Study Plan:** NCERT → Reference Books → Mock Tests!"
    ),
    ("data", "ai", "machine learning", "ml"): (
        "📊 **Data Science / AI Career**\n\n"
        "- **Education:** B.Tech CS / B.Sc Statistics\n"
        "- **Key Skills:** Python, ML, Statistics, SQL\n"
        "- **Salary:** ₹8–30 LPA (AI roles: ₹15–50 LPA)\n"
        "- **Platforms:** Kaggle, Coursera, fast.ai\n\n"
        "**Roadmap:** Python → Stats → ML → Projects → Jobs!"
    ),
    ("ca", "chartered", "accountant"): (
        "📈 **Chartered Accountant (CA)**\n\n"
        "- **Path:** Foundation → Intermediate → Final\n"
        "- **Duration:** 4–5 years\n"
        "- **Salary:** ₹8–30 LPA (Big 4: ₹15–25 LPA)\n"
        "- **Pass Rate:** ~10–15% (very competitive)\n\n"
        "**Tip:** Start articleship early!"
    ),
    ("mba", "management", "cat", "iim"): (
        "🎓 **MBA Career**\n\n"
        "- **Entrance:** CAT / XAT / GMAT\n"
        "- **Duration:** 2 years post-graduation\n"
        "- **Top Institutes:** IIM A/B/C, XLRI, ISB\n"
        "- **Salary:** ₹15–50 LPA (IIM graduates)\n\n"
        "**CAT Prep:** Quant + VARC + DILR — 6 months!"
    ),
}

def get_offline_response(question: str) -> str:
    q = question.lower()
    for keywords, response in OFFLINE_RESPONSES.items():
        if any(w in q for w in keywords):
            return response
    return (
        "🎯 **Career Guidance Tips**\n\n"
        "- Identify your interests and strengths\n"
        "- Research careers matching your stream\n"
        "- Focus on skills + academics + projects\n"
        "- Build a portfolio and network early\n"
        "- Consider both traditional and emerging careers\n\n"
        "Ask me anything specific about careers, exams, or skills!"
    )
