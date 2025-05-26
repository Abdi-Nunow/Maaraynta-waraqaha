import streamlit as st
import pandas as pd
import io
from datetime import datetime
from docx import Document
import os
import shutil

# Dejinta bogga
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("📁 Nidaamka Maareynta Waraaqaha")
st.markdown("Waxaa loogu talagalay in waaxyaha kala duwan ee xafiiska dakhliga ay isku diraan waraaqaha.")

# Hubi galka uploads uu jiro
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Liiska waaxyaha iyo passwordkooda
passwords_file = "passwords.csv"
if not os.path.exists(passwords_file):
    default_passwords = {
        "Xafiiska Wasiirka": "Admin2100",
        "Wasiir Ku-xigeenka 1aad": "Admin2100",
        "Wasiir Ku-xigeenka 2aad": "Admin2100",
        "Wasiir Ku-xigeenka 3aad": "Admin2100",
        "secratory": "Admin2100",
        "Waaxda Xadaynta": "Admin2100",
        "Waaxda Auditka": "Admin2100",
        "Waaxda Adeega Shacabka": "Admin2100",
        "Waaxda ICT": "Admin2100",
        "Waaxda Public Relation": "Admin2100",
        "Waaxda HRM": "Admin2100",
        "Waaxda Wacyigalinta": "Admin2100"
    }
    pd.DataFrame(list(default_passwords.items()), columns=["waaxda", "password"]).to_csv(passwords_file, index=False)

df_passwords = pd.read_csv(passwords_file)
waaxyo_passwords = dict(zip(df_passwords.waaxda, df_passwords.password))

# Admin login
admin_user = "Admin"
admin_password = "Admin2100"

# SESSION STATE
if "waaxda_user" not in st.session_state:
    st.session_state.waaxda_user = None
    st.session_state.is_admin = False

if st.session_state.waaxda_user is None:
    st.subheader("🔐 Fadlan gal nidaamka")
    nooca = st.radio("Nooca isticmaalaha:", ["Waax", "Admin"])

    if nooca == "Waax":
        waax_user = st.selectbox("Waaxda:", list(waaxyo_passwords.keys()))
        password = st.text_input("Password", type="password")
        if st.button("✅ Gali", key="login_waax"):
            if password == waaxyo_passwords.get(waax_user):
                st.session_state.waaxda_user = waax_user
                st.session_state.is_admin = False
                st.success(f"Ku soo dhawoow, {waax_user}")
                st.experimental_rerun()
            else:
                st.error("Password-ka waa khaldanyahay ❌")
    else:
        admin_input = st.text_input("Admin username")
        admin_pass = st.text_input("Admin password", type="password")
        if st.button("✅ Gali", key="login_admin"):
            if admin_input == admin_user and admin_pass == admin_password:
                st.session_state.waaxda_user = "Admin"
                st.session_state.is_admin = True
                st.success("Ku soo dhawoow, Admin")
                st.experimental_rerun()
            else:
                st.error("Xogta Admin waa khaldantahay ❌")
