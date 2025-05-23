import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
import base64

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

uploaded_file = st.file_uploader("Ku Shub Waraaqda (PDF, DOCX, XLSX, CSV)", type=["pdf", "docx", "xlsx", "csv"])

# Diyaarinta faylka la dirayo
if uploaded_file is not None:
    if not os.path.exists("files"):
        os.makedirs("files")
    
    saved_filename = f"{taariikh.strftime('%Y%m%d')}_{diraha.replace(' ', '_')}_{uploaded_file.name}"
    saved_path = os.path.join("files", saved_filename)

    # Faylka keydi
    with open(saved_path, "wb") as f:
        f.write(uploaded_file.read())

    if st.button("✅ Dir Waraaqda"):
        xog = {
            "Ka socota": diraha,
            "Loogu talagalay": loo_dirayo,
            "Cinwaanka": cinwaanka,
            "Taariikh": taariikh.strftime("%Y-%m-%d"),
            "FilePath": saved_path,
            "FileName": uploaded_file.name
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
    st.dataframe(df_helay[["Taariikh", "Ka socota", "Cinwaanka", "FileName"]])

    for _, row in df_helay.iterrows():
        if pd.notna(row["FilePath"]) and os.path.exists(row["FilePath"]):
            with open(row["FilePath"], "rb") as file:
                st.download_button(
                    label=f"⬇️ Soo Degso: {row['FileName']}",
                    data=file.read(),
                    file_name=row["FileName"],
                    mime="application/octet-stream"
                )

except FileNotFoundError:
    st.info("Waraaqo lama helin.")
