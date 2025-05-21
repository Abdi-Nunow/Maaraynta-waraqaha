import streamlit as st
import pandas as pd
import io
from datetime import datetime
from docx import Document

# Dejinta bogga
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")

st.title("AI Nidaamka Maareynta Waraaqaha")
st.markdown("""
Waxaa loogu talagalay in waaxyaha kala duwan ee xafiiska dakhli ay isku diraan waraaqaha.
""")

# Liiska waaxyaha
waaxyo = [
    "Xafiiska Wasiirka",
    "Wasiir Ku-xigeenka 1aad",
    "Wasiir Ku-xigeenka 2aad",
    "Wasiir Ku-xigeenka 3aad",
    "Waaxda Xadaynta",
    "Waaxda Auditka",
    "Waaxda Adeega Shacabka",
    "Waaxda ICT",
    "Waaxda Public Relation",
    "Waaxda HRM",
    "Waaxda Wacyigalinta"
]

# Foomka dirista waraaqda
st.subheader("Dir Waraaq Cusub")
col1, col2 = st.columns(2)
with col1:
    diraha = st.selectbox("Ka socota waaxda:", waaxyo)
    cinwaanka = st.text_input("Cinwaanka Waraaqda")
with col2:
    loo_dirayo = st.selectbox("Loogu talagalay waaxda:", [w for w in waaxyo if w != diraha])
    taariikh = st.date_input("Taariikhda", value=datetime.today())

farriin = st.text_area("Qoraalka Waraaqda")

if st.button("Dir Waraaqda"):
    xog = {
        "Ka socota": diraha,
        "Loogu talagalay": loo_dirayo,
        "Cinwaanka": cinwaanka,
        "Qoraalka": farriin,
        "Taariikh": taariikh.strftime("%Y-%m-%d")
    }

    try:
        df = pd.read_csv("waraaqaha.csv")
        df = pd.concat([df, pd.DataFrame([xog])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([xog])

    df.to_csv("waraaqaha.csv", index=False)
    st.success("Waraaqda waa la diray ✅")

st.subheader("Waraaqaha La Helay")

# Warqadaha la helay
try:
    df = pd.read_csv("waraaqaha.csv")
    waaxdaada = st.selectbox("Dooro waaxdaada si aad u eegto waraaqaha", waaxyo)
    df_helay = df[df["Loogu talagalay"] == waaxdaada]
    st.dataframe(df_helay)

    # Download as Word
    doc = Document()
    doc.add_heading(f"Waraaqaha loo diray {waaxdaada}", 0)

    for _, row in df_helay.iterrows():
        doc.add_paragraph(f"Taariikh: {row['Taariikh']}")
        doc.add_paragraph(f"Ka Socota: {row['Ka socota']}")
        doc.add_paragraph(f"Cinwaan: {row['Cinwaanka']}", style='List Bullet')
        doc.add_paragraph(row['Qoraalka'])
        doc.add_paragraph("---")

    word_buffer = io.BytesIO()
    doc.save(word_buffer)

    st.download_button(
        label="📄 Soo Degso Waraaqaha (Word)",
        data=word_buffer.getvalue(),
        file_name="waraaqaha.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Download as Excel
    excel_buffer = io.BytesIO()
    df_helay.to_excel(excel_buffer, index=False)
    st.download_button(
        label="📊 Soo Degso Waraaqaha (Excel)",
        data=excel_buffer.getvalue(),
        file_name="waraaqaha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

except FileNotFoundError:
    st.info("Waraaqo lama helin.")
