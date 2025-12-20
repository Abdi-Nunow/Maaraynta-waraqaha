import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Maaraynta Waraaqaha", layout="wide")
st.title("📁 Nidaamka Maareynta Waraaqaha")
st.markdown("Nidaam rasmi ah oo waaxyaha xafiiska dakhliga ay isku diraan waraaqaha.")

# ===== FILES & STORAGE =====
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
    st.subheader("🔐 Gal Nidaamka")
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
                st.error("Password khaldan ❌")
    else:
        admin_input = st.text_input("Admin username")
        admin_pass = st.text_input("Admin password", type="password")
        if st.button("✅ Gali"):
            if admin_input == admin_user and admin_pass == admin_password:
                st.session_state.waaxda_user = "Admin"
                st.session_state.is_admin = True
                st.experimental_rerun()
            else:
                st.error("Xogta Admin waa khaldan ❌")

# ===== MAIN APP =====
else:
    user = st.session_state.waaxda_user
    is_admin = st.session_state.is_admin
    st.success(f"👋 Ku soo dhawoow {user}")

    # ===== LOAD LETTERS =====
    if os.path.exists(waraaqaha_file):
        df = pd.read_csv(waraaqaha_file)
    else:
        df = pd.DataFrame(columns=[
            "Ka socota", "Loogu talagalay", "Cinwaanka",
            "Qoraalka", "Taariikh",
            "File", "FilePath",
            "Status", "ArchivedBy"
        ])

    # ===== SEND LETTER =====
    st.subheader("📤 Dir Waraaq")
    col1, col2 = st.columns(2)
    with col1:
        cinwaan = st.text_input("Cinwaanka")
    with col2:
        loo_dirayo = st.selectbox(
            "Loogu talagalay:",
            [w for w in waaxyo_passwords if w != user]
        )

    qoraal = st.text_area("Objective")
    uploaded_file = st.file_uploader("Lifaaq", type=["pdf", "docx", "xlsx", "csv"])

    file_name, file_path = "", ""
    if uploaded_file:
        folder = os.path.join(storage_dir, loo_dirayo)
        os.makedirs(folder, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = uploaded_file.name
        file_path = os.path.join(folder, f"{ts}_{file_name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

    if st.button("📨 Dir"):
        df = pd.concat([df, pd.DataFrame([{
            "Ka socota": user,
            "Loogu talagalay": loo_dirayo,
            "Cinwaanka": cinwaan,
            "Qoraalka": qoraal,
            "Taariikh": datetime.today().strftime("%Y-%m-%d"),
            "File": file_name,
            "FilePath": file_path,
            "Status": "Inbox",
            "ArchivedBy": ""
        }])], ignore_index=True)
        df.to_csv(waraaqaha_file, index=False)
        st.success("✅ Waraaqda waa la diray")

    # ===== TABS =====
    tab1, tab2, tab3 = st.tabs(["📥 Inbox", "📤 Sent", "🗂 Archive"])

    # ===== INBOX =====
    with tab1:
        inbox = df if is_admin else df[
            (df["Loogu talagalay"] == user) &
            (df["Status"] == "Inbox")
        ]
        st.dataframe(inbox)

    # ===== SENT =====
    with tab2:
        sent = df if is_admin else df[df["Ka socota"] == user]
        st.dataframe(sent)

    # ===== ARCHIVE =====
    with tab3:
        archive = df if is_admin else df[
            (df["ArchivedBy"] == user)
        ]
        st.dataframe(archive)

    # ===== ARCHIVE ACTION =====
    st.subheader("🗂 Ku dar Archive")
    if not df.empty:
        idx = st.number_input("Dooro row index:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Archive garee"):
            df.loc[idx, "Status"] = "Archived"
            df.loc[idx, "ArchivedBy"] = user
            df.to_csv(waraaqaha_file, index=False)
            st.success("✅ Waraaqda waa la archive gareeyay")
            st.experimental_rerun()

    # ===== DOWNLOAD FILE =====
    st.subheader("📎 Soo Degso Lifaaq")
    for _, row in df.iterrows():
        if row["FilePath"] and os.path.exists(row["FilePath"]):
            with open(row["FilePath"], "rb") as f:
                st.download_button(
                    f"Soo degso {row['File']}",
                    f,
                    file_name=row["File"]
                )

    # ===== LOGOUT =====
    if st.button("🚪 Bixi"):
        st.session_state.clear()
        st.experimental_rerun()
