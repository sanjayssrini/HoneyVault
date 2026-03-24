# 🍯 Honey Vault – Deceptive Authentication System

A secure vault system implementing **Honey Encryption** and **Distribution Transforming Encoding (DTE)** to protect user data against brute-force and password-guessing attacks.

This project ensures that **even incorrect passwords produce believable fake data**, preventing attackers from distinguishing real credentials from decoys.

---

## 🚀 Features

* 🔐 **Honey Encryption**

  * Incorrect passwords generate **plausible fake vaults**
  * Prevents attackers from verifying correct passwords

* 🧠 **DTE (Distribution Transforming Encoder)**

  * Encodes vault data into realistic seeds
  * Ensures outputs always look valid

* 🛡️ **Decoy Vault System**

  * Fake users and wrong passwords still return usable data
  * Attackers are misled instead of blocked

* 📊 **Security Monitoring**

  * Tracks suspicious login attempts
  * Alerts real users about unauthorized access

* 💻 **Two Interfaces**

  * Streamlit Web App (UI-based) 
  * CLI Application (Terminal-based) 

---

## 🏗️ Project Structure

```
HoneyVault/
│
├── crypto/
│   ├── key_derivation.py
│   ├── seed_cipher.py
│
├── dte/
│   ├── dte_encoder.py
│   ├── dte_decoder.py
│
├── semantic/
│   ├── validator.py
│
├── data/
│   ├── encrypted_vaults.json
│   ├── seed_map.json
│   ├── login_attempts.json
│
├── app.py              # Streamlit Web App
├── main.py              # CLI Version
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

### 🔑 Registration

1. User enters username and master password
2. Vault data (email, password, notes) is encoded into a **seed using DTE**
3. Seed is encrypted using a **derived key + salt**
4. Stored securely in database

---

### 🔓 Login

* **Correct Password**

  * Decrypts real seed
  * Retrieves actual vault

* **Incorrect Password**

  * Generates **fake seed**
  * Returns **decoy vault**
  * Logs suspicious activity

---

### 🧪 Honey Encryption Principle

Instead of failing:

```
Wrong Password → Fake but Realistic Vault
```

This ensures:

* No attacker can confirm correctness
* Every attempt looks valid

---

## 🖥️ Running the Project

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Run Web Application

```bash
streamlit run app.py
```

---

### 3️⃣ Run CLI Version

```bash
python main.py
```

---

## 📂 Data Storage

* `encrypted_vaults.json` → Stores encrypted seeds + salts
* `seed_map.json` → Maps real seeds to vault data
* `login_attempts.json` → Tracks suspicious activity

---

## 🚨 Security Features

* ✔ Fake vaults for wrong passwords
* ✔ Fake users behave like real users
* ✔ Logs attacker actions silently
* ✔ Alerts real users on login

---

## 🔍 Example Behavior

| Scenario                | Result          |
| ----------------------- | --------------- |
| Correct password        | Real vault      |
| Wrong password          | Fake vault      |
| Non-existent user       | Fake vault      |
| Attacker modifies vault | Logged silently |

---

## 🧠 Technologies Used

* Python
* Streamlit
* Cryptography (Key Derivation + Encryption)
* Honey Encryption
* Distribution Transforming Encoding (DTE)

---

## 📌 Use Cases

* Secure password managers
* Military-grade authentication systems
* Research in deception-based security
* Protection against brute-force attacks

---

## ⚠️ Future Improvements

* Multi-user vault support
* Cloud deployment
* Stronger semantic validation
* AI-based realistic decoy generation

---

## ⭐ Final Thought

> “In Honey Encryption, failure is indistinguishable from success.”

---

