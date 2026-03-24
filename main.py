import json
import os
import hashlib
from datetime import datetime

from crypto.key_derivation import derive_key, generate_salt
from crypto.seed_cipher import encrypt_seed, decrypt_seed
from dte.dte_encoder import encode_message
from dte.dte_decoder import decode_seed
from semantic.validator import validate

DB_FILE = "data/encrypted_vaults.json"
SEED_MAP_FILE = "data/seed_map.json"
LOGIN_ATTEMPTS_FILE = "data/login_attempts.json"

# ------------------ Database ------------------

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_seed_map():
    if os.path.exists(SEED_MAP_FILE):
        with open(SEED_MAP_FILE) as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}

def save_seed_map(mapping):
    with open(SEED_MAP_FILE, "w") as f:
        json.dump(mapping, f, indent=4)

# ------------------ Login Attempts Tracking ------------------

def load_login_attempts():
    if os.path.exists(LOGIN_ATTEMPTS_FILE):
        with open(LOGIN_ATTEMPTS_FILE) as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}

def save_login_attempts(attempts):
    with open(LOGIN_ATTEMPTS_FILE, "w") as f:
        json.dump(attempts, f, indent=4)

def record_attempt(username, action, details=None):
    """Record any suspicious activity for a user."""
    attempts = load_login_attempts()
    if username not in attempts:
        attempts[username] = []
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action
    }
    if details:
        entry["details"] = details
    
    attempts[username].append(entry)
    save_login_attempts(attempts)

def get_and_clear_failed_attempts(username):
    """Get failed attempts for a user and clear them."""
    attempts = load_login_attempts()
    if username in attempts and len(attempts[username]) > 0:
        failed = attempts[username]
        attempts[username] = []  # Clear after reading
        save_login_attempts(attempts)
        return failed
    return []

def show_security_alert(username):
    """Display security alert if there were failed login attempts."""
    failed_attempts = get_and_clear_failed_attempts(username)
    if failed_attempts:
        print("\n" + "="*50)
        print("⚠️  SECURITY ALERT ⚠️")
        print("="*50)
        print(f"There were {len(failed_attempts)} suspicious activity(ies):")
        for attempt in failed_attempts:
            print(f"  - {attempt['timestamp']}: {attempt['action']}")
            if 'details' in attempt:
                print(f"    Details: {attempt['details']}")
        print("="*50)
        print("Someone may have tried to access your account!")
        print("Consider changing your master password.\n")

# ------------------ Core Ops ------------------

def register():
    print("\n--- Register ---")
    username = input("Username: ")
    pwd = input("Master password: ")

    db = load_db()
    if username in db:
        print("User already exists.")
        return

    email = input("Email: ")
    if "@" not in email:
        print("Invalid email. Must contain '@'.")
        return
    
    password = input("Account password: ")
    if len(password) < 6:
        print("Account password must be at least 6 characters.")
        return
    
    vault = {
        "email": email,
        "password": password,
        "notes": input("Notes: ")
    }

    salt = generate_salt()
    key = derive_key(pwd, salt)
    seed = encode_message(vault)
    
    mapping = load_seed_map()
    mapping[seed] = vault
    save_seed_map(mapping)
        
    enc = encrypt_seed(seed, key)

    db[username] = {
        "salt": salt.hex(),
        "cipher": enc
    }

    save_db(db)
    print("User registered.\n")

def login():
    print("\n--- Login ---")
    username = input("Username: ")
    pwd = input("Password: ")

    db = load_db()

    if username not in db:
        # Honey behavior: fake user still works
        fake_seed = hashlib.sha256((username + pwd).encode()).hexdigest()
        vault = decode_seed(fake_seed)
        validate(vault)
        print("\nVault opened:")
        print(vault)
        # Return with is_decoy=True, no real username to track
        return None, vault, pwd, True, None

    user = db[username]
    salt = bytes.fromhex(user["salt"])
    key = derive_key(pwd, salt)

    try:
        seed = decrypt_seed(user["cipher"], key)
        # Check if seed exists in seed_map (real vault)
        mapping = load_seed_map()
        if seed in mapping:
            vault = mapping[seed]
            validate(vault)
            
            # Show security alert for failed attempts BEFORE showing vault
            show_security_alert(username)
            
            print("\nVault opened:")
            print(vault)
            # Real user: is_decoy=False
            return username, vault, pwd, False, None
        else:
            # Seed not in map - shouldn't happen, record and show decoy
            record_attempt(username, "Login with invalid seed")
            vault = decode_seed(seed)
            validate(vault)
            print("\nVault opened:")
            print(vault)
            return None, vault, pwd, True, username
    except:
        # Decryption failed - wrong password, show honey vault
        # Record the failed attempt
        record_attempt(username, "Failed login attempt (wrong password)")
        
        fake_seed = hashlib.sha256((pwd + user["salt"]).encode()).hexdigest()
        vault = decode_seed(fake_seed)
        validate(vault)
        print("\nVault opened:")
        print(vault)
        # Return with is_decoy=True and real_username for tracking
        return None, vault, pwd, True, username

