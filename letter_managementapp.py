import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")

# ================= LOGO (CENTER TOP) =================
if os.path.exists("uploads/images.png"):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("uploads/images.png", width=220)

st.markdown("<h2 style='text-align:center'>📁 Nidaamka Maareynta Waraaqaha</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Is-dhaafsiga waraaqaha waaxyaha xafiiska dakhliga</p>", unsafe_allow_html=True)
st.markdown("---")

# ================= FILE PATHS =================
WARAQAHA_FILE = "waraaqaha.csv"
PASSWORDS_FILE = "passwords.csv"

# ================= DEFAULT PASSWORDS =================
if not os.path.exists(PASSWORDS_FILE):
    waaxyo = [
        "Xafiiska Wasiirka", "Wasiir Ku-xigeenka 1aad", "Wasiir Ku-xigeenka 2aad",
        "Wasiir Ku-xigeenka 3aad", "Secretory", "Waaxda Auditka",
        "Waaxda ICT", "Waaxda HRM", "Waaxda Public Relation",
        "Arkiviya-1", "Arkiviya-2"
    ]
    pd.DataFrame({
        "waaxda": waaxyo,
        "password": ["Admin2100"] * len(waaxyo)
    }).to_csv(PASSWORDS_FILE, index=False)

# ================= LOAD PASSWORDS =================
df_passwords = pd.read_csv(PASSWORDS_FILE)
waaxyo_passwords = dict(zip(df_passwords["waaxda"], df_passwords["password"]))

# ================= ADMIN =================
ADMIN_USER = "Admin"
ADMIN_PASS = "Admin2100"

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

# ================= LOGIN =================
if st.session_state.user is None:
    st.subheader("🔐 Login")
    role = st.radio("Nooca Isticmaalaha", ["Waax", "Admin"])

    if role == "Waax":
        waax = st.selectbox("Dooro Waaxda", list(waaxyo_passwords.keys()))
        pwd = st.text_input("Password", type="password")
        if st.button("Gali"):
            if pwd == waaxyo_passwords.get(waax):
                st.session_state.user = waax
                st.session_state.is_admin = False
                st.experimental_rerun()
            else:
                st.error("❌ Password khaldan")

    else:
        u = st.text_input("Admin Username")
        p = st.text_input("Admin Password", type="password")
        if st.button("Gali Admin"):
            if u == ADMIN_USER and p == ADMIN_PASS:
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

    # ================= LOAD WARAQAHA =================
    if os.path.exists(WARAQAHA_FILE):
        df = pd.read_csv(WARAQAHA_FILE)
    else:
        df = pd.DataFrame(columns=[
            "Ka_socota", "Loogu_talagalay", "Cinwaan", "Taariikh", "Files"
        ])

    # ================= 3 MAALIN KEYDIN =================
    df["Taariikh"] = pd.to_datetime(df["Taariikh"], errors="coerce")
    maanta = pd.Timestamp.today()
    df = df[df["Taariikh"] >= (maanta - pd.Timedelta(days=3))]
    df.to_csv(WARAQAHA_FILE, index=False)

    # ================= DIR WARAQ =================
    st.subheader("📤 Dir Waraaq")
    cinwaan = st.text_input("Cinwaanka Waraaqda")
    loo = st.selectbox("Loogu talagalay", [w for w in waaxyo_passwords if w != user])

    files = st.file_uploader(
        "Ku dar waraaqo (multiple files)",
        accept_multiple_files=True,
        type=["pdf", "docx", "xlsx", "csv"]
    )

    if st.button("📨 Dir"):
        if not files:
            st.warning("Fadlan ugu yaraan hal file ku dar")
        else:
            saved_files = []
            for f in files:
                encoded = base64.b64encode(f.read()).decode()
                saved_files.append({"name": f.name, "data": encoded})

            new_row = {
                "Ka_socota": user,
                "Loogu_talagalay": loo,
                "Cinwaan": cinwaan,
                "Taariikh": datetime.now(),
                "Files": base64.b64encode(str(saved_files).encode()).decode()
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(WARAQAHA_FILE, index=False)
            st.success("✅ Waraaqda waa la diray")

    # ================= VIEW WARAQAHA =================
    st.subheader("📥 Waraaqaha La Helay")
    view_df = df if is_admin else df[df["Loogu_talagalay"] == user]
    st.dataframe(view_df[["Ka_socota", "Cinwaan", "Taariikh"]])

    # ================= DOWNLOAD FILES =================
    for i, row in view_df.iterrows():
        files = eval(base64.b64decode(row["Files"]).decode())
        st.markdown(f"**📄 {row['Cinwaan']}**")
        for f in files:
            st.download_button(
                label=f"⬇️ {f['name']}",
                data=base64.b64decode(f["data"]),
                file_name=f["name"],
                key=f"{i}_{f['name']}"
            )

    # ================= CHANGE PASSWORD =================
    if not is_admin:
        st.subheader("🔒 Badal Password")
        old = st.text_input("Password Hore", type="password")
        new = st.text_input("Password Cusub", type="password")
        confirm = st.text_input("Ku celi Password-ka", type="password")

        if st.button("Badal Password"):
            if old != waaxyo_passwords.get(user):
                st.error("Password hore khaldan")
            elif new != confirm:
                st.error("Password-yadu isma mid aha")
            else:
                df_passwords.loc[df_passwords["waaxda"] == user, "password"] = new
                df_passwords.to_csv(PASSWORDS_FILE, index=False)
                st.success("✅ Password waa la badalay")

    # ================= LOGOUT =================
    if st.button("🚪 Ka Bax"):
        st.session_state.clear()
        st.experimental_rerun()
