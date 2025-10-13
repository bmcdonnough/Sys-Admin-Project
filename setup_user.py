#!/usr/bin/env python3
import os
import pyotp
import qrcode
import getpass
from pathlib import Path
import pyqrcode

# ===== Configuration =====
ISSUER = "MyPiKeypadProject"
SECRETS_DIR = Path("/etc/keypad_2fa")

# ===== Determine current user =====
current_user = getpass.getuser()  # e.g. 'pi', 'ben', etc.
print(f"Detected current user: {current_user}")

# ===== Ensure directory exists =====
SECRETS_DIR.mkdir(parents=True, exist_ok=True)

# ===== Determine user secret file =====
secret_file = SECRETS_DIR / f"{current_user}.secret"

# ===== Generate or reuse secret =====
if secret_file.exists():
    print(f"Secret already exists for {current_user}. Reusing existing secret.")
    secret = secret_file.read_text().strip()
else:
    secret = pyotp.random_base32()
    secret_file.write_text(secret)
    os.chmod(secret_file, 0o600)
    print(f"Created new secret for {current_user} at {secret_file}")

# ===== Create TOTP and provisioning URI =====
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name=current_user, issuer_name=ISSUER)
qr = pyqrcode.create(uri)
print("\nScan this QR code in Duo Mobile (or any authenticator):")
print(qr.terminal())

# ===== Generate QR code image =====
qr_filename = f"{current_user}_totp_qr.png"
img = qrcode.make(uri)
img.save(qr_filename)
print(f"\nQR code saved as: {qr_filename}")
print("You can open this image and scan it with Duo Mobile to register your account.")

# ===== Display info summary =====
print("\nSummary:")
print(f"  User: {current_user}")
print(f"  Secret path: {secret_file}")
print(f"  QR code file: {qr_filename}")
print("Done ✅")
