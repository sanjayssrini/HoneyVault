import streamlit as st
import json
import os
import hashlib
from datetime import datetime

from crypto.key_derivation import derive_key
from crypto.seed_cipher import encrypt_seed, decrypt_seed
from dte.dte_encoder import encode_vault
from dte.dte_decoder import decode_seed

DB_FILE = "data/encrypted_vaults.json"
SEED_MAP_FILE = "data/seed_map.json"
LOGIN_LOG_FILE = "data/login_attempts.json"


# ============================================================
# UTIL
# ============================================================

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        raw = f.read().strip()
        return json.loads(raw) if raw else {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_logs():
    if not os.path.exists(LOGIN_LOG_FILE):
        return {}
    with open(LOGIN_LOG_FILE) as f:
        raw = f.read().strip()
        return json.loads(raw) if raw else {}

def generate_salt():
    return os.urandom(16)

def fake_seed(username, password):
    return hashlib.sha256((username + password).encode()).hexdigest()


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(page_title="Honey Vault", layout="centered")


# ============================================================
# STYLE (UNCHANGED)
# ============================================================

st.markdown("""
<style>
section.main > div {
    padding-top: 0rem !important;
}

.center-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100px;
    text-align: center;
}

.hero-title {
    font-size: 48px;
    font-weight: 700;
    margin-bottom: 10px;
}

.hero-sub {
    font-size: 18px;
    color: #94a3b8;
    margin-bottom: 40px;
}

div.stButton > button {
    width: 200px;
    border-radius: 10px;
    padding: 12px;
    font-size: 16px;
    margin: 5px;
    background: #2563eb;
    color: white;
    border: none;
    transition: 0.2s;
}

div.stButton > button:hover {
    background: #1d4ed8;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "vault" not in st.session_state:
    st.session_state.vault = None

if "is_real" not in st.session_state:
    st.session_state.is_real = False

if "master_password" not in st.session_state:
    st.session_state.master_password = None


# ============================================================
# LOAD DB
# ============================================================

db = load_json(DB_FILE)
seed_map = load_json(SEED_MAP_FILE)


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "home":

    st.markdown('<div class="center-box">', unsafe_allow_html=True)

    st.markdown('<div class="hero-title">Honey Vault</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Deceptive authentication using honey encryption</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# LOGIN
# ============================================================

elif st.session_state.page == "login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Authenticate"):

        if username in db:
            salt = bytes.fromhex(db[username]["salt"])
            key = derive_key(password, salt)

            try:
                seed = decrypt_seed(db[username]["cipher"], key)
            except:
                seed = fake_seed(username, password)
        else:
            seed = fake_seed(username, password)

        vault = decode_seed(seed)

        st.session_state.is_real = seed in seed_map
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.vault = vault
        st.session_state.master_password = password   # FIX

        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()


# ============================================================
# REGISTER
# ============================================================

elif st.session_state.page == "register":

    st.title("Create Account")

    username = st.text_input("Username")
    master_password = st.text_input("Master Password", type="password")

    st.subheader("Vault Data")

    email = st.text_input("Email")
    acc_password = st.text_input("Password")
    notes = st.text_area("Notes")

    if st.button("Register"):

        if username in db:
            st.warning("User already exists")
        else:
            vault = {
                "email": email,
                "password": acc_password,
                "notes": notes
            }

            seed = encode_vault(vault)

            salt = generate_salt()
            key = derive_key(master_password, salt)
            cipher = encrypt_seed(seed, key)

            db[username] = {
                "salt": salt.hex(),
                "cipher": cipher
            }

            seed_map[seed] = vault

            save_json(DB_FILE, db)
            save_json(SEED_MAP_FILE, seed_map)

            st.success("Account created")

            st.session_state.page = "login"
            st.rerun()

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

elif st.session_state.page == "dashboard":

    st.title("Vault Dashboard")

    vault = st.session_state.vault

    # ================= SECURITY PANEL =================

    if st.session_state.is_real:

        attempts = load_logs()
        user_logs = attempts.get(st.session_state.username, [])

        if user_logs:

            st.error("Security Alert")

            st.write(f"There were {len(user_logs)} suspicious activity(ies):")

            for log in user_logs:
                st.write(f"- {log['timestamp']}: {log['action']}")
                if "details" in log:
                    st.code(str(log["details"]))

            st.warning("Someone may have tried to access your account. Consider changing your master password.")

    # ==================================================

    email = st.text_input("Email", vault.get("email", ""))
    acc_password = st.text_input("Password", vault.get("password", ""))
    notes = st.text_area("Notes", vault.get("notes", ""))

    if st.button("Update Vault"):

        new_vault = {
            "email": email,
            "password": acc_password,
            "notes": notes
        }

        # ---------- FAKE USER ----------
        if not st.session_state.is_real:

            st.session_state.vault = new_vault
            st.success("Vault updated")

            attempts = load_logs()
            user = st.session_state.username

            if user in db:
                if user not in attempts:
                    attempts[user] = []

                attempts[user].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "Attempted vault update",
                    "details": new_vault
                })

                save_json(LOGIN_LOG_FILE, attempts)

        # ---------- REAL USER ----------
        else:

            salt = bytes.fromhex(db[st.session_state.username]["salt"])
            key = derive_key(st.session_state.master_password, salt)

            seed = encode_vault(new_vault)
            cipher = encrypt_seed(seed, key)

            db[st.session_state.username]["cipher"] = cipher
            seed_map[seed] = new_vault

            save_json(DB_FILE, db)
            save_json(SEED_MAP_FILE, seed_map)

            st.success("Vault updated")

    if st.button("Logout"):
        st.session_state.clear()
        st.session_state.page = "home"
        st.rerun()