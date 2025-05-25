import streamlit as st
import pandas as pd
import io
from docx import Document
from fpdf import FPDF

# Tusaale ahaan DataFrame-ka guud
# Waa in 'df' horey loo dejiyey, tusaale ahaan ka yimid CSV ama DB
# Halkan waa tusaale fudud:
df = pd.DataFrame([
    {"Taariikh": "2025-05-01", "Ka socota": "ICT", "Loogu talagalay": "HRM", "Cinwaanka": "Warbixin", "Qoraalka": "Tani waa warbixin", "File": "warbixin.pdf"},
    {"Taariikh": "2025-05-02", "Ka socota": "Audit", "Loogu talagalay": "ICT", "Cinwaanka": "Ogaal", "Qoraalka": None, "File": ""},
])

# Qiyaasaha user-ka
is_admin = st.session_state.get("is_admin", False)
waaxda_user = st.session_state.get("waaxda_user", "ICT")

# Samee df_helay
if is_admin:
    df_helay = df.copy()
else:
    df_helay = df[df["Loogu talagalay"] == waaxda_user]

# Haddii waraaqo la helay
if not df_helay.empty:

    # ========== WORD ==========
    doc = Document()
    doc.add_heading(f"Waraaqaha {'dhammaan waaxyaha' if is_admin else 'loo diray ' + waaxda_user}", 0)
    for _, row in df_helay.iterrows():
        doc.add_paragraph(f"Taariikh: {row['Taariikh']}")
        doc.add_paragraph(f"Ka Socota: {row['Ka socota']}")
        doc.add_paragraph(f"Cinwaan: {row['Cinwaanka']}", style='List Bullet')
        doc.add_paragraph(str(row['Qoraalka']) if pd.notna(row['Qoraalka']) else "(Qoraal ma jiro)")
        if pd.notna(row.get("File")) and row["File"]:
            doc.add_paragraph(f"Lifaaq: {row['File']}")
        doc.add_paragraph("---")

    word_buffer = io.BytesIO()
    doc.save(word_buffer)
    st.download_button(
        label="📄 Soo Degso (Word)",
        data=word_buffer.getvalue(),
        file_name="waraaqaha.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # ========== EXCEL ==========
    excel_buffer = io.BytesIO()
    df_helay.drop(columns=["FileData"], errors='ignore').to_excel(excel_buffer, index=False)
    st.download_button(
        label="📊 Soo Degso (Excel)",
        data=excel_buffer.getvalue(),
        file_name="waraaqaha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ========== PDF ==========
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Waraaqaha {'dhammaan waaxyaha' if is_admin else 'loo diray ' + waaxda_user}", ln=True, align='C')

    for _, row in df_helay.iterrows():
        pdf.cell(200, 10, txt=f"Taariikh: {row['Taariikh']}", ln=True)
        pdf.cell(200, 10, txt=f"Ka Socota: {row['Ka socota']}", ln=True)
        pdf.cell(200, 10, txt=f"Cinwaan: {row['Cinwaanka']}", ln=True)
        qoraal = str(row['Qoraalka']) if pd.notna(row['Qoraalka']) else "(Qoraal ma jiro)"
        pdf.multi_cell(0, 10, txt=f"Qoraal: {qoraal}")
        if pd.notna(row.get("File")) and row["File"]:
            pdf.cell(200, 10, txt=f"Lifaaq: {row['File']}", ln=True)
        pdf.cell(200, 10, txt="---", ln=True)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    st.download_button(
        label="🖨️ Soo Degso (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="waraaqaha.pdf",
        mime="application/pdf"
    )

else:
    st.warning("Waraaqo lama helin.")