def update_vault(username, vault, pwd, is_decoy=False, real_username=None):
    print("\n--- Update Vault ---")
    
    new_email = input("New email: ")
    if "@" not in new_email:
        print("Invalid email. Must contain '@'.")
        return
    
    new_password = input("New password: ")
    if len(new_password) < 6:
        print("Password must be at least 6 characters.")
        return
    
    new_notes = input("New notes: ")
    
    if is_decoy:
        # Record the attempted update but don't actually save anything
        if real_username:
            record_attempt(real_username, "Attempted vault update", {
                "new_email": new_email,
                "new_password": new_password,
                "new_notes": new_notes
            })
        # Pretend it worked
        vault["email"] = new_email
        vault["password"] = new_password
        vault["notes"] = new_notes
        print("Vault updated.\n")
        return
    
    # Real update for authenticated user
    vault["email"] = new_email
    vault["password"] = new_password
    vault["notes"] = new_notes

    db = load_db()
    salt = bytes.fromhex(db[username]["salt"])
    key = derive_key(pwd, salt)
    seed = encode_message(vault)
    
    # Update the seed map with the new seed
    mapping = load_seed_map()
    mapping[seed] = vault
    save_seed_map(mapping)
    
    enc = encrypt_seed(seed, key)

    db[username]["cipher"] = enc
    save_db(db)
    print("Vault updated.\n")

def change_password(username, vault, is_decoy=False, real_username=None):
    print("\n--- Change Master Password ---")
    new_pwd = input("New password: ")

    if is_decoy:
        # Record the attempted password change but don't actually save anything
        if real_username:
            record_attempt(real_username, "Attempted master password change", {
                "new_password_hint": new_pwd[:2] + "***"  # Only log partial for security
            })
        # Pretend it worked
        print("Password changed.\n")
        return

    # Real password change for authenticated user
    db = load_db()
    salt = generate_salt()
    key = derive_key(new_pwd, salt)
    seed = encode_message(vault)
    
    # Update the seed map with the new seed
    mapping = load_seed_map()
    mapping[seed] = vault
    save_seed_map(mapping)
    
    enc = encrypt_seed(seed, key)

    db[username] = {
        "salt": salt.hex(),
        "cipher": enc
    }
    save_db(db)
    print("Password changed.\n")

def delete_user():
    print("\n--- Delete User ---")
    username = input("Username to delete: ")
    pwd = input("Master password: ")
    
    db = load_db()
    if username not in db:
        print("User not found.\n")
        return
    
    # Verify the master password
    user = db[username]
    salt = bytes.fromhex(user["salt"])
    key = derive_key(pwd, salt)
    
    try:
        seed = decrypt_seed(user["cipher"], key)
        mapping = load_seed_map()
        
        # Only allow deletion if seed is in map (real user with correct password)
        if seed in mapping:
            del db[username]
            save_db(db)
            
            # Also clean up login attempts for this user
            attempts = load_login_attempts()
            if username in attempts:
                del attempts[username]
                save_login_attempts(attempts)
            
            print(f"User '{username}' deleted successfully.\n")
        else:
            # Wrong password but decryption succeeded - record and fake success
            record_attempt(username, "Attempted account deletion")
            print(f"User '{username}' deleted successfully.\n")
    except:
        # Wrong password - record and fake success to not reveal anything
        record_attempt(username, "Attempted account deletion (wrong password)")
        print(f"User '{username}' deleted successfully.\n")

# ------------------ Main ------------------

def main():
    print("1. Register")
    print("2. Login")
    print("3. Delete User")
    choice = input("Choice: ")

    if choice == "1":
        register()

    elif choice == "2":
        result = login()
        username, vault, pwd, is_decoy, real_username = result
        
        # Show menu for both real and decoy users (attacker won't know the difference)
        if vault:
            while True:
                print("\n1. Update vault")
                print("2. Change password")
                print("3. Exit")
                c = input("Choice: ")

                if c == "1":
                    update_vault(username, vault, pwd, is_decoy, real_username)
                elif c == "2":
                    change_password(username, vault, is_decoy, real_username)
                elif c == "3":
                    break
    
    elif choice == "3":
        delete_user()

if __name__ == "__main__":
    main()
