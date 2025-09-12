# JoyBridge CHAOKE

This project provides a bridge to control a robot using a joystick through ROS. It reads joystick inputs, maps them to vehicle and robotic arm commands based on a configuration file, and sends them to ROS topics.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd JoyBridge_CHAOKE
   ```

2. **Install dependencies:**
   Install the required packages by running:
   ```bash
   pip install -r requirements.txt
   ```

## Architecture

The JoyBridge application works as follows:

1.  **Joystick Input**: It captures events from a connected joystick.
2.  **Command Mapping**: Based on the `config.yaml` file, these events (button presses and axis movements) are mapped to specific commands for the robot's wheels or robotic arm.
3.  **ROSBridge Communication**: The mapped commands are then sent as messages to a `rosbridge_server` via a WebSocket connection. This allows the application to communicate with the ROS ecosystem without being a native ROS node itself.
4.  **ROS Topics**: The `rosbridge_server` then publishes these messages to the appropriate ROS topics, which are subscribed to by the robot's control nodes.

## Configuration

- **`config.yaml`**: This file contains all the configuration for button mappings, axis controls, and ROS topic names. Modify this file to suit your robot's setup.
- **Controller Setup**: The application will automatically detect and list all connected joysticks. You may need to edit `joystick_controller.py` to select the correct joystick index if multiple controllers are connected.

## Usage

1. **Connect your joystick.**

2. **Start the ROS bridge:**
   Ensure your `rosbridge_server` is running.

3. **Run the application:**
   ```bash
   python main.py config.yaml
   ```
   or
   ```bash
   run.sh
   ```

## Desktop Shortcut (Optional)
To start JoyBridge by simply tapping an icon on the touchscreen, create a .desktop launcher:
1. Create a launcher file on your Desktop:

   ```
   cat > ~/Desktop/JoyBridge.desktop <<'EOF'
   [Desktop Entry]
   Type=Application
   Name=JoyBridge (Start)
   Comment=Start JoyBridge in venv
   Exec=/home/<YOUR_USER>/workspace/JoyBridge_CHAOKE/run.sh
   Terminal=true
   Icon=utilities-terminal
   Categories=Utility;
   EOF
   ```

   Replace <YOUR_USER> with your username and make sure run_joybridge.sh (or your startup script) is executable:

   ```
   chmod +x ~/workspace/JoyBridge_CHAOKE/run_joybridge.sh
   ```

2. Mark the shortcut as trusted and executable:

   ```
   chmod 755 ~/Desktop/JoyBridge.desktop
   gio set ~/Desktop/JoyBridge.desktop metadata::trusted true
   ```

3. Log into the desktop environment on the Jetson or PC where the joystick is connected, then tap the JoyBridge icon on the touchscreen to start the program.