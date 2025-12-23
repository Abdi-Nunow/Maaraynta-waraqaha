import streamlit as st
from sqlalchemy import create_engine, text
import os
import base64
from datetime import datetime, timedelta

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

# ================= DATABASE =================
DATABASE_URL = os.environ.get("DATABASE_URL")  # Ku dar DATABASE_URL env variable Render
engine = create_engine(DATABASE_URL, echo=False)

# ================= CREATE TABLES =================
with engine.connect() as conn:
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
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS passwords (
        waaxda TEXT PRIMARY KEY,
        password TEXT
    )
    """))

# ================= DEFAULT PASSWORDS =================
waaxyo = [
    "Xafiiska Wasiirka","Wasiir Ku-xigeenka 1aad","Wasiir Ku-xigeenka 2aad",
    "Wasiir Ku-xigeenka 3aad","Secretory","Waaxda Auditka",
    "Waaxda ICT","Waaxda HRM","Waaxda Public Relation",
    "Arkiviya-1","Arkiviya-2"
]

with engine.connect() as conn:
    for w in waaxyo:
        conn.execute(text("""
            INSERT INTO passwords (waaxda, password)
            VALUES (:waax, :pwd)
            ON CONFLICT (waaxda) DO NOTHING
        """), {"waax": w, "pwd": "Admin2100"})

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
        with engine.connect() as conn:
            waaxyo_list = [r[0] for r in conn.execute(text("SELECT waaxda FROM passwords"))]
        waax = st.selectbox("Dooro Waaxda", waaxyo_list)
        pwd = st.text_input("Password", type="password")
        if st.button("Gali"):
            with engine.connect() as conn:
                real = conn.execute(text("SELECT password FROM passwords WHERE waaxda=:w"), {"w": waax}).fetchone()
            if real and pwd == real[0]:
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

    # ================= DIR WARAQ =================
    st.subheader("📤 Dir Waraaq")
    cinwaan = st.text_input("Cinwaanka Waraaqda")
    loo = st.selectbox("Loogu talagalay", [w for w in waaxyo if w != user])

    files = st.file_uploader(
        "Ku dar waraaqo (multiple files)",
        accept_multiple_files=True,
        type=["pdf","docx","xlsx","csv"]
    )

    if st.button("📨 Dir"):
        if not files:
            st.warning("Fadlan ugu yaraan hal file ku dar")
        else:
            saved_files = []
            for f in files:
                encoded = base64.b64encode(f.read()).decode()
                saved_files.append({"name": f.name, "data": encoded})

            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO waraaqaha
                    (ka_socota, loogu_talagalay, cinwaan, taariikh, files)
                    VALUES (:ka, :loo, :cin, :taa, :files)
                """), {
                    "ka": user,
                    "loo": loo,
                    "cin": cinwaan,
                    "taa": datetime.now(),
                    "files": base64.b64encode(str(saved_files).encode()).decode()
                })
            st.success("✅ Waraaqda waa la diray")

    # ================= VIEW WARAQAHA =================
    st.subheader("📥 Waraaqaha La Helay")
    with engine.connect() as conn:
        if is_admin:
            rows = conn.execute(text("SELECT * FROM waraaqaha ORDER BY taariikh DESC")).fetchall()
        else:
            three_days_ago = datetime.now() - timedelta(days=3)
            rows = conn.execute(text("""
                SELECT * FROM waraaqaha
                WHERE loogu_talagalay=:user AND taariikh >= :d
                ORDER BY taariikh DESC
            """), {"user": user, "d": three_days_ago}).fetchall()

    for r in rows:
        st.markdown(f"**📄 {r.cinwaan}** ({r.ka_socota}) - {r.taariikh}")
        files = eval(base64.b64decode(r.files).decode())
        for f in files:
            st.download_button(
                label=f"⬇️ {f['name']}",
                data=base64.b64decode(f["data"]),
                file_name=f["name"],
                key=f"{r.id}_{f['name']}"
            )

    # ================= CHANGE PASSWORD =================
    if not is_admin:
        st.subheader("🔒 Badal Password")
        old = st.text_input("Password Hore", type="password")
        new = st.text_input("Password Cusub", type="password")
        confirm = st.text_input("Ku celi Password-ka", type="password")

        if st.button("Badal Password"):
            with engine.connect() as conn:
                real = conn.execute(text("SELECT password FROM passwords WHERE waaxda=:w"), {"w": user}).fetchone()
            if old != real[0]:
                st.error("Password hore khaldan")
            elif new != confirm:
                st.error("Password-yadu isma mid aha")
            else:
                with engine.connect() as conn:
                    conn.execute(text("UPDATE passwords SET password=:p WHERE waaxda=:w"), {"p": new, "w": user})
                st.success("✅ Password waa la badalay")

    # ================= LOGOUT =================
    if st.button("🚪 Ka Bax"):
        st.session_state.clear()
        st.experimental_rerun()
