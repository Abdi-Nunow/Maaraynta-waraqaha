import streamlit as st
import pandas as pd
import io
from datetime import datetime
from docx import Document
import os

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("📁 Nidaamka Maareynta Waraaqaha")
st.markdown("Waxaa loogu talagalay in waaxyaha kala duwan ee xafiiska dakhliga ay isku diraan waraaqaha.")

# ===== FILE PATHS =====
passwords_file = "passwords.csv"
waraaqaha_file = "waraaqaha.csv"
storage_dir = "storage"
os.makedirs(storage_dir, exist_ok=True)

# ===== DEFAULT PASSWORDS =====
if not os.path.exists(passwords_file):
    default_passwords = {
        "Xafiiska Wasiirka": "Admin2100",
        "Wasiir Ku-xigeenka 1aad": "Admin2100",
        "Wasiir Ku-xigeenka 2aad": "Admin2100",
        "Wasiir Ku-xigeenka 3aad": "Admin2100",
        "Secratory": "Admin2100",
        "Waaxda Xadaynta": "Admin2100",
        "Waaxda Auditka": "Admin2100",
        "Waaxda Adeega Shacabka": "Admin2100",
        "Waaxda ICT": "Admin2100",
        "Waaxda Public Relation": "Admin2100",
        "Waaxda HRM": "Admin2100",
        "Waaxda Wacyigalinta": "Admin2100"
    }
    pd.DataFrame(default_passwords.items(), columns=["waaxda", "password"]).to_csv(passwords_file, index=False)

# ===== LOAD PASSWORDS =====
df_passwords = pd.read_csv(passwords_file)
waaxyo_passwords = dict(zip(df_passwords.waaxda, df_passwords.password))

# ===== ADMIN =====
admin_user = "Admin"
admin_password = "Admin2100"

# ===== SESSION =====
if "waaxda_user" not in st.session_state:
    st.session_state.waaxda_user = None
    st.session_state.is_admin = False

# ===== LOGIN =====
if st.session_state.waaxda_user is None:
    st.subheader("🔐 Fadlan gal nidaamka")
    nooca = st.radio("Nooca isticmaalaha:", ["Waax", "Admin"])

    if nooca == "Waax":
        waax_user = st.selectbox("Waaxda:", list(waaxyo_passwords.keys()))
        password = st.text_input("Password", type="password")
        if st.button("✅ Gali"):
            if password == waaxyo_passwords.get(waax_user):
                st.session_state.waaxda_user = waax_user
                st.session_state.is_admin = False
                st.experimental_rerun()
            else:
                st.error("Password-ka waa khaldanyahay ❌")
    else:
        admin_input = st.text_input("Admin username")
        admin_pass = st.text_input("Admin password", type="password")
        if st.button("✅ Gali"):
            if admin_input == admin_user and admin_pass == admin_password:
                st.session_state.waaxda_user = "Admin"
                st.session_state.is_admin = True
                st.experimental_rerun()
            else:
                st.error("Xogta Admin waa khaldantahay ❌")

# ===== MAIN APP =====
else:
    waaxda_user = st.session_state.waaxda_user
    is_admin = st.session_state.is_admin
    st.success(f"👋 Ku soo dhawoow {waaxda_user}")

    # ===== LOAD LETTERS =====
    if os.path.exists(waraaqaha_file):
        df_all = pd.read_csv(waraaqaha_file)
    else:
        df_all = pd.DataFrame(columns=[
            "Ka socota", "Loogu talagalay", "Cinwaanka",
            "Qoraalka", "Taariikh", "File", "FileData"
        ])

    # ===== SEND LETTER =====
    st.subheader("📤 Dir Waraaq Cusub")
    col1, col2 = st.columns(2)
    with col1:
        cinwaanka = st.text_input("Cinwaanka Waraaqda")
    with col2:
        loo_dirayo = st.selectbox(
            "Loogu talagalay:",
            [w for w in waaxyo_passwords if w != waaxda_user]
        )

    farriin = st.text_area("Objective")
    uploaded_file = st.file_uploader("Lifaaq (ikhtiyaari)", type=["pdf", "docx", "xlsx", "csv"])

    file_name, file_path = "", ""
    if uploaded_file:
        file_name = uploaded_file.name
        waax_folder = os.path.join(storage_dir, loo_dirayo)
        os.makedirs(waax_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{file_name}"
        file_path = os.path.join(waax_folder, safe_name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

    if st.button("📨 Dir"):
        new_row = {
            "Ka socota": waaxda_user,
            "Loogu talagalay": loo_dirayo,
            "Cinwaanka": cinwaanka,
            "Qoraalka": farriin,
            "Taariikh": datetime.today().strftime("%Y-%m-%d"),
            "File": file_name,
            "FileData": file_path
        }
        df_all = pd.concat([df_all, pd.DataFrame([new_row])], ignore_index=True)
        df_all.to_csv(waraaqaha_file, index=False)
        st.success("Waraaqda waa la diray ✅")

    # ===== VIEW LETTERS =====
    st.subheader("📥 Waraaqaha La Helay")
    df_view = df_all if is_admin else df_all[df_all["Loogu talagalay"] == waaxda_user]
    st.dataframe(df_view.drop(columns=["FileData"], errors="ignore"))

    # ===== DOWNLOAD FILES =====
    if not df_view.empty:
        for _, row in df_view.iterrows():
            if pd.notna(row["FileData"]) and row["FileData"] != "":
                if os.path.exists(row["FileData"]):
                    with open(row["FileData"], "rb") as f:
                        st.download_button(
                            label=f"📎 Soo degso {row['File']}",
                            data=f,
                            file_name=row["File"]
                        )

    # ===== CHANGE PASSWORD =====
    if not is_admin:
        st.subheader("🔒 Bedel Password-ka")
        old_pass = st.text_input("Password-kii Hore", type="password")
        new_pass = st.text_input("Password Cusub", type="password")
        confirm_pass = st.text_input("Mar kale geli password-ka cusub", type="password")

        if st.button("📅 Badal Password-ka"):
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

    # ===== LOGOUT =====
    if st.button("🚪 Bixi"):
        st.session_state.clear()
        st.experimental_rerun()
