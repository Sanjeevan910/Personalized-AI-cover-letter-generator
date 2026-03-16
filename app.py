import streamlit as st
import datetime
import uuid
from config import JOB_FILE_TYPES
from utils import extract_text_from_file, generate_cover_letter_api, extract_job_details

st.set_page_config(page_title="AI Cover Letter Generator", page_icon="🤖", layout="wide")

with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- State Management ---
if 'chats' not in st.session_state:
    st.session_state.chats = []
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def create_new_chat():
    st.session_state.current_chat_id = None
    st.session_state.uploader_key += 1 

def delete_current_chat():
    if st.session_state.current_chat_id:
        st.session_state.chats = [c for c in st.session_state.chats if c['id'] != st.session_state.current_chat_id]
        st.session_state.current_chat_id = None
        st.rerun()

def load_chat(chat_id):
    st.session_state.current_chat_id = chat_id

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🛠️ Controls")
    if st.button("➕ New Chat", help="Start a new application"):
        create_new_chat()
    
    st.divider()
    
    st.markdown("### 📂 History")
    
    delete_id = None
    
    for chat in reversed(st.session_state.chats):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            label = f"{chat['company']}"
            sub = f"{chat['role']}"
            if st.button(f"{label}\n{sub}", key=f"load_{chat['id']}", use_container_width=True):
                load_chat(chat['id'])
        with col2:
            if st.button(":material/delete:", key=f"del_{chat['id']}", help="Delete"):
                delete_id = chat['id']
                
    if delete_id:
        st.session_state.chats = [c for c in st.session_state.chats if c['id'] != delete_id]
        if st.session_state.current_chat_id == delete_id:
            st.session_state.current_chat_id = None
        st.rerun()

# --- Main Content ---
current_chat = next((c for c in st.session_state.chats if c['id'] == st.session_state.current_chat_id), None)

st.title("💼 Personalized Cover Letter Generator")

col_input, col_preview = st.columns([1, 1.2])

with col_input:
    st.markdown("### 📝 Application Details")
    
    # Auto-fill Section
    with st.expander("✨ Import Job Details from File", expanded=False):
        st.markdown("""
**✅ Supported file types:**
`PDF` · `DOCX` · `DOC` · `TXT` · `PNG` · `JPG` · `JPEG` · `WEBP` · `HTML` · `JSON` · `CSV` · `XLSX` · `PPTX` · `EML` · `MSG`

*Upload a job posting, offer letter, screenshot, email, spreadsheet, or any document containing job details.*
        """)
        uploaded_poster = st.file_uploader(
            "Upload Job File",
            type=JOB_FILE_TYPES,
            key="poster_uploader",
            help="Supported: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG, WEBP, HTML, JSON, CSV, XLSX, PPTX, EML, MSG"
        )
        if uploaded_poster:
            if st.button("Extract Details"):
                with st.spinner("Extracting info..."):
                    details = extract_job_details(uploaded_poster)
                    if details:
                        st.session_state.extracted_company = details.get('company', '')
                        st.session_state.extracted_role = details.get('role', '')
                        st.session_state.extracted_jd = details.get('description', '')
                        st.success("Details extracted! Review below.")
                        st.rerun()

    with st.form("cover_letter_form"):
        # Determine default values based on extraction or loaded chat
        default_role = st.session_state.get('extracted_role', current_chat['role'] if current_chat else "")
        default_company = st.session_state.get('extracted_company', current_chat['company'] if current_chat else "")
        default_jd = st.session_state.get('extracted_jd', current_chat['jd'] if current_chat else "")
        
        role = st.text_input("Target Role", placeholder="e.g. Senior Product Manager", value=default_role)
        company = st.text_input("Company Name", placeholder="e.g. Google", value=default_company)
        
        job_description = st.text_area("Job Description", placeholder="Paste the JD here...", height=150, value=default_jd)
        uploaded_file = st.file_uploader("Resume Source", type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'webp'], help="Upload your CV to extract skills.", key=f"uploader_{st.session_state.uploader_key}")
        
        st.markdown("---")
        max_words = st.slider("Max Word Count", min_value=100, max_value=1000, value=300, step=50, help="Approximate length of the cover letter.")
        
        submitted = st.form_submit_button("Generate Cover Letter", use_container_width=True)


    
with col_preview:
    if current_chat and 'output' in current_chat:
        st.markdown("### 📄 Cover Letter")
        
        st.code(current_chat['output'], language=None)
        
        st.download_button("💾 Download .txt", data=current_chat['output'], file_name=f"Cover_Letter_{current_chat['company']}.txt")
    else:
        st.info("👈 Fill in the details on the left to generate your document.")
        st.markdown("""
        <div style="text-align: center; color: #aaa; margin-top: 30px;">
            <h4>Ready to write?</h4>
            <p>Upload your resume and paste the job description to get started.</p>
        </div>
        """, unsafe_allow_html=True)

if submitted:
    if not company or not role or not job_description:
        st.error("Please provide Company, Role, and Job Description.")
    else:
        resume_text = ""
        if uploaded_file:
            resume_text = extract_text_from_file(uploaded_file)
        elif current_chat and 'resume_text' in current_chat:
            resume_text = current_chat['resume_text']
        else:
            st.error("Please upload a resume context.")
            st.stop()
            
        with st.spinner("Analyzing profile and drafting letter..."):
            generated_letter = generate_cover_letter_api(company, role, resume_text, job_description, max_words)
            
            if generated_letter:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
                new_chat = {
                    'id': str(uuid.uuid4()),
                    'company': company,
                    'role': role,
                    'resume_text': resume_text,
                    'jd': job_description,
                    'output': generated_letter,
                    'date': timestamp
                }
                
                if current_chat:
                    current_chat.update(new_chat)
                    current_chat['id'] = st.session_state.current_chat_id 
                else:
                    st.session_state.chats.append(new_chat)
                    st.session_state.current_chat_id = new_chat['id']
                
                st.rerun()
