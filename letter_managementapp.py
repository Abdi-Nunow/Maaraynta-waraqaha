import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from docx import Document
import base64

# Dejinta bogga
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("Nidaamka Maareynta Waraaqaha")
st.markdown("Waxaa loogu talagalay in waaxyaha kala duwan ee xafiiska dakhli ay isku diraan waraaqaha.")

# Liiska waaxyaha
waaxyo = [
    "Xafiiska Wasiirka", "Wasiir Ku-xigeenka 1aad", "Wasiir Ku-xigeenka 2aad",
    "Wasiir Ku-xigeenka 3aad", "secratory", "Waaxda Xadaynta", "Waaxda Auditka",
    "Waaxda Adeega Shacabka", "Waaxda ICT", "Waaxda Public Relation",
    "Waaxda HRM", "Waaxda Wacyigalinta"
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

farriin = st.text_area("Qoraal Kooban (Ikhtiyaari)")
uploaded_file = st.file_uploader("📎 Upload Waraaqda (faylka la dirayo)", type=["pdf", "docx", "xlsx", "csv"])

# Dirista
if st.button("✅ Dir Waraaqda"):
    if uploaded_file is None:
        st.error("❌ Fadlan soo geli faylka warqadda la dirayo.")
    else:
        # Faylka keydi si magac gaar ah ugu noqdo
        uploads_folder = "uploads"
        os.makedirs(uploads_folder, exist_ok=True)
        safe_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
        file_path = os.path.join(uploads_folder, safe_filename)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        xog = {
            "Ka socota": diraha,
            "Loogu talagalay": loo_dirayo,
            "Cinwaanka": cinwaanka,
            "Qoraalka": farriin,
            "Taariikh": taariikh.strftime("%Y-%m-%d"),
            "File": uploaded_file.name,
            "FilePath": file_path
        }

        try:
            df = pd.read_csv("waraaqaha.csv")
            df = pd.concat([df, pd.DataFrame([xog])], ignore_index=True)
        except FileNotFoundError:
            df = pd.DataFrame([xog])

        df.to_csv("waraaqaha.csv", index=False)
        st.success("✅ Waraaqda iyo lifaaqeedii waa la diray")

# Waraaqaha la helay
st.subheader("📥 Waraaqaha La Helay")
try:
    df = pd.read_csv("waraaqaha.csv")
    waaxdaada = st.selectbox("Dooro waaxdaada si aad u eegto waraaqaha", waaxyo)
    df_helay = df[df["Loogu talagalay"] == waaxdaada]

    # Tus xogta guud
    st.dataframe(df_helay[["Taariikh", "Ka socota", "Cinwaanka", "File"]])

    # Soo dejiso fayl kasta
    for _, row in df_helay.iterrows():
        st.markdown(f"**📄 {row['Cinwaanka']}**")
        st.markdown(f"- **Taariikh:** {row['Taariikh']}")
        st.markdown(f"- **Ka Socota:** {row['Ka socota']}")
        st.markdown(f"- **Qoraal Kooban:** {row['Qoraalka'] if pd.notna(row['Qoraalka']) else '(Ma jiro)'}")
        if os.path.exists(row["FilePath"]):
            with open(row["FilePath"], "rb") as file:
                st.download_button(
                    label=f"⬇️ Soo Degso Faylka: {row['File']}",
                    data=file.read(),
                    file_name=row["File"],
                    mime="application/octet-stream"
                )
        st.markdown("---")

    # Soo Degso dhammaan waraaqaha (Excel)
    excel_buffer = io.BytesIO()
    df_helay.drop(columns=["FilePath"], errors='ignore').to_excel(excel_buffer, index=False)
    st.download_button(
        label="📊 Soo Degso Dhammaan (Excel)",
        data=excel_buffer.getvalue(),
        file_name="waraaqaha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

except FileNotFoundError:
    st.info("Waraaqo lama helin.")
