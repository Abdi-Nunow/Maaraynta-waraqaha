import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from sqlalchemy import create_engine, text

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")

# ================= DATABASE =================
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# ================= INIT DATABASE =================
def init_db():
    with engine.begin() as conn:
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

def insert_default_passwords():
    waaxyo = [
        "Xafiiska Wasiirka", "Wasiir Ku-xigeenka 1aad", "Wasiir Ku-xigeenka 2aad",
        "Wasiir Ku-xigeenka 3aad", "Secretory", "Waaxda Auditka",
        "Waaxda ICT", "Waaxda HRM", "Waaxda Public Relation",
        "Arkiviya-1", "Arkiviya-2"
    ]
    with engine.begin() as conn:
        for w in waaxyo:
            conn.execute(
                text("""
                INSERT INTO passwords (waaxda, password)
                VALUES (:w, :p)
                ON CONFLICT (waaxda) DO NOTHING
                """),
                {"w": w, "p": "Admin2100"}
            )

def load_passwords():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM passwords", conn)
    return dict(zip(df["waaxda"], df["password"]))

def insert_waraq(data):
    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO waraaqaha
            (ka_socota, loogu_talagalay, cinwaan, taariikh, files)
            VALUES (:k, :l, :c, :t, :f)
            """),
            data
        )

def load_waraaqaha():
    with engine.connect() as conn:
        df = pd.read_sql("""
            SELECT * FROM waraaqaha
            WHERE taariikh >= NOW() - INTERVAL '3 days'
            ORDER BY taariikh DESC
        """, conn)
    return df

# ================= INIT =================
init_db()
insert_default_passwords()
waaxyo_passwords = load_passwords()

# ================= ADMIN =================
ADMIN_USER = "Admin"
ADMIN_PASS = "Admin2100"

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

# ================= LOGO =================
if os.path.exists("uploads/images.png"):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("uploads/images.png", width=220)

st.markdown("<h2 style='text-align:center'>📁 Nidaamka Maareynta Waraaqaha</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Is-dhaafsiga waraaqaha waaxyaha xafiiska dakhliga</p>", unsafe_allow_html=True)
st.markdown("---")

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

    df = load_waraaqaha()

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
                saved_files.append({
                    "name": f.name,
                    "data": base64.b64encode(f.read()).decode()
                })

            insert_waraq({
                "k": user,
                "l": loo,
                "c": cinwaan,
                "t": datetime.now(),
                "f": base64.b64encode(str(saved_files).encode()).decode()
            })

            st.success("✅ Waraaqda waa la diray")

    # ================= VIEW WARAQAHA =================
    st.subheader("📥 Waraaqaha La Helay")
    view_df = df if is_admin else df[df["loogu_talagalay"] == user]
    st.dataframe(view_df[["ka_socota", "cinwaan", "taariikh"]])

    # ================= DOWNLOAD FILES =================
    for _, row in view_df.iterrows():
        files = eval(base64.b64decode(row["files"]).decode())
        st.markdown(f"**📄 {row['cinwaan']}**")

        for f in files:
            st.download_button(
                label=f"⬇️ {f['name']}",
                data=base64.b64decode(f["data"]),
                file_name=f["name"],
                key=f"{row['id']}_{f['name']}"
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
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                        UPDATE passwords
                        SET password = :p
                        WHERE waaxda = :w
                        """),
                        {"p": new, "w": user}
                    )
                st.success("✅ Password waa la badalay")

    # ================= LOGOUT =================
    if st.button("🚪 Ka Bax"):
        st.session_state.clear()
        st.experimental_rerun()
