import streamlit as st
import pandas as pd
import io
from datetime import datetime
from docx import Document
import base64
import os

# Dejinta bogga
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("Nidaamka Maareynta Waraaqaha")
st.markdown("Waxaa loogu talagalay in waaxyaha kala duwan ee xafiiska dakhli ay isku diraan waraaqaha.")

# Liiska waaxyaha
waaxyo = [
    "Xafiiska Wasiirka",
    "Wasiir Ku-xigeenka 1aad",
    "Wasiir Ku-xigeenka 2aad",
    "Wasiir Ku-xigeenka 3aad",
    "secratory",
    "Waaxda Xadaynta",
    "Waaxda Auditka",
    "Waaxda Adeega Shacabka",
    "Waaxda ICT",
    "Waaxda Public Relation",
    "Waaxda HRM",
    "Waaxda Wacyigalinta"
]

# Foomka dirista waraaqda
st.subheader("📤 Dir Waraaq Cusub")
col1, col2 = st.columns(2)
with col1:
    diraha = st.selectbox("Ka socota waaxda:", waaxyo)
    cinwaanka = st.text_input("Cinwaanka Waraaqda")
with col2:
    loo_dirayo = st.selectbox("Loogu talagalay waaxda:", [w for w in waaxyo if w != diraha])
    taariikh = st.date_input("Taariikhda", value=datetime.today())

farriin = st.text_area("Qoraalka Waraaqda")
uploaded_file = st.file_uploader("Upload Lifaaq (ikhtiyaari ah)", type=["pdf", "docx", "xlsx", "csv"])

# File-ka lifaaqa u keydi base64
file_name = ""
file_data = ""
if uploaded_file is not None:
    file_name = uploaded_file.name
    file_data = base64.b64encode(uploaded_file.read()).decode("utf-8")

# Dirista
if st.button("✅ Dir Waraaqda"):
    xog = {
        "Ka socota": diraha,
        "Loogu talagalay": loo_dirayo,
        "Cinwaanka": cinwaanka,
        "Qoraalka": farriin,
        "Taariikh": taariikh.strftime("%Y-%m-%d"),
        "File": file_name,
        "FileData": file_data
    }

    try:
        df = pd.read_csv("waraaqaha.csv")
        df = pd.concat([df, pd.DataFrame([xog])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([xog])

    df.to_csv("waraaqaha.csv", index=False)
    st.success("✅ Waraaqda waa la diray")

# Waraaqaha la helay
st.subheader("📥 Waraaqaha La Helay")
try:
    df = pd.read_csv("waraaqaha.csv")
    waaxdaada = st.selectbox("Dooro waaxdaada si aad u eegto waraaqaha", waaxyo)
    df_helay = df[df["Loogu talagalay"] == waaxdaada]
    st.dataframe(df_helay[["Taariikh", "Ka socota", "Cinwaanka", "File"]])

    # Soo degso Word
    doc = Document()
    doc.add_heading(f"Waraaqaha loo diray {waaxdaada}", 0)
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

    # Soo degso Excel
    excel_buffer = io.BytesIO()
    df_helay.drop(columns=["FileData"], errors='ignore').to_excel(excel_buffer, index=False)
    st.download_button(
        label="📊 Soo Degso (Excel)",
        data=excel_buffer.getvalue(),
        file_name="waraaqaha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

except FileNotFoundError:
    st.info("Waraaqo lama helin.")
