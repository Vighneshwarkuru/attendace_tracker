import pandas as pd
import base64
from datetime import datetime
import os

# File paths
USERS_FILE = "users.csv"
REGISTERED_FILE = "registered.csv"
VALIDATED_FILE = "validated.csv"

# Ensure required CSV files exist
for file in [REGISTERED_FILE, VALIDATED_FILE]:
    if not os.path.exists(file):
        pd.DataFrame(columns=["username", "email", "role", "location", "timestamp"]).to_csv(file, index=False)

# Login and return user dict if valid
def login(username, email):
    users = pd.read_csv(USERS_FILE)
    match = users[(users['username'] == username) & (users['email'] == email)]
    return match.iloc[0].to_dict() if not match.empty else None

# Generate and print base64 QR string
def generate_encoded_qr_string(username, email):
    data = f"{username}|{email}"
    encoded = base64.b64encode(data.encode()).decode()
    print(f"\n📎 QR Code (share this with Tech Lead for scanning):\n{encoded}\n")
    return encoded

# Register user attendance intent
def register_user(username, email, role, location):
    df = pd.read_csv(REGISTERED_FILE)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = pd.DataFrame([{
        "username": username,
        "email": email,
        "role": role,
        "location": location,
        "timestamp": timestamp
    }])
    df = pd.concat([df, entry], ignore_index=True)
    df.to_csv(REGISTERED_FILE, index=False)
    print("✅ Registered successfully in registered.csv")

# Get role from users.csv
def get_user_role(username, email):
    users = pd.read_csv(USERS_FILE)
    match = users[(users['username'] == username) & (users['email'] == email)]
    return match.iloc[0]['role'] if not match.empty else None

# Validate QR string and mark attendance
def validate_attendance(encoded_data, scanner_role, location):
    try:
        decoded = base64.b64decode(encoded_data).decode()
        username, email = decoded.split("|")
        role = get_user_role(username, email)

        if scanner_role == "Tech Lead" and role == "AI Developer":
            mark_validated(username, email, role, location)
        else:
            print(f"⚠️ {scanner_role} is not authorized to scan {role}")
    except Exception as e:
        print(f"❌ Failed to decode QR: {e}")

# Save to validated.csv
def mark_validated(username, email, role, location):
    df = pd.read_csv(VALIDATED_FILE)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = pd.DataFrame([{
        "username": username,
        "email": email,
        "role": role,
        "location": location,
        "timestamp": timestamp
    }])
    df = pd.concat([df, entry], ignore_index=True)
    df.to_csv(VALIDATED_FILE, index=False)
    print("✅ Attendance validated and saved to validated.csv")

# Main interactive flow
if __name__ == "__main__":
    print("🎯 Welcome to the Offline Attendance System")
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()

    user = login(username, email)
    if not user:
        print("❌ Invalid username or email.")
    else:
        role = user["role"]
        print(f"👋 Logged in as: {role}")

        if role == "AI Developer":
            location = input("Enter your location: ").strip()
            attending = input("Will you attend offline? (yes/no): ").strip().lower()
            if attending == "yes":
                generate_encoded_qr_string(username, email)
                register_user(username, email, role, location)

        elif role == "Tech Lead":
            location = input("Enter your location: ").strip()
            encoded_qr = input("Paste the Base64 QR string from AI Developer: ").strip()
            validate_attendance(encoded_qr, role, location)

        elif role == "Admin":
            location = input("Enter location to view attendance: ").strip()
            df = pd.read_csv(VALIDATED_FILE)
            print(f"\n📊 Validated Attendance for {location}:\n")
            print(df[df['location'] == location].to_string(index=False))

        else:
            print("⚠️ Unknown role or no permissions assigned.")