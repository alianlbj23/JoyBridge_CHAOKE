#!/bin/bash
# 取得當前腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
USER_NAME=$(whoami)
DESKTOP_PATH="/home/$USER_NAME/Desktop/JoyBridge.desktop"

# 建立 .desktop 檔案
cat > "$DESKTOP_PATH" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=JoyBridge (Start)
Comment=Start JoyBridge in venv
Exec=$SCRIPT_DIR/run.sh
Path=$SCRIPT_DIR
Terminal=true
Icon=utilities-terminal
Categories=Utility;
EOF

# 設定權限與信任
chmod +x "$DESKTOP_PATH"
gio set "$DESKTOP_PATH" metadata::trusted true

echo "✅ 已在 $DESKTOP_PATH 建立 JoyBridge.desktop 並設定完成。"
