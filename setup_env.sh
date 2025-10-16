#!/bin/bash
set -e

PROJECT_DIR="/home/pi/SysAdminProject"
REPO_URL="https://github.com/bmcdonnough/Sys-Admin-Project.git"
USER_NAME=$(logname)
REAL_SUDO="/usr/bin/sudo"

echo "=== Installing dependencies ==="
$REAL_SUDO apt update -y
$REAL_SUDO apt install -y python3 python3-pip git i2c-tools python3-smbus acl

echo "=== Installing Python packages ==="
pip3 install --upgrade RPLCD pyotp pyqrcode qrcode --break-system-packages

echo "=== Enabling I2C and GPIO access ==="
$REAL_SUDO raspi-config nonint do_i2c 0 || true
$REAL_SUDO usermod -aG i2c "$USER_NAME"
$REAL_SUDO usermod -aG gpio "$USER_NAME"

echo "=== Cloning or updating repository ==="
if [ -d "$PROJECT_DIR/.git" ]; then
    cd "$PROJECT_DIR"
    $REAL_SUDO git pull
else
    $REAL_SUDO git clone "$REPO_URL" "$PROJECT_DIR"
    $REAL_SUDO chown -R root:root "$PROJECT_DIR"
    $REAL_SUDO chmod -R 755 "$PROJECT_DIR"
fi

$REAL_SUDO git config --system --add safe.directory "$PROJECT_DIR" || true

echo "=== Creating 2FA secret directory ==="
$REAL_SUDO mkdir -p /etc/keypad_2fa
$REAL_SUDO chmod 751 /etc/keypad_2fa
$REAL_SUDO chown root:root /etc/keypad_2fa

echo "=== Running setup_user.py for $USER_NAME ==="
cd "$PROJECT_DIR"
$REAL_SUDO -u "$USER_NAME" python3 setup_user.py

# Fix ownership and permissions of the created secret file
SECRET_FILE="/etc/keypad_2fa/${USER_NAME}.secret"
if [ -f "$SECRET_FILE" ]; then
    $REAL_SUDO chown "$USER_NAME":root "$SECRET_FILE"
    $REAL_SUDO chmod 640 "$SECRET_FILE"
fi

echo "=== Installing sudo-2fa wrapper ==="
$REAL_SUDO cp "$PROJECT_DIR/sudo-2fa" /usr/local/bin/sudo-2fa
$REAL_SUDO chmod 755 /usr/local/bin/sudo-2fa
$REAL_SUDO chown root:root /usr/local/bin/sudo-2fa

echo "=== 9. Setting up per-user 2FA alias ==="
BASHRC="/home/$USER_NAME/.bashrc"
if ! grep -q "sudo-2fa" "$BASHRC"; then
    echo "alias sudo='/usr/local/bin/sudo-2fa'" >> "$BASHRC"
    chown "$USER_NAME":"$USER_NAME" "$BASHRC"

echo "=== Final verification ==="
groups "$USER_NAME" | grep -E "i2c|gpio" >/dev/null || echo "⚠️  Add user to i2c/gpio groups manually."
ls -l /etc/keypad_2fa
echo
echo "✅ Setup complete for user $USER_NAME"
echo "Run 'sudo whoami' to test 2FA."




