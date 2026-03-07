#!/bin/bash
#
# StoryBot Jetson Installation Script
#
# This script sets up a complete StoryBot deployment on NVIDIA Jetson.
# It creates the user, installs dependencies, configures services,
# and sets up hardware permissions.
#
# Usage:
#   sudo bash deploy/install.sh [--dev]
#
# Options:
#   --dev    Skip model downloads (for development/testing)
#
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

INSTALL_DIR="/opt/storybot"
SERVICE_USER="storybot"
DEV_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "================================================"
echo "StoryBot Installation Script"
echo "================================================"
echo "Target directory: $INSTALL_DIR"
echo "Service user: $SERVICE_USER"
echo "Dev mode: $DEV_MODE"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}ERROR: This script must be run as root${NC}"
   echo "Use: sudo bash deploy/install.sh"
   exit 1
fi

# Detect platform
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [[ "$ARCH" != "aarch64" ]]; then
    echo -e "${YELLOW}WARNING: This script is designed for Jetson (aarch64)${NC}"
    echo "Current architecture is $ARCH"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Create service user
echo ""
echo "Step 1: Creating service user..."
if id "$SERVICE_USER" &>/dev/null; then
    echo "User $SERVICE_USER already exists"
else
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_USER"
    echo -e "${GREEN}Created user $SERVICE_USER${NC}"
fi

# Step 2: Create installation directory
echo ""
echo "Step 2: Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
echo -e "${GREEN}Created $INSTALL_DIR${NC}"

# Step 3: Copy project files
echo ""
echo "Step 3: Copying project files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "$SCRIPT_DIR/.git" ]]; then
    echo "Copying from git repository..."
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
    cp -r "$SCRIPT_DIR"/.[!.]* "$INSTALL_DIR/" 2>/dev/null || true
else
    echo "Copying from directory (not a git repo)..."
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
fi
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
echo -e "${GREEN}Project files copied${NC}"

# Step 4: Install Python dependencies
echo ""
echo "Step 4: Installing Python dependencies..."
cd "$INSTALL_DIR"

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtualenv
echo "Creating virtual environment..."
sudo -u "$SERVICE_USER" uv venv "$INSTALL_DIR/.venv"

# Install dependencies (without jetson extras on non-jetson platforms)
if [[ "$ARCH" == "aarch64" ]]; then
    echo "Installing dependencies for Jetson..."
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/.venv/bin/pip" install -e "$INSTALL_DIR"
else
    echo "Installing dependencies with dev extras..."
    sudo -u "$SERVICE_USER" uv sync --extra dev
fi
echo -e "${GREEN}Dependencies installed${NC}"

# Step 5: Download models
if [[ "$DEV_MODE" == false ]]; then
    echo ""
    echo "Step 5: Downloading TTS models..."
    sudo -u "$SERVICE_USER" bash "$INSTALL_DIR/deploy/download-models.sh" "$INSTALL_DIR/models/piper"
    echo -e "${GREEN}Models downloaded${NC}"
else
    echo ""
    echo "Step 5: Skipping model downloads (dev mode)..."
fi

# Step 6: Create content directories
echo ""
echo "Step 6: Creating content directories..."
sudo -u "$SERVICE_USER" mkdir -p "$INSTALL_DIR/content/stories"
sudo -u "$SERVICE_USER" mkdir -p "$INSTALL_DIR/content/interactive"
sudo -u "$SERVICE_USER" mkdir -p "$INSTALL_DIR/content/images"
echo -e "${GREEN}Content directories created${NC}"

# Step 7: Configure hardware permissions
echo ""
echo "Step 7: Configuring hardware permissions..."

# Add user to required groups
usermod -aG audio "$SERVICE_USER"
usermod -aG dialout "$SERVICE_USER"
usermod -aG plugdev "$SERVICE_USER" || true
echo -e "${GREEN}Added $SERVICE_USER to audio, dialout, plugdev groups${NC}"

# Create udev rules for NFC reader
cat > /etc/udev/rules.d/99-storybot-nfc.rules << 'EOF'
# ACS ACR122U NFC Reader
SUBSYSTEM=="usb", ATTR{idVendor}=="072f", ATTR{idVendor}=="2200", MODE="0666", GROUP="plugdev"
EOF
echo -e "${GREEN}Created udev rules for NFC reader${NC}"

# Create udev rules for Brother printer
cat > /etc/udev/rules.d/99-storybot-printer.rules << 'EOF'
# Brother QL series printers
SUBSYSTEM=="usb", ATTR{idVendor}=="04f9", MODE="0666", GROUP="plugdev"
EOF
echo -e "${GREEN}Created udev rules for printer${NC}"

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

# Step 8: Install systemd services
echo ""
echo "Step 8: Installing systemd services..."
cp "$INSTALL_DIR/deploy/storybot.service" /etc/systemd/system/
cp "$INSTALL_DIR/deploy/storybot-kiosk.service" /etc/systemd/system/
systemctl daemon-reload
echo -e "${GREEN}Systemd services installed${NC}"

# Step 9: Enable services
echo ""
echo "Step 9: Enabling services..."
systemctl enable storybot.service
systemctl enable storybot-kiosk.service
echo -e "${GREEN}Services enabled${NC}"

# Step 10: Create .env file if not exists
echo ""
echo "Step 10: Creating environment configuration..."
if [[ ! -f "$INSTALL_DIR/.env" ]]; then
    cat > "$INSTALL_DIR/.env" << 'EOF'
# StoryBot Environment Configuration

# Hardware
NFC_READER_TYPE=acr122u
PRINTER_MODEL=QL-800
LED_ENABLED=false

# Audio
TTS_VOICE=es_ES-sharvard-medium
AUDIO_OUTPUT=auto

# Server
HOST=0.0.0.0
PORT=8000
EOF
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
    echo -e "${GREEN}Created .env file${NC}"
else
    echo ".env file already exists, skipping..."
fi

# Done!
echo ""
echo "================================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Reboot the system: sudo reboot"
echo "  2. StoryBot will start automatically on boot"
echo ""
echo "To manually start services:"
echo "  sudo systemctl start storybot"
echo "  sudo systemctl start storybot-kiosk"
echo ""
echo "To check service status:"
echo "  sudo systemctl status storybot"
echo "  sudo journalctl -u storybot -f"
echo ""
echo "To stop services:"
echo "  sudo systemctl stop storybot-kiosk"
echo "  sudo systemctl stop storybot"
echo ""
