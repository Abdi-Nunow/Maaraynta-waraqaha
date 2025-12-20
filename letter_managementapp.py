import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

# ================= CONFIG =================
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("📁 Nidaamka Maareynta Waraaqaha")

# ================= FILES =================
passwords_file = "passwords.csv"
letters_file = "waraaqaha.csv"
storage_dir = "storage"
os.makedirs(storage_dir, exist_ok=True)

# ================= DEFAULT PASSWORDS =================
if not os.path.exists(passwords_file):
    defaults = {
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
    pd.DataFrame(defaults.items(), columns=["waaxda", "password"]).to_csv(passwords_file, index=False)

df_passwords = pd.read_csv(passwords_file)
waaxyo = dict(zip(df_passwords.waaxda, df_passwords.password))

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.is_admin = False

# ================= LOGIN =================
if st.session_state.user is None:
    st.subheader("🔐 Gal Nidaamka")
    role = st.radio("Nooca:", ["Waax", "Admin"])

    if role == "Waax":
        w = st.selectbox("Waaxda:", waaxyo.keys())
        p = st.text_input("Password", type="password")
        if st.button("Gali"):
            if p == waaxyo[w]:
                st.session_state.user = w
                st.session_state.is_admin = False
                st.experimental_rerun()
            else:
                st.error("Password khaldan")
    else:
        u = st.text_input("Admin username")
        p = st.text_input("Admin password", type="password")
        if st.button("Gali"):
            if u == "Admin" and p == "Admin2100":
                st.session_state.user = "Admin"
                st.session_state.is_admin = True
                st.experimental_rerun()
            else:
                st.error("Admin login khaldan")

# ================= MAIN =================
else:
    user = st.session_state.user
    is_admin = st.session_state.is_admin
    st.success(f"👋 Ku soo dhawoow {user}")

    # ---------- LOAD DATA ----------
    if os.path.exists(letters_file):
        df = pd.read_csv(letters_file)
    else:
        df = pd.DataFrame(columns=[
            "id", "from", "to", "title", "content",
            "date", "file", "filepath",
            "box", "archived_by"
        ])

    # ---------- SEND LETTER ----------
    st.subheader("📤 Dir Waraaq")
    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("Cinwaanka")
    with c2:
        to = st.selectbox("Loogu talagalay:", [w for w in waaxyo if w != user])

    content = st.text_area("Ujeedada")
    file = st.file_uploader("Lifaaq", ["pdf", "docx", "xlsx", "csv"])

    fname, fpath = "", ""
    if file:
        folder = os.path.join(storage_dir, to)
        os.makedirs(folder, exist_ok=True)
        fname = file.name
        fpath = os.path.join(folder, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fname}")
        with open(fpath, "wb") as f:
            f.write(file.read())

    if st.button("📨 Dir"):
        df = pd.concat([df, pd.DataFrame([{
            "id": str(uuid.uuid4()),
            "from": user,
            "to": to,
            "title": title,
            "content": content,
            "date": datetime.today().strftime("%Y-%m-%d"),
            "file": fname,
            "filepath": fpath,
            "box": "Inbox",
            "archived_by": ""
        }])], ignore_index=True)
        df.to_csv(letters_file, index=False)
        st.success("Waraaqda waa la diray")
        st.experimental_rerun()

    # ================= TABS =================
    inbox_tab, sent_tab, archive_tab = st.tabs(["📥 Inbox", "📤 Sent", "🗂 Archive"])

    # ---------- INBOX ----------
    with inbox_tab:
        inbox = df if is_admin else df[(df["to"] == user) & (df["box"] == "Inbox")]
        st.dataframe(inbox)

        if not inbox.empty:
            sel = st.selectbox("Dooro warqad si aad u archive-gareyso:", inbox["id"])
            if st.button("Archive Inbox"):
                df.loc[df["id"] == sel, "archived_by"] = user
                df.to_csv(letters_file, index=False)
                st.experimental_rerun()

    # ---------- SENT ----------
    with sent_tab:
        sent = df if is_admin else df[df["from"] == user]
        st.dataframe(sent)

        if not sent.empty:
            sel = st.selectbox("Dooro warqad Sent si aad u archive-gareyso:", sent["id"])
            if st.button("Archive Sent"):
                df.loc[df["id"] == sel, "archived_by"] = user
                df.to_csv(letters_file, index=False)
                st.experimental_rerun()

    # ---------- ARCHIVE ----------
    with archive_tab:
        archive = df if is_admin else df[df["archived_by"] == user]
        st.dataframe(archive)

    # ---------- DOWNLOAD ----------
    st.subheader("📎 Soo Degso Lifaaq")
    for _, r in df.iterrows():
        if r["filepath"] and os.path.exists(r["filepath"]):
            with open(r["filepath"], "rb") as f:
                st.download_button(
                    f"Soo degso {r['file']}",
                    f,
                    file_name=r["file"]
                )

    # ---------- LOGOUT ----------
    if st.button("🚪 Bixi"):
        st.session_state.clear()
        st.experimental_rerun()
