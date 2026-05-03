import streamlit as st

# 1. Page Config
st.set_page_config(layout="wide", page_title="Gapix AI Platform", page_icon="🚀")

import sqlite3
import hashlib
from PyPDF2 import PdfReader
import plotly.graph_objects as go
import time
import pandas as pd
import re

# API Configuration
import requests
import json

# API Key ko code se hata kar secrets se read karo
api_key = st.secrets["OPENROUTER_API_KEY"]
SELECTED_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"

# ==========================================
# 🔐 ADVANCED DATABASE MODULE
# ==========================================
conn = sqlite3.connect('gapix_users.db', check_same_thread=False)
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, email TEXT, password TEXT, role TEXT)')
    # 👇 Nayi table chat history ke liye
    c.execute('''CREATE TABLE IF NOT EXISTS chat_logs(
                 email TEXT, 
                 role TEXT, 
                 content TEXT, 
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, email, password, role):
    c.execute('INSERT INTO userstable(username, email, password, role) VALUES (?,?,?,?)', (username, email, password, role))
    conn.commit()

def login_user(email, password):
    c.execute('SELECT * FROM userstable WHERE email = ? AND password = ?', (email, password))
    return c.fetchall()

def view_all_users():
    c.execute('SELECT username, email, role FROM userstable')
    return c.fetchall()

def add_chat_message(email, role, content):
    c.execute('INSERT INTO chat_logs(email, role, content) VALUES (?,?,?)', (email, role, content))
    conn.commit()

def get_user_chat_history(email):
    c.execute('SELECT role, content FROM chat_logs WHERE email = ? ORDER BY timestamp ASC', (email,))
    return c.fetchall()

def view_all_chats():
    c.execute('SELECT * FROM chat_logs ORDER BY timestamp DESC')
    return c.fetchall()

create_usertable()

# ==========================================
# 📊 ROLES DATA
# ==========================================
ROLES_DATA = {
    "Generative AI Engineer": {"Skills": ["LLMs", "LangChain", "Vector Databases", "Prompt Engineering", "PyTorch", "OpenAI API", "HuggingFace", "Python"]},
    "Data Scientist & ML Engineer": {"Skills": ["Python", "Pandas", "Scikit-Learn", "Deep Learning", "SQL", "Statistics", "TensorFlow", "Computer Vision"]},
    "Data Engineer": {"Skills": ["Python", "SQL", "Spark", "Kafka", "Airflow", "AWS", "ETL", "Snowflake"]},
    "Data Analyst (BI)": {"Skills": ["SQL", "Power BI", "Tableau", "Excel", "Data Modeling", "Python", "Business Intelligence"]},
    "Prompt Engineer (Specialized)": {"Skills": ["ChatGPT", "Midjourney", "Claude", "Few-Shot Prompting", "Chain of Thought", "Content Generation", "AI Ethics"]},
    "Full Stack Developer (MERN/Next)": {"Skills": ["Next.js", "React", "TypeScript", "Node.js", "MongoDB", "PostgreSQL", "Prisma", "Docker"]},
    "Frontend UI Developer": {"Skills": ["HTML", "CSS", "JavaScript", "React", "Vue", "Tailwind CSS", "Redux", "Responsive Design"]},
    "Backend Systems Engineer": {"Skills": ["Python", "Java", "Go", "Node.js", "REST APIs", "Microservices", "System Design", "SQL"]},
    "Mobile App Developer": {"Skills": ["Flutter", "React Native", "Swift", "Kotlin", "Firebase", "Mobile UI", "App Store Deployment"]},
    "Cloud & DevOps Engineer": {"Skills": ["AWS", "Azure", "Kubernetes", "Docker", "Terraform", "CI/CD Pipelines", "Linux Shell", "GitHub Actions"]},
    "Site Reliability Engineer (SRE)": {"Skills": ["Linux", "Networking", "Prometheus", "Grafana", "Incident Response", "Python", "Infrastructure as Code"]},
    "Cybersecurity Analyst": {"Skills": ["Ethical Hacking", "Network Security", "SOC Analyst", "Penetration Testing", "Wireshark", "Linux Security", "Zero Trust"]},
    "Cloud Solutions Architect": {"Skills": ["AWS", "System Design", "Cost Optimization", "Microservices architecture", "Serverless", "Network Security"]},
    "Product Manager (Tech)": {"Skills": ["Agile", "Jira", "Product Roadmap", "User Research", "Market Analysis", "Stakeholder Management", "A/B Testing"]},
    "UI/UX Product Designer": {"Skills": ["Figma", "Adobe XD", "Prototyping", "User Experience Research", "Wireframing", "Visual Design", "Design Systems"]},
    "Blockchain/Web3 Developer": {"Skills": ["Solidity", "Smart Contracts", "Ethereum", "Rust", "Web3.js", "Cryptography", "Hyperledger"]},
    "Game Developer": {"Skills": ["Unity", "Unreal Engine", "C#", "C++", "3D Math", "Game Physics", "Shader Programming"]},
    "AR/VR Meta Developer": {"Skills": ["Unity", "C#", "Oculus SDK", "ARCore", "ARKit", "3D Modeling", "Spatial Computing"]},
    "QA Automation Engineer": {"Skills": ["Selenium", "Cypress", "Playwright", "Java", "Python", "API Testing", "Postman", "CI/CD"]},
    "Salesforce Developer": {"Skills": ["Apex", "Lightning Web Components", "SOQL", "Salesforce CRM", "API Integration", "Visualforce"]}
}

# ==========================================
# 🚀 FUNCTION: RENDER AI DASHBOARD
# ==========================================
def render_ai_dashboard():
    st.title("🚀 Gapix Intelligence Platform")
    st.markdown("---")

    col_main, col_chat = st.columns([7, 3], gap="large")

    # --- LEFT COLUMN: SCANNER & COVER LETTER ---
    with col_main:
        st.subheader("🎯 Skill Gap Analysis")
        selected_role = st.selectbox("Select Target Career Path", list(ROLES_DATA.keys()))
        uploaded_file = st.file_uploader("Upload Resume (PDF Format)", type="pdf")

        if uploaded_file:
            with st.spinner("Gapix Engine scanning..."):
                reader = PdfReader(uploaded_file)
                resume_text = " ".join([p.extract_text().lower() for p in reader.pages if p.extract_text()])
                
                target_skills = ROLES_DATA[selected_role]["Skills"]
                found = [s for s in target_skills if s.lower() in resume_text]
                missing = [s for s in target_skills if s not in found]
                
                total = len(target_skills)
                score = int((len(found) / total) * 100) if total > 0 else 0

                st.markdown("<div class='main-card' style='margin-top: 20px;'>", unsafe_allow_html=True)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=score, 
                    number={'suffix': "%", 'font': {'size': 50, 'color': "#ffffff"}},
                    title={'text': "Market Readiness Score", 'font': {'size': 20, 'color': "#ffffff"}},
                    gauge={
                        'axis': {'range': [0, 100], 'visible': True, 'tickmode': 'linear', 'tick0': 0, 'dtick': 20, 'tickcolor': "white"},
                        'bar': {'color': "#6366f1"}, 'bgcolor': "rgba(255,255,255,0.1)", 'borderwidth': 0
                    }
                ))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True, key=f"gauge_{score}")
                st.markdown("</div>", unsafe_allow_html=True)

                found_tags = " ".join([f"<span style='background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 3px; display: inline-block; border: 1px solid #10b981;'>{s}</span>" for s in found]) if found else "<span style='color:#94a3b8; font-size:12px;'>No exact match</span>"
                missing_tags = " ".join([f"<span style='background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 3px; display: inline-block; border: 1px solid #ef4444;'>{s}</span>" for s in missing]) if missing else "<span style='color:#94a3b8; font-size:12px;'>All clear!</span>"

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"<div style='background-color: rgba(99, 102, 241, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(99, 102, 241, 0.3);'><h3 style='margin: 0; color: #6366f1; font-size: 28px;'>{total}</h3><p style='margin: 0; color: #94a3b8; font-size: 14px; font-weight: bold;'>🎯 Total Skills Needed</p></div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div style='background-color: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(16, 185, 129, 0.3);'><h3 style='margin: 0; color: #10b981; font-size: 28px;'>{len(found)}</h3><p style='margin: 0 0 10px 0; color: #94a3b8; font-size: 14px; font-weight: bold;'>✅ Skills Matched</p><div>{found_tags}</div></div>", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"<div style='background-color: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 10px; text-align: center; border: 1px solid rgba(239, 68, 68, 0.3);'><h3 style='margin: 0; color: #ef4444; font-size: 28px;'>{len(missing)}</h3><p style='margin: 0 0 10px 0; color: #94a3b8; font-size: 14px; font-weight: bold;'>🚨 Skills to Learn</p><div>{missing_tags}</div></div>", unsafe_allow_html=True)

                if missing:
                    st.markdown("---")
                    st.subheader("📚 Your Custom Learning Path")
                    for skill in missing:
                        url_skill = skill.replace(" ", "+")
                        st.markdown(f"<div style='background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ef4444;'><h4 style='margin:0 0 10px 0; padding:0; color: #f8fafc;'>🔥 {skill}</h4><a href='https://www.youtube.com/results?search_query={url_skill}+full+course+2025' target='_blank' style='text-decoration: none; color: #ef4444; margin-right: 15px; font-weight: bold;'>🎬 Free YouTube Course</a><a href='https://www.coursera.org/search?query={url_skill}' target='_blank' style='text-decoration: none; color: #3b82f6; font-weight: bold;'>🎓 Coursera Certification</a></div>", unsafe_allow_html=True)
                elif total > 0:
                    st.balloons(); st.success("🎉 You are 100% Market Ready!")

                st.markdown("---")
                st.subheader("✨ AI Cover Letter Generator")
                if st.button("Generate Cover Letter 🚀", use_container_width=True):
                    with st.spinner("Writing..."):
                        try:
                            payload = {"model": SELECTED_MODEL, "messages": [{"role": "user", "content": f"Write professional cover letter for {selected_role} based on resume: {resume_text}"}]}
                            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://gapix.ai", "X-Title": "Gapix AI"}
                            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
                            reply = response.json()['choices'][0]['message']['content']
                            st.markdown(f"<div style='background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border-left: 4px solid #10b981;'>{reply}</div>", unsafe_allow_html=True)
                        except Exception as e: st.error(f"Error: {e}")

    # --- RIGHT COLUMN: AI COPILOT ---
    with col_chat:
        st.subheader("🤖 Gapix Copilot")
        user_email = st.session_state.get('user_email', 'unknown_user')
        
        # 🟢 BADLAV 1: Check karo ki kya session mein kisi DOOSRE user ki chat toh nahi?
        # Agar user badal gaya hai, toh purani messages clear karo
        if "current_chat_user" not in st.session_state or st.session_state.current_chat_user != user_email:
            st.session_state.current_chat_user = user_email # Naya user set karo
            
            # Database se sirf is user ki history uthao
            db_history = get_user_chat_history(user_email)
            if db_history:
                st.session_state.messages = [{"role": row[0], "content": row[1]} for row in db_history]
            else:
                st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me about career advice."}]
        chat_box = st.container(height=500)
        for m in st.session_state.messages:
            with chat_box.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            add_chat_message(user_email, "user", prompt)
            with chat_box.chat_message("user"): st.markdown(prompt)

            with st.spinner("Thinking..."):
                try:
                    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://gapix.ai", "X-Title": "Gapix AI"}
                    payload = {"model": SELECTED_MODEL, "messages": [{"role": "system", "content": "You are Gapix Copilot, an elite AI career strategist."}, {"role": "user", "content": prompt}]}
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload)).json()
                    reply = response['choices'][0]['message']['content']
                except Exception as e: reply = f"Error: {e}"
            
            with chat_box.chat_message("assistant"): st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            add_chat_message(user_email, "assistant", reply)

# ==========================================
# 🏠 MAIN APP LOGIC
# ==========================================
def show_dashboard():
    with st.sidebar:
        # --- 1. PROFILE SECTION (Professional Card) ---
        user_email = st.session_state.get('user_email', 'User')
        role = st.session_state.get('user_role')
        
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px;'>
                <p style='margin: 0; color: #94a3b8; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;'>Logged in as</p>
                <h4 style='margin: 5px 0 8px 0; color: #f8fafc; font-size: 15px; overflow: hidden; text-overflow: ellipsis;'>👤 {user_email}</h4>
            </div>
        """, unsafe_allow_html=True)
        
        # --- 2. STATUS BADGE ---
        if role == 'admin':
            st.markdown("<div style='text-align: center;'><span style='background: #064e3b; color: #34d399; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; border: 1px solid #059669; display: inline-block;'>🛡️ System Admin</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center;'><span style='background: #1e3a8a; color: #60a5fa; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; border: 1px solid #2563eb; display: inline-block;'>🔵 Standard Agent</span></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # --- 3. NAVIGATION SECTION ---
        st.markdown("<p style='color: #64748b; font-size: 11px; font-weight: bold; margin-bottom: 5px; letter-spacing: 0.5px;'>MAIN NAVIGATION</p>", unsafe_allow_html=True)
        
        nav_options = ["AI Dashboard"]
        if role == "admin":
            nav_options.append("🛡️ Admin Console")
            
        # Navigation ko clean dikhane ke liye label hide kiya hai
        choice = st.radio("Navigation", nav_options, label_visibility="collapsed")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # --- 4. SECURE LOGOUT ---
        if st.button("Sign Out", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = ""
            st.session_state['user_role'] = ""
            st.rerun()

    # --- ROUTING LOGIC (Sidebar ke bahar) ---
    if choice == "AI Dashboard":
        render_ai_dashboard()
        
    elif choice == "🛡️ Admin Console":
        st.title("🛡️ Enterprise Admin Console")
        st.markdown("---")
        tab1, tab2 = st.tabs(["👤 User Directory", "💬 Chat Intelligence Logs"])
        
        with tab1:
            user_data = view_all_users()
            if user_data:
                df = pd.DataFrame(user_data, columns=["Username", "Email", "Role"])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"Total Active Agents: {len(user_data)}")
            else:
                st.warning("No users found in the secure database.")
                
        with tab2:
            chat_data = view_all_chats()
            if chat_data:
                df = pd.DataFrame(chat_data, columns=["User Email", "Sender", "Message", "Time"])
                selected_user = st.selectbox("🎯 Filter Logs by Agent", ["All Systems"] + list(df["User Email"].unique()))
                
                display_df = df if selected_user == "All Systems" else df[df["User Email"] == selected_user]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No chat logs recorded yet.")

def main():
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    if st.session_state['logged_in']:
        show_dashboard()
    else:
        st.markdown("<h1 style='text-align: center; color: #6366f1;'>🚀 Welcome to Gapix AI</h1>", unsafe_allow_html=True)
        auth_col1, auth_col2, auth_col3 = st.columns([1, 1.5, 1])
        with auth_col2:
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
            with tab1:
                log_email = st.text_input("Email").lower().strip()
                log_pass = st.text_input("Password", type="password")
                if st.button("Access Dashboard", use_container_width=True):
                    result = login_user(log_email, make_hashes(log_pass))
                    if result:
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = log_email
                        st.session_state['user_role'] = result[0][3]
                        st.rerun()
                    else: st.error("Invalid credentials.")
        with tab2:
                st.subheader("📝 Register Agent")
                new_user = st.text_input("Full Name")
                new_email = st.text_input("Email Address").lower().strip()
                new_pass = st.text_input("Create Password", type="password")

                if st.button("Create Account", use_container_width=True):
                    if new_user and new_email and new_pass:
                        # 1. Admin Email Check
                        try:
                            master_email = st.secrets["MASTER_ADMIN_EMAIL"].lower().strip()
                        except:
                            master_email = "milan@gapix.com" 

                        # 2. Role Assignment
                        if new_email == master_email:
                            role = "admin"
                        else:
                            role = "user"

                        # 3. Database Entry
                        add_user(new_user, new_email, make_hashes(new_pass), role)
                        
                        # 4. Success Message & Effects
                        st.success(f"✅ Account Created! Role assigned: {role.upper()}")
                        
                        # 🎈 SABKE LIYE BALLOONS (Condition hata di hai)
                        st.balloons()
                        
                    else:
                        st.warning("⚠️ Please fill all fields.")
            

# --- Ye hamesha file ke end mein rahega ---
if __name__ == "__main__":
    main()