echo "==> Installing ALSA config (asound.conf)..."
sudo cp ./service/asound.conf /etc/

echo "==> Installing piedra.sh startup script to /usr/local/bin..."
sudo cp ./service/piedra.sh /usr/local/bin
sudo chmod +x /usr/local/bin/piedra.sh

echo "==> Installing piedra.service systemd unit..."
sudo cp ./service/piedra.service /etc/systemd/system
sudo chmod 640 /etc/systemd/system/piedra.service

echo "==> Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "==> Enabling piedra service (start on boot)..."
sudo systemctl enable piedra

echo "==> Starting piedra service..."
sudo systemctl start piedra

echo "==> Setup complete. Current service status:"
sudo systemctl status piedra.service
