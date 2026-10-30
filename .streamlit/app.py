import os
import io
import base64
import requests
import pandas as pd
import streamlit as st
from pathlib import Path
from pypdf import PdfReader

# Optional viewer component; falls back to embedded iframe if unavailable
try:
    from streamlit_pdf_viewer import pdf_viewer
    HAS_PDF_VIEWER = True
except ImportError:
    HAS_PDF_VIEWER = False

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="ChemInformatics Virtual Laboratory Pro",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Charcoal/Dark Navy & Turquoise accents
st.markdown("""
<style>
    .metric-card {
        background-color: #1c2541;
        border: 1px solid #3a506b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .turquoise-text {
        color: #00d2be;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1c2541;
        border-radius: 6px;
        color: #f0f4f8;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d2be !important;
        color: #0b132b !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: Student Credentials & Navigation
# ---------------------------------------------------------
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

with st.sidebar:
    st.markdown("## 🧪 ChemLab Pro")
    st.caption("College Virtual ChemInformatics Laboratory")
    st.markdown("---")
    
    st.markdown("### 🎓 Student Details")
    student_name = st.text_input("Student Name", value=st.session_state.get("student_name", "Student"))
    reg_number = st.text_input("Registration / Roll No.", value=st.session_state.get("reg_number", "CHEM-2026-001"))
    st.session_state["student_name"] = student_name
    st.session_state["reg_number"] = reg_number
    
    st.markdown("---")
    navigation = st.radio(
        "Navigation",
        [
            "🏠 Lab Overview",
            "📄 Repository PDFs & Reports",
            "🔍 PubChem Explorer",
            "📊 Structure-Property Analysis",
            "📝 Assessment Quiz"
        ]
    )
    st.markdown("---")
    st.caption(f"Active Session: **{student_name}** (`{reg_number}`)")

# Helper: Display PDF using base64 iframe fallback
def render_pdf_fallback(pdf_bytes: bytes, height: int = 700):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="{height}px" type="application/pdf" style="border: 1px solid #3a506b; border-radius: 8px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# ---------------------------------------------------------
# View 1: Lab Overview
# ---------------------------------------------------------
if navigation == "🏠 Lab Overview":
    st.markdown("# 🔬 ChemInformatics Virtual Laboratory Pro")
    st.markdown(f"**Welcome, {student_name} (`{reg_number}`)**")
    
    st.info(
        "This virtual lab connects computational chemical representations with experimental "
        "reports and molecular datasets retrieved live from the NCBI PubChem database."
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <span class="turquoise-text">01. PDF Lab Manuals</span>
            <p>Access experiment sheets and research documents synced directly from your GitHub repository.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <span class="turquoise-text">02. Live PubChem Integration</span>
            <p>Retrieve molecular weights, SMILES, IUPAC names, and 2D structures straight via PUG REST.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <span class="turquoise-text">03. Property Verification</span>
            <p>Compare experimental literature values against live retrieved chemical descriptors.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📚 Key Theory: Molecular Representations")
    st.markdown("""
    - **SMILES (Simplified Molecular Input Line Entry System):** Encodes 2D molecular graphs into short ASCII strings (e.g., `CC(=O)Oc1ccccc1C(=O)O` for Aspirin).
    - **InChI & InChIKey:** Standard IUPAC non-proprietary identifier providing unique digital signatures for structural uniqueness.
    - **Molecular Descriptors:** Physicochemical properties (LogP, TPSA, H-Bond donors/acceptors) governing absorption, distribution, metabolism, and excretion (ADME).
    """)

# ---------------------------------------------------------
# View 2: Repository PDFs & Reports
# ---------------------------------------------------------
elif navigation == "📄 Repository PDFs & Reports":
    st.markdown("# 📄 Repository PDF Documents & Lab Reports")
    st.markdown(
        "This section automatically reads PDF files stored in the `docs/` directory of your GitHub repository. "
        "Commit any new `.pdf` file to that folder and push to GitHub to have it appear here."
    )

    pdf_files = sorted(list(DOCS_DIR.glob("*.pdf")))

    if not pdf_files:
        st.warning("No PDF documents found in the `docs/` directory.")
        st.markdown("""
        **To add PDFs to this application:**
        1. Create a `docs` folder inside your GitHub repository.
        2. Upload your PDF files (e.g., `docs/lab_sheet.pdf`).
        3. Commit and push the changes:
           ```bash
           git add docs/
           git commit -m "Add chemistry lab PDFs"
           git push origin main
           ```
        4. Streamlit will instantly refresh and list your uploaded documents.
        """)
    else:
        file_names = [f.name for f in pdf_files]
        selected_file_name = st.selectbox("📂 Select Document from Repository:", file_names)
        selected_file_path = DOCS_DIR / selected_file_name

        with open(selected_file_path, "rb") as f:
            pdf_bytes = f.read()

        tab_view, tab_text, tab_meta = st.tabs(["🖥️ PDF Viewer", "🔎 Text Extraction & Search", "ℹ️ Document Details"])

        with tab_view:
            st.download_button(
                label=f"⬇️ Download {selected_file_name}",
                data=pdf_bytes,
                file_name=selected_file_name,
                mime="application/pdf"
            )
            if HAS_PDF_VIEWER:
                pdf_viewer(input=pdf_bytes, width=800)
            else:
                render_pdf_fallback(pdf_bytes, height=750)

        with tab_text:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            st.write(f"**Total Pages:** {total_pages}")
            
            search_query = st.text_input("Search keyword in document (e.g., 'Benzene', 'Titration', 'SMILES'):")
            if search_query:
                matches = []
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if search_query.lower() in text.lower():
                        matches.append(idx + 1)
                if matches:
                    st.success(f"Keyword '{search_query}' found on page(s): {', '.join(map(str, matches))}")
                else:
                    st.warning(f"No occurrences of '{search_query}' found.")

            selected_page = st.number_input("Display Page Text:", min_value=1, max_value=max(total_pages, 1), value=1)
            extracted_text = reader.pages[selected_page - 1].extract_text()
            st.text_area(f"Page {selected_page} Content", extracted_text, height=350)

        with tab_meta:
            st.markdown(f"- **Filename:** `{selected_file_name}`")
            st.markdown(f"- **File Size:** `{len(pdf_bytes) / 1024:.2f} KB`")
            st.markdown(f"- **Repository Path:** `docs/{selected_file_name}`")

# ---------------------------------------------------------
# View 3: PubChem Explorer
# ---------------------------------------------------------
elif navigation == "🔍 PubChem Explorer":
    st.markdown("# 🔍 Live PubChem PUG REST Explorer")
    st.caption("Live queries via https://pubchem.ncbi.nlm.nih.gov/rest/pug/")
    
    query = st.text_input("Enter Compound Name, CID, or SMILES:", value="Aspirin")
    
    if st.button("Query Database", type="primary"):
        with st.spinner("Fetching data from NCBI PubChem..."):
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query.strip()}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES,InChIKey/JSON"
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    props = data["PropertyTable"]["Properties"][0]
                    cid = props["CID"]
                    
                    st.success(f"Found record for: **{query}** (CID: {cid})")
                    
                    col_img, col_data = st.columns([1, 2])
                    with col_img:
                        img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
                        st.image(img_url, caption=f"2D Structure (CID {cid})", use_container_width=True)
                    
                    with col_data:
                        st.markdown(f"**Formula:** `{props.get('MolecularFormula', 'N/A')}`")
                        st.markdown(f"**Molecular Weight:** `{props.get('MolecularWeight', 'N/A')} g/mol`")
                        st.markdown(f"**IUPAC Name:** {props.get('IUPACName', 'N/A')}")
                        st.markdown(f"**Canonical SMILES:** `{props.get('CanonicalSMILES', 'N/A')}`")
                        st.markdown(f"**InChIKey:** `{props.get('InChIKey', 'N/A')}`")
                        st.markdown(f"[🔗 View full entry on NCBI PubChem](https://pubchem.ncbi.nlm.nih.gov/compound/{cid})")
                else:
                    st.error(f"No compound found for '{query}'. Please check the spelling or format.")
            except requests.exceptions.RequestException as e:
                st.error(f"API Connection error: {e}")

# ---------------------------------------------------------
# View 4: Structure-Property Analysis
# ---------------------------------------------------------
elif navigation == "📊 Structure-Property Analysis":
    st.markdown("# 📊 Structure-Property Comparison")
    st.markdown("Compare molecular weights and properties across key laboratory standards:")

    compounds = ["Ethanol", "Benzene", "Phenol", "Acetic acid", "Aspirin", "Caffeine"]
    selected_compounds = st.multiselect("Select compounds to compare:", compounds, default=["Ethanol", "Benzene", "Aspirin"])

    if selected_compounds:
        results = []
        for name in selected_compounds:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    p = r.json()["PropertyTable"]["Properties"][0]
                    results.append({
                        "Compound": name,
                        "CID": p["CID"],
                        "Formula": p.get("MolecularFormula"),
                        "MW (g/mol)": float(p.get("MolecularWeight", 0)),
                        "SMILES": p.get("CanonicalSMILES")
                    })
            except Exception:
                pass
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Compound")["MW (g/mol)"])

# ---------------------------------------------------------
# View 5: Assessment Quiz
# ---------------------------------------------------------
elif navigation == "📝 Assessment Quiz":
    st.markdown("# 📝 ChemInformatics Practical Assessment")
    st.markdown(f"**Candidate:** {student_name} | **Roll No:** `{reg_number}`")
    
    with st.form("quiz_form"):
        q1 = st.radio(
            "1. What does the acronym SMILES stand for in computational chemistry?",
            [
                "Standard Molecular Identifier Line Entry Schema",
                "Simplified Molecular Input Line Entry System",
                "Systematic Molecular Identification and Linear Encoding Scheme"
            ]
        )
        q2 = st.radio(
            "2. Which PubChem service provides automated RESTful web endpoints?",
            ["Entrez Direct", "PUG REST", "BioAssay FTP"]
        )
        submitted = st.form_submit_button("Submit Assessment")
        
        if submitted:
            score = 0
            if q1 == "Simplified Molecular Input Line Entry System":
                score += 1
            if q2 == "PUG REST":
                score += 1
            st.success(f"Final Score: {score} / 2")
            st.balloons()
