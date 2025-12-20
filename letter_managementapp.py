# file: dds_letter_management.py

import streamlit as st
import sqlite3
import os
from datetime import datetime

# ===================== CONFIG =====================
UPLOAD_FOLDER = "stored_letters"
DB_NAME = "dds_letters.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===================== DATABASE =====================
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT,
    stored_filename TEXT,
    sender TEXT,
    receiver TEXT,
    sent_at TEXT
)
""")
conn.commit()

# ===================== DEPARTMENTS =====================
departments = [
    "Wasiirka (Muxidin)",
    "Wasiir Ku-xigeenka 1aad",
    "Wasiir Ku-xigeenka 2aad",
    "HRM",
    "Adeega Shacabka",
    "ICT",
    "Sharciyada",
    "Xadaynka",
    "Public Relation",
    "Planing",
    "Wacyigalinta"
]

# ===================== UI =====================
st.set_page_config(page_title="DDS Revenue Office", layout="wide")
st.title("📁 DDS Revenue Office – Letter Management System")

current_department = st.selectbox("Dooro Waaxdaada", departments)

menu = st.sidebar.radio("Menu", ["Dir Warqad", "Inbox"])

# ===================== SEND LETTER =====================
if menu == "Dir Warqad":
    st.header("📤 Dir Warqad (Original File)")

    uploaded_file = st.file_uploader(
        "Dooro warqadda computer-kaaga ku jirta",
        type=["pdf", "doc", "docx", "xls", "xlsx", "txt"]
    )

    receiver = st.selectbox(
        "U dir waaxda:",
        [d for d in departments if d != current_department]
    )

    if st.button("📨 Dir Warqadda"):
        if uploaded_file is None:
            st.error("Fadlan dooro warqad.")
        else:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            stored_filename = f"{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(UPLOAD_FOLDER, stored_filename)

            # Save ORIGINAL FILE (NO MODIFICATION)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            cursor.execute("""
                INSERT INTO letters 
                (original_filename, stored_filename, sender, receiver, sent_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                uploaded_file.name,
                stored_filename,
                current_department,
                receiver,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()

            st.success("✅ Warqadda original-ka ah si guul leh ayaa loo diray.")

# ===================== INBOX =====================
elif menu == "Inbox":
    st.header("📥 Warqadaha Laguu Soo Diray")

    cursor.execute("""
        SELECT original_filename, stored_filename, sender, sent_at
        FROM letters
        WHERE receiver = ?
        ORDER BY sent_at DESC
    """, (current_department,))

    letters = cursor.fetchall()

    if not letters:
        st.info("📭 Ma jiraan warqado laguu soo diray.")
    else:
        for original, stored, sender, date in letters:
            st.markdown("---")
            st.write(f"📄 **Warqad:** {original}")
            st.write(f"👤 **Laga soo diray:** {sender}")
            st.write(f"🕒 **Taariikh:** {date}")

            file_path = os.path.join(UPLOAD_FOLDER, stored)

            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Soo Daji Warqadda (Original)",
                        data=f,
                        file_name=original,
                        mime="application/octet-stream"
                    )
            else:
                st.error("❌ File-ka lama helin (khalad system).")
