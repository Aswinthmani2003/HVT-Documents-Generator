import streamlit as st
from docx import Document
from datetime import datetime
import os
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
import uuid
import tempfile
import subprocess
from pathlib import Path

# Conditional import for Windows
import platform
if platform.system() == "Windows":
    import pythoncom

PROPOSAL_CONFIG = {
    "Manychats + CRM Automation - 550 USD": {
        "template": "HVT Proposal - AI Automations.docx",
        "special_fields": [("VDate", "<<")],
        "team_type": "hvt_ai"
    },
    "Manychats + CRM Automation - Custom Price": {
        "template": "HVT Proposal - AI Automations - Custom Price.docx",
        "special_fields": [("VDate", "<<")],
        "team_type": "hvt_ai_custom_price"
    },
    "Internship Offer Letter": {
        "template": "Offer Letter.docx",
        "special_fields": [],
        "team_type": "offer_letter"
    }
}

def convert_docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX to PDF using LibreOffice"""
    try:
        result = subprocess.run(
            ['unoconv', '-f', 'pdf', '-o', str(pdf_path.parent), str(docx_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Conversion failed: {e.stderr.decode()}")
        return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def apply_formatting(new_run, original_run):
    """Copy formatting from original run to new run"""
    if original_run.font.name:
        new_run.font.name = original_run.font.name
        new_run._element.rPr.rFonts.set(qn('w:eastAsia'), original_run.font.name)
    if original_run.font.size:
        new_run.font.size = original_run.font.size
    if original_run.font.color.rgb:
        new_run.font.color.rgb = original_run.font.color.rgb
    new_run.bold = original_run.bold
    new_run.italic = original_run.italic

def replace_in_paragraph(para, placeholders):
    """Enhanced paragraph replacement with style preservation"""
    original_runs = para.runs
    if not original_runs:
        return

    full_text = "".join([run.text for run in original_runs])
    modified = any(ph in full_text for ph in placeholders)

    if not modified:
        return

    for ph, value in placeholders.items():
        full_text = full_text.replace(ph, str(value))

    for run in original_runs:
        run.text = ""

    current_pos = 0
    for start, end, original_run in [
        (i, i+len(run.text), run) 
        for i, run in enumerate(original_runs)
    ]:
        if current_pos >= len(full_text):
            break

        segment = full_text[current_pos:current_pos+len(original_run.text)]
        original_run.text = segment
        apply_formatting(original_run, original_run)
        current_pos += len(segment)

    if current_pos < len(full_text):
        new_run = para.add_run(full_text[current_pos:])
        apply_formatting(new_run, original_runs[-1])

def replace_and_format(doc, placeholders):
    """Process entire document"""
    for para in doc.paragraphs:
        replace_in_paragraph(para, placeholders)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.tables:
                    for nested_table in cell.tables:
                        for nested_row in nested_table.rows:
                            for nested_cell in nested_row.cells:
                                for para in nested_cell.paragraphs:
                                    replace_in_paragraph(para, placeholders)
                for para in cell.paragraphs:
                    replace_in_paragraph(para, placeholders)
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    return doc

def get_hvt_ai_team_details():
    """Collect team composition details"""
    st.subheader("Team Composition")
    team_roles = {
        "Project Manager": "P1",
        "Frontend Developers": "F1",
        "UI/UX Members": "U1",
        "AI/ML Developers": "A1",
        "Business Analyst": "B1",
        "AWS Developer": "AD1",
        "Backend Developers": "BD1",
        "System Architect": "S1"
    }
    team_details = {}
    cols = st.columns(2)

    for idx, (role, placeholder) in enumerate(team_roles.items()):
        with cols[idx % 2]:
            count = st.number_input(
                f"{role} Count:",
                min_value=0,
                step=1,
                key=f"hvt_team_{placeholder}"
            )
            team_details[f"<<{placeholder}>>"] = str(count)
    return team_details

def validate_phone_number(country, phone_number):
    """Validate phone number format"""
    if country.lower() == "india":
        return phone_number.startswith("+91")
    return phone_number.startswith("+1")

def generate_document():
    st.title("Document Generator Pro")
    base_dir = os.path.join(os.getcwd(), "templates")

    selected_proposal = st.selectbox("Select Document", list(PROPOSAL_CONFIG.keys()))
    config = PROPOSAL_CONFIG[selected_proposal]
    template_path = os.path.join(base_dir, config["template"])

    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = {}

    placeholders = {}
    if selected_proposal == "Internship Offer Letter":
        st.subheader("Candidate Information")
        placeholders.update({
            "<<E-Name>>": st.text_input("Candidate Name:"),
            "<<Job>>": st.selectbox("Job Role", ["UI UX", "AI Automations", "Software Developer", "Sales"]),
            "<<S-Date>>": st.date_input("Start Date").strftime("%d %B, %Y"),
            "<<Stipend>>": f"{st.number_input('Stipend (₹)', min_value=0):,}",
            "<<Months>>": st.number_input("Duration (Months)", min_value=1),
            "<<Date>>": datetime.today().strftime("%d %B, %Y")
        })
    else:
        st.subheader("Client Details")
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name:")
            client_email = st.text_input("Email:")
        with col2:
            country = st.text_input("Country:")
            client_number = st.text_input("Phone Number:")

        st.subheader("Date Information")
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            date_field = st.date_input("Proposal Date", datetime.today())
        with date_col2:
            validation_date = st.date_input("Validation Date", datetime.today())

        placeholders.update({
            "<<Client Name>>": client_name,
            "<<Client Email>>": client_email,
            "<<Client Number>>": client_number,
            "<<Country>>": country,
            "<<Date>>": date_field.strftime("%d %B, %Y"),
            "<<D-Date>>": date_field.strftime("%d %B, %Y"),
            "<<VDate>>": validation_date.strftime("%d-%m-%Y")
        })

        if "hvt_ai" in config["team_type"]:
            placeholders.update(get_hvt_ai_team_details())

        if "custom_price" in config["team_type"]:
            st.subheader("Pricing Details")
            pricing = {
                "<<P01>>": st.number_input("Manychats Setup (USD)", min_value=0),
                "<<P02>>": st.number_input("Make Automations (USD)", min_value=0),
                "<<A-Price>>": st.number_input("Annual Maintenance (USD)", min_value=0)
            }
            placeholders.update(pricing)
            placeholders["<<T-Price>>"] = f"{sum(pricing.values()):,}"

    if st.button("Generate Documents"):
        if selected_proposal != "Internship Offer Letter":
            if not validate_phone_number(placeholders["<<Country>>"], placeholders["<<Client Number>>"]):
                st.error("Invalid phone number format for selected country")
                return

        unique_id = uuid.uuid4().hex[:8]
        base_name = f"{selected_proposal.replace(' ', '_')}_{unique_id}"
        doc_filename = f"{base_name}.docx"
        pdf_filename = f"{base_name}.pdf"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                doc = Document(template_path)
                doc = replace_and_format(doc, placeholders)
                doc_path = os.path.join(temp_dir, doc_filename)
                doc.save(doc_path)

                pdf_path = os.path.join(temp_dir, pdf_filename)
                
                # Start unoserver process
                uno_process = subprocess.Popen(["unoserver", "--port", "2002"])
                
                try:
                    if not convert_docx_to_pdf(doc_path, pdf_path):
                        st.error("PDF conversion failed")
                        st.stop()
                finally:
                    uno_process.terminate()
                    uno_process.wait()

                # Store files in session state
                with open(doc_path, "rb") as f:
                    st.session_state.generated_files['doc'] = f.read()
                with open(pdf_path, "rb") as f:
                    st.session_state.generated_files['pdf'] = f.read()
                st.session_state.generated_files['doc_name'] = doc_filename
                st.session_state.generated_files['pdf_name'] = pdf_filename

                st.success("Documents generated successfully!")

        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
            if platform.system() == "Windows":
                pythoncom.CoUninitialize()

    if 'doc' in st.session_state.generated_files:
        st.markdown("---")
        st.subheader("Download Documents")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Word Document",
                data=st.session_state.generated_files['doc'],
                file_name=st.session_state.generated_files['doc_name'],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        with col2:
            st.download_button(
                label="Download PDF Document",
                data=st.session_state.generated_files['pdf'],
                file_name=st.session_state.generated_files['pdf_name'],
                mime="application/pdf"
            )

if __name__ == "__main__":
    generate_document()
