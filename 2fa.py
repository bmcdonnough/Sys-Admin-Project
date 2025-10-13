import time
import pyotp
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD
import getpass
from pathlib import Path
import site
site.ENABLE_USER_SITE = True
site.addsitedir('/home/benmcdonnough/.local/lib/python3.13/site-packages')

# ====== CONFIGURATION ======
LCD_I2C_ADDR = 0x27  # change to your LCD address (use i2cdetect -y 1)
USER = getpass.getuser()
SECRET_PATH = Path(f"/etc/keypad_2fa/{USER}.secret")
CODE_LEN = 6
TIME_STEP = 30

# Keypad pins (BCM numbering)
ROWS = [5, 6, 13, 19]
COLS = [12, 16, 20]
KEYMAP = [
    ['1','2','3'],
    ['4','5','6'],
    ['7','8','9'],
    ['*','0','#']
]

# ====== LOAD SECRET ======
with open(SECRET_PATH) as f:
    USER_SECRET = f.read().strip()

# ====== SETUP LCD ======
lcd = CharLCD('PCF8574', 0x27,
              cols=16, rows=2, charmap='A00',
              auto_linebreaks=True)
lcd.clear()
lcd.write_string("2FA System Ready")
time.sleep(1)
lcd.clear()

# ====== SETUP GPIO ======
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for r in ROWS:
        GPIO.setup(r, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    for c in COLS:
        GPIO.setup(c, GPIO.OUT)
        GPIO.output(c, GPIO.LOW)

def read_key():
    while True:
        for c_idx, c in enumerate(COLS):
            GPIO.output(c, GPIO.HIGH)
            for r_idx, r in enumerate(ROWS):
                if GPIO.input(r) == GPIO.HIGH:
                    time.sleep(0.02)
                    if GPIO.input(r) == GPIO.HIGH:
                        key = KEYMAP[r_idx][c_idx]
                        while GPIO.input(r) == GPIO.HIGH:
                            time.sleep(0.01)
                        GPIO.output(c, GPIO.LOW)
                        return key
            GPIO.output(c, GPIO.LOW)
        time.sleep(0.01)

def verify_totp(code):
    totp = pyotp.TOTP(USER_SECRET, interval=TIME_STEP)
    return totp.verify(code, valid_window=1)

# ====== MAIN LOOP ======
def main():
    setup_gpio()
    lcd.clear()
    lcd.write_string("Enter 6-digit\nDuo Code:")

    try:
        while True:
            code = ""
            lcd.cursor_pos = (1, 0)
            lcd.write_string(" " * 16)  # clear bottom line
            lcd.cursor_pos = (1, 0)

            while len(code) < CODE_LEN:
                k = read_key()
                if k == '*':
                    code = ""
                    lcd.clear()
                    lcd.write_string("Cleared\nEnter again:")
                    time.sleep(1)
                    lcd.clear()
                    lcd.write_string("Enter 6-digit\nDuo Code:")
                    lcd.cursor_pos = (1, 0)
                    continue
                elif k == '#':
                    break
                elif k.isdigit():
                    code += k
                    lcd.write_string("*")
            lcd.clear()
            lcd.write_string("Verifying...")

            if verify_totp(code):
                lcd.clear()
                lcd.write_string("✅ Access Granted")
                print("Access granted.")
                time.sleep(2)
                lcd.clear()
                lcd.write_string("Enter 6-digit\nDuo Code:")
            else:
                lcd.clear()
                lcd.write_string("❌ Invalid Code")
                print("Invalid code.")
                time.sleep(2)
                lcd.clear()
                lcd.write_string("Enter 6-digit\nDuo Code:")
    except KeyboardInterrupt:
        lcd.clear()
        lcd.write_string("System halted")
        GPIO.cleanup()
        time.sleep(1)
        lcd.clear()

if __name__ == "__main__":
    main()
