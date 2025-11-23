# Raspberry Pi Two-Factor Authentication (2FA) System

A hardware-based two-factor authentication system for Raspberry Pi that uses a physical keypad and LCD display to secure `sudo` commands with TOTP (Time-based One-Time Password) authentication.

## Overview

This project implements a physical 2FA system that intercepts `sudo` commands and requires users to enter a 6-digit code from their authenticator app (like Duo or Google Authenticator) using a hardware keypad. The LCD display provides real-time feedback during authentication.

## Features

- **Hardware keypad input**: Enter TOTP codes using a physical 4x4 matrix keypad
- **LCD feedback**: Real-time status display on a 16x2 I2C LCD screen
- **TOTP authentication**: Compatible with Duo, Google Authenticator, and other TOTP apps
- **Session caching**: Remembers successful authentication for 15 minutes to avoid repeated prompts
- **Multiple attempts**: Allows 3 attempts per authentication request
- **Secure storage**: TOTP secrets stored in `/etc/keypad_2fa/` with proper permissions

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- 16x2 I2C LCD Display (PCF8574 or compatible, typically at address 0x27 or 0x3F)
- 4x4 Matrix Keypad
- Jumper wires for connections

### GPIO Pin Configuration

**Keypad Rows (Output):**
- Row 1: GPIO 5
- Row 2: GPIO 6
- Row 3: GPIO 13
- Row 4: GPIO 19

**Keypad Columns (Input):**
- Column 1: GPIO 12
- Column 2: GPIO 16
- Column 3: GPIO 20
- Column 4: GPIO 21

**LCD:**
- Connected via I2C (SDA/SCL pins)

## Software Dependencies

- Python 3
- Python packages:
  - `RPi.GPIO` - GPIO control
  - `RPLCD` - LCD display driver
  - `pyotp` - TOTP generation and verification
  - `pyqrcode` / `qrcode` - QR code generation for setup
- System packages:
  - `i2c-tools` - I2C utilities
  - `python3-smbus` - I2C Python bindings
  - `acl` - Access control lists

## Installation

### Automated Setup

Run the automated setup script as a regular user (it will use sudo internally):

```bash
bash setup_env.sh
```

This script will:
1. Install all required system packages
2. Install Python dependencies
3. Enable I2C and add your user to necessary groups
4. Clone/update the repository to `/home/pi/SysAdminProject`
5. Create the 2FA secrets directory
6. Generate your TOTP secret and QR code
7. Install the `sudo-2fa` wrapper
8. Add a `sudo` alias to your `.bashrc`

### Manual Setup

If you prefer manual installation:

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip git i2c-tools python3-smbus acl
   pip3 install --upgrade RPLCD pyotp pyqrcode qrcode --break-system-packages
   ```

2. **Enable I2C:**
   ```bash
   sudo raspi-config nonint do_i2c 0
   ```

3. **Add user to groups:**
   ```bash
   sudo usermod -aG i2c,gpio $USER
   ```

4. **Set up 2FA secret:**
   ```bash
   cd /home/pi/SysAdminProject
   python3 setup_user.py
   ```
   Scan the QR code with your authenticator app.

5. **Install sudo wrapper:**
   ```bash
   sudo cp sudo-2fa /usr/local/bin/sudo-2fa
   sudo chmod 755 /usr/local/bin/sudo-2fa
   ```

6. **Add alias to .bashrc:**
   ```bash
   echo "alias sudo='/usr/local/bin/sudo-2fa'" >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

After installation, simply use `sudo` commands as normal:

```bash
sudo whoami
```

The system will:
1. Check if you've authenticated recently (within 15 minutes)
2. If not, prompt you on the LCD to enter your 6-digit TOTP code
3. Use the keypad to enter the code from your authenticator app
4. Press `#` to confirm or `*` to clear and re-enter
5. Grant access if the code is correct

### Keypad Controls

- **0-9**: Enter digits
- **#**: Confirm/Submit code
- **\***: Clear entered code
- **A, B, C, D**: Reserved (not used in current version)

## Project Files

- **`2fa.py`**: Main authentication script that handles keypad input, LCD display, and TOTP verification
- **`setup_env.sh`**: Automated setup script for complete system installation
- **`setup_user.py`**: Generates TOTP secret and QR code for individual users
- **`sudo-2fa`**: Bash wrapper script that intercepts sudo commands and triggers 2FA
- **`root_totp_qr.png`**: Example QR code image (for reference)

## Configuration

### Changing LCD I2C Address

If your LCD uses a different I2C address (check with `i2cdetect -y 1`):

Edit `2fa.py` line 19:
```python
lcd = CharLCD('PCF8574', 0x27)  # Change to 0x3F or your address
```

### Adjusting Session Timeout

Edit `sudo-2fa` line 8:
```bash
TIMEOUT=900  # Change timeout in seconds (default: 15 minutes)
```

### Changing Max Attempts

Edit `2fa.py` line 114:
```python
MAX_ATTEMPTS = 3  # Change number of allowed attempts
```

## Troubleshooting

### LCD not displaying
- Run `i2cdetect -y 1` to verify I2C address
- Check I2C is enabled: `ls /dev/i2c*`
- Verify wiring connections

### Permission denied errors
- Ensure user is in `i2c` and `gpio` groups: `groups $USER`
- Re-login after adding to groups for changes to take effect

### TOTP code always fails
- Verify system time is synchronized: `timedatectl status`
- Check authenticator app is using correct time
- Ensure secret file exists: `ls -l /etc/keypad_2fa/`

### Keypad not responding
- Check GPIO pin connections match the configuration
- Verify pins are not in use by other services
- Test with `gpio readall` command

### Script path errors
- Note: There is an inconsistency in the original project files where `setup_env.sh` uses `/home/pi/SysAdminProject` but `sudo-2fa` uses `/home/pi/SysadminProject`
- If you encounter "file not found" errors, check which directory name was created and update the path in `sudo-2fa` line 5 accordingly

## Security Considerations

- TOTP secrets are stored in `/etc/keypad_2fa/` with restricted permissions (640, owned by user:root)
- Each user has their own secret file
- Session cache files are stored in `/tmp/` and expire after 15 minutes
- The system provides hardware-based 2FA, adding physical security to authentication
- Failed authentication attempts are limited to 3 per session

## Compatibility

- Tested on Raspberry Pi 4 with Raspberry Pi OS
- Should work on other Raspberry Pi models with GPIO support
- Requires Python 3.7 or higher

## License

This project is provided as-is for educational and system administration purposes.

## Contributing

Contributions are welcome! Please ensure hardware compatibility when making changes to GPIO configurations.
