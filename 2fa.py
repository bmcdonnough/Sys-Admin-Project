import os
import sys
import time
import pyotp
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
from pathlib import Path

# ===============================
# LCD Configuration (adjust as needed)
# ===============================
lcd = CharLCD('PCF8574', 0x27)  # if i2cdetect shows 0x3F, change it here
lcd.clear()
lcd.write_string("2FA System Ready")
time.sleep(1)
lcd.clear()

# ===============================
# Keypad GPIO Pin Setup
# ===============================
L1, L2, L3, L4 = 5, 6, 13, 19
C1, C2, C3, C4 = 12, 16, 20, 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for pin in [L1, L2, L3, L4]:
    GPIO.setup(pin, GPIO.OUT)

for pin in [C1, C2, C3, C4]:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# ===============================
# Keymap
# ===============================
key_map = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

# ===============================
# Helper Functions
# ===============================

def read_line(line, characters):
    GPIO.output(line, GPIO.HIGH)
    for i, pin in enumerate([C1, C2, C3, C4]):
        if GPIO.input(pin) == 1:
            GPIO.output(line, GPIO.LOW)
            return characters[i]
    GPIO.output(line, GPIO.LOW)
    return None


def get_keypad_input(prompt="Enter Code:", code_length=6):
    lcd.clear()
    lcd.write_string(prompt)
    entered = ""

    while len(entered) < code_length:
        for line, chars in zip([L1, L2, L3, L4], key_map):
            key = read_line(line, chars)
            if key:
                if key == "#":  # confirm
                    return entered
                elif key == "*":  # clear
                    entered = ""
                    lcd.clear()
                    lcd.write_string(prompt)
                elif key.isdigit():
                    entered += key
                    lcd.clear()
                    lcd.write_string(prompt)
                    lcd.cursor_pos = (1, 0)
                    #lcd.write_string("*" * len(entered))
                    lcd.write_string(f"{key}")
                time.sleep(0.3)
        time.sleep(0.05)  

    return entered      

# ===============================
# User + TOTP Setup
# ===============================
USER = os.getenv("SUDO_USER") or os.getenv("USER") or os.getlogin()
secret_path = Path(f"/etc/keypad_2fa/{USER}.secret")

if not secret_path.exists():
    lcd.clear()
    lcd.write_string("❌ No secret found")
    time.sleep(2)
    GPIO.cleanup()
    sys.exit(1)

with open(secret_path, "r") as f:
    secret = f.read().strip()

totp = pyotp.TOTP(secret, digits=6)


# ===============================
# Verification Loop (3 attempts)
# ===============================
try:
    MAX_ATTEMPTS = 3
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        code = get_keypad_input("Enter Duo Code:")

        lcd.clear()
        if totp.verify(code, valid_window=1):
            lcd.clear()
            lcd.write_string("✅ Access Granted")
            time.sleep(1.5)
            lcd.clear()
            GPIO.cleanup()
            sys.exit(0)

        # Wrong code
        attempts += 1
        remaining = MAX_ATTEMPTS - attempts
        lcd.clear()
        if remaining > 0:
            lcd.write_string(f"❌ Invalid ({remaining})")
            time.sleep(1.5)
        else:
            lcd.write_string("❌ Locked Out")
            time.sleep(2)
            lcd.clear()
            GPIO.cleanup()
            sys.exit(1)
except KeyboardInterrupt:
    lcd.clear()
    time.sleep(1)
    GPIO.cleanup()
    sys.exit(1)