else:
    waaxda_user = st.session_state.waaxda_user
    is_admin = st.session_state.is_admin
    st.success(f"👋 Kuso dhawow waaxda, {waaxda_user} ✅")

    if os.path.exists("waraaqaha.csv"):
        df_all = pd.read_csv("waraaqaha.csv")
    else:
        df_all = pd.DataFrame(columns=["Ka socota", "Loogu talagalay", "Cinwaanka", "Qoraalka", "Taariikh", "FilePath"])

    if not is_admin:
        df_user = df_all[df_all["Loogu talagalay"] == waaxda_user]
        count = df_user.shape[0]
        if count > 0:
            st.info(f"🔔 Waxaa kuu yaalla **{count} waraaqo** cusub.")
        else:
            st.success("✅ Waqtigan ma jiraan waraaqo cusub.")

    st.markdown("---")
    st.subheader("📤 Dir Waraaq Cusub")

    col1, col2 = st.columns(2)
    with col1:
        diraha = waaxda_user
        cinwaanka = st.text_input("Cinwaanka Waraaqda")
    with col2:
        loo_dirayo = st.selectbox("Loogu talagalay waaxda:", [w for w in waaxyo_passwords if w != diraha])
        taariikh = st.date_input("Taariikhda", value=datetime.today())

    farriin = st.text_area("Objective")
    uploaded_file = st.file_uploader("Upload Lifaaq (ikhtiyaari ah)", type=["pdf", "docx", "xlsx", "csv"])

    file_path = ""
    if uploaded_file:
        file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
        file_path = os.path.join(upload_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    if st.button("📨 Dir Waraaqda"):
        xog = {
            "Ka socota": diraha,
            "Loogu talagalay": loo_dirayo,
            "Cinwaanka": cinwaanka,
            "Qoraalka": farriin,
            "Taariikh": taariikh.strftime("%Y-%m-%d"),
            "FilePath": file_path
        }
        df_all = pd.concat([df_all, pd.DataFrame([xog])], ignore_index=True)
        df_all.to_csv("waraaqaha.csv", index=False)
        st.success("✅ Waraaqda waa la diray.")

    st.markdown("---")
    st.subheader("📥 Waraaqaha La Helay")

    df_helay = df_all if is_admin else df_all[df_all["Loogu talagalay"] == waaxda_user]

    if not df_helay.empty:
        display_df = df_helay.copy()
        display_df["Lifaaq"] = display_df["FilePath"].apply(lambda x: os.path.basename(x) if pd.notna(x) and x else "")
        st.dataframe(display_df[["Taariikh", "Ka socota", "Cinwaanka", "Lifaaq"]])

        for index, row in df_helay.iterrows():
            if row["FilePath"] and os.path.exists(row["FilePath"]):
                with open(row["FilePath"], "rb") as f:
                    file_bytes = f.read()
                st.download_button(
                    label=f"📥 Download: {os.path.basename(row['FilePath'])}",
                    data=file_bytes,
                    file_name=os.path.basename(row["FilePath"]),
                    mime="application/octet-stream",
                    key=f"download_{index}"
                )

        # Word Download
        doc = Document()
        doc.add_heading("Waraaqaha", 0)
        for _, row in df_helay.iterrows():
            doc.add_paragraph(f"Taariikh: {row['Taariikh']}")
            doc.add_paragraph(f"Ka Socota: {row['Ka socota']}")
            doc.add_paragraph(f"Cinwaan: {row['Cinwaanka']}", style='List Bullet')
            doc.add_paragraph(str(row['Qoraalka']) if pd.notna(row['Qoraalka']) else "(Qoraal ma jiro)")
            if pd.notna(row["FilePath"]):
                doc.add_paragraph(f"Lifaaq: {os.path.basename(row['FilePath'])}")
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

    # Password Change
    if not is_admin:
        st.markdown("---")
        st.subheader("🔒 Bedel Password-ka")
        old_pass = st.text_input("Password-kii Hore", type="password")
        new_pass = st.text_input("Password Cusub", type="password")
        confirm_pass = st.text_input("Mar kale geli password-ka cusub", type="password")
        if st.button("💾 Badal Password-ka"):
            if old_pass != waaxyo_passwords.get(waaxda_user):
                st.error("Password-kii hore waa khaldan ❌")
            elif new_pass != confirm_pass:
                st.error("Password-yada cusub isma mid aha ❌")
            elif len(new_pass) < 6:
                st.warning("Password-ka waa inuu ka bato 6 xaraf.")
            else:
                df_passwords.loc[df_passwords.waaxda == waaxda_user, "password"] = new_pass
                df_passwords.to_csv(passwords_file, index=False)
                st.success("✅ Password-ka waa la badalay si guul ah")

    # Logout
    st.markdown("---")
    if st.button("🚪 Bixi"):
        st.session_state.waaxda_user = None
        st.session_state.is_admin = False
        st.experimental_rerun()
