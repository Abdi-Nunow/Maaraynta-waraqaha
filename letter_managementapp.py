import streamlit as st
import pandas as pd
import io
from datetime import datetime
from docx import Document
import base64
import os

# Dejinta bogga
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("📁 Nidaamka Maareynta Waraaqaha")
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

# SESSION STATE - User-ka
if "waaxda_user" not in st.session_state:
    st.session_state.waaxda_user = None

# Haddii user-ka weli ma login-galin
if st.session_state.waaxda_user is None:
    st.subheader("🔐 Fadlan dooro waaxdaada si aad u gasho:")
    waax_user = st.selectbox("Waaxda:", waaxyo)
    if st.button("✅ Gali"):
        st.session_state.waaxda_user = waax_user
        st.rerun()

else:
    waaxda_user = st.session_state.waaxda_user
    st.success(f"👋 Waad soo dhawaatay, {waaxda_user} ✅")

    # 🔔 Notifications
    if os.path.exists("waraaqaha.csv"):
        df_all = pd.read_csv("waraaqaha.csv")
        df_user = df_all[df_all["Loogu talagalay"] == waaxda_user]
        count = df_user.shape[0]
        if count > 0:
            st.info(f"🔔 **Ogeysiis:** Waxaa kuu yaalla **{count} waraaqo** cusub.")
        else:
            st.success("✅ Waqtigan ma jiraan waraaqo cusub.")
    else:
        df_all = pd.DataFrame(columns=["Ka socota", "Loogu talagalay", "Cinwaanka", "Qoraalka", "Taariikh", "File", "FileData"])

    st.markdown("---")
    st.subheader("📤 Dir Waraaq Cusub")

    col1, col2 = st.columns(2)
    with col1:
        diraha = waaxda_user
        cinwaanka = st.text_input("Cinwaanka Waraaqda")
    with col2:
        loo_dirayo = st.selectbox("Loogu talagalay waaxda:", [w for w in waaxyo if w != diraha])
        taariikh = st.date_input("Taariikhda", value=datetime.today())

    farriin = st.text_area("Objective")
    uploaded_file = st.file_uploader("Upload Lifaaq (ikhtiyaari ah)", type=["pdf", "docx", "xlsx", "csv"])

    file_name = ""
    file_data = ""
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_data = base64.b64encode(uploaded_file.read()).decode("utf-8")

    if st.button("📨 Dir Waraaqda"):
        xog = {
            "Ka socota": diraha,
            "Loogu talagalay": loo_dirayo,
            "Cinwaanka": cinwaanka,
            "Qoraalka": farriin,
            "Taariikh": taariikh.strftime("%Y-%m-%d"),
            "File": file_name,
            "FileData": file_data
        }

        df_all = pd.concat([df_all, pd.DataFrame([xog])], ignore_index=True)
        df_all.to_csv("waraaqaha.csv", index=False)
        st.success("✅ Waraaqda waa la diray.")

    st.markdown("---")
    st.subheader("📥 Waraaqaha La Helay")
    df_helay = df_all[df_all["Loogu talagalay"] == waaxda_user]

    if not df_helay.empty:
        st.dataframe(df_helay[["Taariikh", "Ka socota", "Cinwaanka", "File"]])

        # Word Download
        doc = Document()
        doc.add_heading(f"Waraaqaha loo diray {waaxda_user}", 0)
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

        # Excel Download
        excel_buffer = io.BytesIO()
        df_helay.drop(columns=["FileData"], errors='ignore').to_excel(excel_buffer, index=False)
        st.download_button(
            label="📊 Soo Degso (Excel)",
            data=excel_buffer.getvalue(),
            file_name="waraaqaha.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Waraaqo lama helin.")

    # Bixitaanka
    st.markdown("---")
    if st.button("🚪 Bixi"):
        st.session_state.waaxda_user = None
        st.rerun()
