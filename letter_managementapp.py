import streamlit as st
from sqlalchemy import create_engine, text
import os
import base64
from datetime import datetime, timedelta
import pandas as pd

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

# ================= DATABASE CONNECTION =================
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# ================= CREATE TABLES =================
with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS passwords (
        waaxda TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS waraaqaha (
        id SERIAL PRIMARY KEY,
        ka_socota TEXT,
        loogu_talagalay TEXT,
        cinwaan TEXT,
        taariikh TIMESTAMP,
        files TEXT
    )
    """))

# ================= DEFAULT PASSWORDS =================
waaxyo = [
    "Xafiiska Wasiirka", "Wasiir Ku-xigeenka 1aad", "Wasiir Ku-xigeenka 2aad",
    "Wasiir Ku-xigeenka 3aad", "Secretory", "Waaxda Auditka",
    "Waaxda ICT", "Waaxda HRM", "Waaxda Public Relation",
    "Arkiviya-1", "Arkiviya-2"
]

with engine.begin() as conn:
    for w in waaxyo:
        conn.execute(text("""
            INSERT INTO passwords (waaxda, password)
            VALUES (:waaxda, :pwd)
            ON CONFLICT (waaxda) DO NOTHING
        """), {"waaxda": w, "pwd": "Admin2100"})

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
        with engine.begin() as conn:
            result = conn.execute(text("SELECT waaxda FROM passwords"))
            waaxyo_passwords = [r[0] for r in result.fetchall()]

        waax = st.selectbox("Dooro Waaxda", waaxyo_passwords)
        pwd = st.text_input("Password", type="password")
        if st.button("Gali"):
            with engine.begin() as conn:
                result = conn.execute(text("SELECT password FROM passwords WHERE waaxda=:w"), {"w": waax})
                real_pwd = result.fetchone()
                if real_pwd and pwd == real_pwd[0]:
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
    if is_admin:
        query = "SELECT * FROM waraaqaha ORDER BY taariikh DESC"
        df = pd.read_sql(query, engine)
    else:
        three_days_ago = datetime.now() - timedelta(days=3)
        query = text("""
            SELECT * FROM waraaqaha
            WHERE loogu_talagalay=:user AND taariikh>=:date
            ORDER BY taariikh DESC
        """)
        df = pd.read_sql(query, engine, params={"user": user, "date": three_days_ago})

    # ================= DIR WARAQ =================
    st.subheader("📤 Dir Waraaq")
    cinwaan = st.text_input("Cinwaanka Waraaqda")
    loo = st.selectbox("Loogu talagalay", [w for w in waaxyo if w != user])

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

            files_encoded = base64.b64encode(str(saved_files).encode()).decode()

            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO waraaqaha (ka_socota, loogu_talagalay, cinwaan, taariikh, files)
                    VALUES (:ks, :lt, :cin, :ta, :files)
                """), {
                    "ks": user,
                    "lt": loo,
                    "cin": cinwaan,
                    "ta": datetime.now(),
                    "files": files_encoded
                })
            st.success("✅ Waraaqda waa la diray")

    # ================= VIEW WARAQAHA =================
    st.subheader("📥 Waraaqaha La Helay")
    if not df.empty:
        st.dataframe(df[["ka_socota", "cinwaan", "taariikh"]])

        # ================= DOWNLOAD FILES =================
        for i, row in df.iterrows():
            files_list = eval(base64.b64decode(row["files"]).decode())
            st.markdown(f"**📄 {row['cinwaan']}**")
            for f in files_list:
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
            with engine.begin() as conn:
                result = conn.execute(text("SELECT password FROM passwords WHERE waaxda=:w"), {"w": user})
                real_pwd = result.fetchone()[0]

                if old != real_pwd:
                    st.error("Password hore khaldan")
                elif new != confirm:
                    st.error("Password-yadu isma mid aha")
                else:
                    conn.execute(text("UPDATE passwords SET password=:p WHERE waaxda=:w"),
                                 {"p": new, "w": user})
                    st.success("✅ Password waa la badalay")

    # ================= LOGOUT =================
    if st.button("🚪 Ka Bax"):
        st.session_state.clear()
        st.experimental_rerun()
