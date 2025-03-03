import streamlit as st
import os
import uuid
import tempfile
import subprocess
import time
from datetime import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

# Set base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Conditional import for Windows
import platform
if platform.system() == "Windows":
    import pythoncom
    pythoncom.CoInitialize()

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

def convert_to_pdf(doc_path, pdf_path):
    """Convert DOCX to PDF using LibreOffice"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', 
                 os.path.dirname(pdf_path), doc_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
            # Rename output file to desired filename
            temp_pdf = os.path.splitext(doc_path)[0] + '.pdf'
            if os.path.exists(temp_pdf):
                os.rename(temp_pdf, pdf_path)
                return True
            return False
        except subprocess.CalledProcessError as e:
            if attempt == max_retries - 1:
                error_msg = e.stderr.decode() if e.stderr else str(e)
                st.error(f"PDF conversion failed: {error_msg}")
                return False
            time.sleep(2)
        except Exception as e:
            st.error(f"Conversion error: {str(e)}")
            return False
    return False

def render_template(template_name, context):
    template = jinja_env.get_template(template_name)
    return template.render(context)

def generate_pdf(html_content, output_path):
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'quiet': ''
    }
    pdfkit.from_string(html_content, output_path, options=options)

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
    """Enhanced paragraph replacement with style preservation and table handling"""
    original_runs = para.runs
    if not original_runs:
        return

    # Build list of (text, run) tuples
    run_map = []
    text_length = 0
    for run in original_runs:
        run_text = run.text
        run_map.append((text_length, text_length + len(run_text), run))
        text_length += len(run_text)

    # Build full text and check for replacements
    full_text = "".join([run.text for run in original_runs])
    modified = any(ph in full_text for ph in placeholders.keys())

    if not modified:
        return

    # Perform replacements
    for ph, value in placeholders.items():
        full_text = full_text.replace(ph, str(value))

    # Clear existing runs
    for run in original_runs:
        run.text = ""

    # Rebuild runs with original formatting
    current_pos = 0
    for start, end, original_run in run_map:
        if current_pos >= len(full_text):
            break

        remaining_length = len(full_text) - current_pos
        segment_length = min(len(original_run.text), remaining_length)
        segment = full_text[current_pos:current_pos + segment_length]
        
        if segment:
            original_run.text = segment
            apply_formatting(original_run, original_run)
            current_pos += segment_length

    if current_pos < len(full_text):
        new_run = para.add_run(full_text[current_pos:])
        apply_formatting(new_run, original_runs[-1])

def replace_and_format(doc, placeholders):
    """Enhanced replacement with table cell handling"""
    # Process paragraphs
    for para in doc.paragraphs:
        replace_in_paragraph(para, placeholders)

    # Process tables
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
    """Collect team composition details for HVT AI proposal"""
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
            team_details[f"{placeholder}"] = str(count)
    return team_details

def main():
    st.title("Document Generator")

    selected_proposal = st.selectbox("Select Document", list(PROPOSAL_CONFIG.keys()))
    config = PROPOSAL_CONFIG[selected_proposal]
    
    context = {}
    
    if selected_proposal == "Internship Offer Letter":
        context.update({
            "candidate_name": st.text_input("Candidate Name:"),
            "job_role": st.selectbox("Job Role", ["UI UX", "AI Automations", "Software Developer", "Sales"]),
            "start_date": st.date_input("Starting Date").strftime("%d %B, %Y"),
            "stipend": f"{st.number_input('Stipend Amount (Rs.)', min_value=0):,}",
            "months": st.number_input("Duration (Months)", min_value=1)
        })
    else:
        col1, col2 = st.columns(2)
        with col1:
            context.update({
                "client_name": st.text_input("Client Name:"),
                "client_email": st.text_input("Client Email:")
            })
        with col2:
            context.update({
                "country": st.text_input("Country:"),
                "client_number": st.text_input("Client Number:")
            })
        
        if config["team_type"] == "hvt_ai":
            context["team"] = get_hvt_ai_team_details()
        elif config["team_type"] == "hvt_ai_custom_price":
            context.update({
                "team": get_hvt_ai_team_details(),
                "pricing": get_project_pricing_details()
            })

    context["date"] = datetime.today().strftime("%d %B, %Y")

    if st.button("Generate Document"):
        try:
            html_content = render_template(config["template"], context)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_filename = f"document_{uuid.uuid4()}.pdf"
                pdf_path = os.path.join(temp_dir, pdf_filename)
                
                generate_pdf(html_content, pdf_path)
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                st.session_state['pdf_bytes'] = pdf_bytes
                st.session_state['pdf_filename'] = pdf_filename

        except Exception as e:
            st.error(f"Error generating document: {str(e)}")

    if 'pdf_bytes' in st.session_state:
        st.download_button(
            label="📄 Download PDF Document",
            data=st.session_state['pdf_bytes'],
            file_name=st.session_state['pdf_filename'],
            mime="application/pdf"
        )

def get_project_pricing_details():
    """Collect project pricing details for custom price proposal"""
    st.subheader("Project Pricing Details")
    pricing_fields = {
        "Manychats Setup": "P01",
        "Make Automations": "P02",
        "Annual Maintenance": "A-Price"
    }
    pricing_details = {}
    cols = st.columns(2)

    for idx, (field, placeholder) in enumerate(pricing_fields.items()):
        with cols[idx % 2]:
            value = st.number_input(
                f"{field} (USD):",
                min_value=0,
                step=1,
                format="%d",
                key=f"project_pricing_{placeholder}"
            )
            formatted_value = f"{value:,}"
            pricing_details[f"<<{placeholder}>>"] = formatted_value
    return pricing_details

def validate_phone_number(country, phone_number):
    """Validate phone number based on country"""
    if country.lower() == "india":
        if not phone_number.startswith("+91"):
            return False
    else:
        if not phone_number.startswith("+1"):
            return False
    return True

def generate_document():
    st.title("Offer Letter Generator")
    base_dir = TEMPLATES_DIR

    selected_proposal = st.selectbox("Select Document", list(PROPOSAL_CONFIG.keys()))
    config = PROPOSAL_CONFIG[selected_proposal]
    template_path = os.path.join(base_dir, config["template"])

    # Conditional fields collection
    if selected_proposal == "Internship Offer Letter":
        candidate_name = st.text_input("Candidate Name:")
        job_role = st.selectbox("Job Role", ["UI UX", "AI Automations", "Software Developer", "Sales"])
        start_date = st.date_input("Starting Date")
        stipend = st.number_input("Stipend Amount (Rs.)", min_value=0)
        months = st.number_input("Duration (Months)", min_value=1)
    else:
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name:")
            client_email = st.text_input("Client Email:")
        with col2:
            country = st.text_input("Country:")
            client_number = st.text_input("Client Number:")
            if client_number and country:
                if not validate_phone_number(country, client_number):
                    st.error(f"Phone number for {country} should start with {'+91' if country.lower() == 'india' else '+1'}")

    date_field = st.date_input("Date:", datetime.today())

    # Additional fields for non-offer letters
    special_data = {}
    team_data = {}
    pricing_data = {}
    
    if selected_proposal != "Internship Offer Letter":
        st.subheader("Additional Details")
        vdate = st.date_input("Proposal Validity Until:")
        special_data["<<VDate>>"] = vdate.strftime("%d-%m-%Y")

        if config["team_type"] == "hvt_ai":
            team_data = get_hvt_ai_team_details()
        elif config["team_type"] == "hvt_ai_custom_price":
            team_data = get_hvt_ai_team_details()
            pricing_data = get_project_pricing_details()

    # Build placeholders
    placeholders = {}
    if selected_proposal == "Internship Offer Letter":
        placeholders = {
            "<<Date>>": date_field.strftime("%d %B, %Y"),
            "<<E-Name>>": candidate_name,
            "<<Job>>": job_role,
            "<<Stipend>>": f"{stipend:,}",
            "<<S-Date>>": start_date.strftime("%d %B, %Y"),
            "<<S-date>>": start_date.strftime("%d-%m-%Y"),
            "<<Months>>": months
        }
    else:
        placeholders = {
            "<<Client Name>>": client_name,
            "<<Client Email>>": client_email,
            "<<Client Number>>": client_number,
            "<<Date>>": date_field.strftime("%d %B, %Y"),
            "<<D-Date>>": date_field.strftime("%d %B, %Y"),
            "<<Country>>": country
        }
        placeholders.update(team_data)
        if config["team_type"] == "hvt_ai_custom_price":
            placeholders.update(pricing_data)
            p01 = int(pricing_data.get("<<P01>>", "0").replace(",", ""))
            p02 = int(pricing_data.get("<<P02>>", "0").replace(",", ""))
            placeholders["<<T-Price>>"] = f"{(p01 + p02):,}"
        placeholders.update(special_data)

    if st.button("Generate Document"):
        error = False
        if selected_proposal != "Internship Offer Letter":
            if client_number and country and not validate_phone_number(country, client_number):
                st.error(f"Invalid phone number format for {country} should start with {'+91' if country.lower() == 'india' else '+1'}.")
                error = True
        
        if not error:
            formatted_date = date_field.strftime("%d-%b-%Y")
            unique_id = str(uuid.uuid4())[:8]

            # Generate filenames without spaces
            if config["team_type"] == "offer_letter":
                clean_name = candidate_name.replace(' ', '_')
                doc_filename = f"Offer_Letter_{clean_name}_{formatted_date}_{unique_id}.docx"
                pdf_filename = f"Offer_Letter_{clean_name}_{formatted_date}_{unique_id}.pdf"
            else:
                clean_name = client_name.replace(' ', '_')
                doc_filename = f"Proposal_{clean_name}_{formatted_date}_{unique_id}.docx"
                pdf_filename = f"Proposal_{clean_name}_{formatted_date}_{unique_id}.pdf"

            with tempfile.TemporaryDirectory() as temp_dir:
                doc_path = os.path.join(temp_dir, doc_filename)
                pdf_path = os.path.join(temp_dir, pdf_filename)

                # Process document
                doc = Document(template_path)
                doc = replace_and_format(doc, placeholders)
                doc.save(doc_path)

                # Convert to PDF
                if convert_to_pdf(doc_path, pdf_path):
                    # Store files in session state
                    with open(doc_path, "rb") as f:
                        st.session_state['doc_bytes'] = f.read()
                    with open(pdf_path, "rb") as f:
                        st.session_state['pdf_bytes'] = f.read()
                    st.session_state['doc_filename'] = doc_filename
                    st.session_state['pdf_filename'] = pdf_filename
                else:
                    st.error("Failed to generate PDF document")

    # Download buttons
    if 'doc_bytes' in st.session_state and 'pdf_bytes' in st.session_state:
        st.markdown("---")
        st.subheader("Download Documents")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download Word Document",
                data=st.session_state['doc_bytes'],
                file_name=st.session_state['doc_filename'],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        with col2:
            st.download_button(
                label="📑 Download PDF Document",
                data=st.session_state['pdf_bytes'],
                file_name=st.session_state['pdf_filename'],
                mime="application/pdf"
            )
if __name__ == "__main__":
    generate_document()
