import os
import pyotp
import qrcode
import getpass
from pathlib import Path

# ===============================
# Detect the real user
# ===============================
USER = os.getenv("SUDO_USER") or getpass.getuser()
SECRET_DIR = Path("/etc/keypad_2fa")
SECRET_FILE = SECRET_DIR / f"{USER}.secret"

# ===============================
# Ensure directory exists
# ===============================
if not SECRET_DIR.exists():
    print("🔐 Creating /etc/keypad_2fa directory...")
    os.system("sudo mkdir -p /etc/keypad_2fa && sudo chmod 700 /etc/keypad_2fa && sudo chown root:root /etc/keypad_2fa")

# ===============================
# Check if user already has a secret
# ===============================
if SECRET_FILE.exists():
    print(f"⚠️  A secret already exists for user '{USER}' at {SECRET_FILE}.")
    overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
    if overwrite != "y":
        print("❌ Cancelled. Keeping existing secret.")
        exit(0)

# ===============================
# Generate a new TOTP secret
# ===============================
secret = pyotp.random_base32()
print(f"✅ Generated new TOTP secret for {USER}: {secret}")

# Write secret securely
os.system(f"echo '{secret}' | sudo tee {SECRET_FILE} > /dev/null")
os.system(f"sudo chmod 600 {SECRET_FILE}")

# ===============================
# Generate provisioning URI and QR code
# ===============================
issuer_name = "RaspberryPi 2FA"
uri = pyotp.totp.TOTP(secret).provisioning_uri(name=USER, issuer_name=issuer_name)

print("\n📱 Scan this QR code in Duo or Google Authenticator:")
qr = qrcode.QRCode(border=2)
qr.add_data(uri)
qr.make(fit=True)
qr.print_ascii(invert=True)

print("\nOr add this manually:")
print(uri)

print("\n✅ Setup complete! You can now run your 2FA check with:")
print(f"    sudo python3 /home/{USER}/SysAdminProject/2fa.py")
