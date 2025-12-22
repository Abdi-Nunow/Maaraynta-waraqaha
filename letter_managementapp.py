import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")

# ================= LOGO =================
if os.path.exists("images.png"):
    st.image("images.png", width=220)

st.markdown("## 📁 Nidaamka Maareynta Waraaqaha")
st.markdown("Diridda iyo helidda warqadaha rasmiga ah (original files, multiple uploads).")

# ================= FILE PATHS =================
passwords_file = "passwords.csv"
waraaqaha_file = "waraaqaha.csv"

# ================= DEFAULT WAAXYO =================
if not os.path.exists(passwords_file):
    waaxyo = {
        "Xafiiska Wasiirka": "Admin2100",
        "Wasiir Ku-xigeenka 1aad": "Admin2100",
        "Wasiir Ku-xigeenka 2aad": "Admin2100",
        "Secretory": "Admin2100",
        "Waaxda Auditka": "Admin2100",
        "Waaxda ICT": "Admin2100",
        "Waaxda HRM": "Admin2100",
        "Arkiviya-1": "Admin2100",
        "Arkiviya-2": "Admin2100"
    }
    pd.DataFrame(waaxyo.items(), columns=["waaxda", "password"]).to_csv(passwords_file, index=False)

df_pass = pd.read_csv(passwords_file)
waax_passwords = dict(zip(df_pass.waaxda, df_pass.password))

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

# ================= LOGIN =================
if st.session_state.user is None:
    st.subheader("🔐 Login")

    role = st.radio("Nooca isticmaalaha", ["Waax", "Admin"])

    if role == "Waax":
        waax = st.selectbox("Dooro Waaxda", list(waax_passwords.keys()))
        pwd = st.text_input("Password", type="password")

        if st.button("Gali"):
            if pwd == waax_passwords.get(waax):
                st.session_state.user = waax
                st.session_state.is_admin = False
                st.experimental_rerun()
            else:
                st.error("❌ Password khaldan")

    else:
        u = st.text_input("Admin Username")
        p = st.text_input("Admin Password", type="password")

        if st.button("Gali"):
            if u == "Admin" and p == "Admin2100":
                st.session_state.user = "Admin"
                st.session_state.is_admin = True
                st.experimental_rerun()
            else:
                st.error("❌ Admin login khaldan")

# ================= MAIN APP =================
else:
    user = st.session_state.user
    is_admin = st.session_state.is_admin

    st.success(f"Ku soo dhawoow: {user}")

    if os.path.exists(waraaqaha_file):
        df = pd.read_csv(waraaqaha_file)
    else:
        df = pd.DataFrame(columns=[
            "Diary", "Ka Socota", "Loogu Talagalay",
            "Cinwaan", "Taariikh",
            "FileName", "FileData"
        ])

    # ================= SEND LETTER (MULTIPLE FILES) =================
    st.subheader("📤 Dir Warqado (Original Files – Multiple)")

    cinwaan = st.text_input("Cinwaanka Warqadda")
    loo = st.selectbox(
        "Loogu Talagalay",
        [w for w in waax_passwords.keys() if w != user]
    )

    files = st.file_uploader(
        "Dooro warqadaha rasmiga ah (PDF, Word, Excel – hal ama dhowr)",
        type=["pdf", "docx", "doc", "xlsx", "xls"],
        accept_multiple_files=True
    )

    if st.button("📨 Dir"):
        if not files:
            st.error("❌ Fadlan dooro ugu yaraan hal warqad")
        else:
            for file in files:
                diary = f"DR-{len(df)+1:05d}"
                encoded = base64.b64encode(file.read()).decode()

                new_row = {
                    "Diary": diary,
                    "Ka Socota": user,
                    "Loogu Talagalay": loo,
                    "Cinwaan": cinwaan,
                    "Taariikh": datetime.today().strftime("%Y-%m-%d"),
                    "FileName": file.name,
                    "FileData": encoded
                }

                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            df.to_csv(waraaqaha_file, index=False)
            st.success("✅ Dhammaan warqadihii waa la diray si guul ah")

    # ================= VIEW LETTERS =================
    st.subheader("📥 Waraaqaha La Helay")

    view_df = df if is_admin else df[df["Loogu Talagalay"] == user]
    st.dataframe(view_df.drop(columns=["FileData"], errors="ignore"))

    # ================= DOWNLOAD ORIGINAL FILES =================
    st.subheader("⬇️ Soo Degso Warqadaha Asalka ah")

    for i, row in view_df.iterrows():
        file_bytes = base64.b64decode(row["FileData"])
        st.download_button(
            label=f"⬇️ {row['FileName']} | {row['Diary']}",
            data=file_bytes,
            file_name=row["FileName"],
            key=f"dl_{i}"
        )

    # ================= CHANGE PASSWORD (WAAX) =================
    if not is_admin:
        st.subheader("🔒 Bedel Password-ka")

        old_pass = st.text_input("Password-kii hore", type="password")
        new_pass = st.text_input("Password cusub", type="password")
        confirm_pass = st.text_input("Ku celi password-ka cusub", type="password")

        if st.button("🔁 Bedel Password"):
            if old_pass != waax_passwords.get(user):
                st.error("❌ Password-kii hore waa khaldan")
            elif new_pass != confirm_pass:
                st.error("❌ Password-yadu isma mid aha")
            elif len(new_pass) < 6:
                st.warning("⚠️ Password-ka waa inuu ka bato 6 xaraf")
            else:
                df_pass.loc[df_pass["waaxda"] == user, "password"] = new_pass
                df_pass.to_csv(passwords_file, index=False)
                st.success("✅ Password-ka waa la beddelay")

    # ================= LOGOUT =================
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_rerun()
