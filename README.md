# JoyBridge_CHAOKE

A Python-based joystick controller that bridges gamepad input to ROS topics via rosbridge. This project allows you to control robotic systems using a standard gamepad/joystick by converting joystick inputs into ROS messages.

## Device
https://www.taobao.com/list/item/805683311431.htm

## Features

- **Gamepad Support**: Compatible with standard gamepads (Xbox, PlayStation controllers)
- **ROS Integration**: Publishes to ROS topics through rosbridge websocket
- **Configurable Controls**: YAML-based configuration for button mappings and joystick behavior
- **Angle-based Control**: Convert joystick positions to directional angles with speed control
- **Deadzone Support**: Customizable deadzone settings for joystick precision
- **Real-time Publishing**: Live input translation to ROS Float32MultiArray messages

## Requirements

- Python 3.x
- pygame
- roslibpy
- PyYAML
- Running ROS system with rosbridge server

## Installation

1. Clone this repository:
```bash
git clone https://github.com/alianlbj23/JoyBridge_CHAOKE.git
cd JoyBridge_CHAOKE
```

2. Install required packages:
```bash
pip install pygame roslibpy pyyaml
```

3. Ensure rosbridge is running on your ROS system:
```bash
roslaunch rosbridge_server rosbridge_websocket.launch
```

## Usage

1. Connect your gamepad/joystick to your computer
2. Configure the settings in `config.yaml` (see Configuration section)
3. Run the main script:
```bash
python main.py config.yaml
```

## Configuration

The `config.yaml` file contains all the configuration settings:

### Button Mappings
```yaml
buttons:
  A:      [0.0, 0.0, 0.0, 0.0]  # Speed values for 4 wheels [FL, FR, RL, RR]
  B:      [0.0, 0.0, 0.0, 0.0]
  # ... other buttons
```

### Joystick Settings
```yaml
axes_angle_map:
  left_stick:
    deadzone: 0.15              # Deadzone threshold
    rules:
      - range: [-30.0, 30.0]    # Angle range in degrees
        speed: [30.0, -30.0, 30.0, -30.0]  # Wheel speeds
      # ... more rules
```

### ROS Topics
```yaml
ros_topics:
  - name: /car_C_front_wheel    # ROS topic name
    indices: [0, 1]             # Which values from speed array to publish
  - name: /car_C_rear_wheel
    indices: [2, 3]
```

### Rosbridge Connection
```yaml
rosbridge:
  host: 127.0.0.1              # Rosbridge server IP
  port: 9090                   # Rosbridge server port
```

## Control Mapping

### Default Button Layout (Xbox Controller)
- **A, B, X, Y**: Configurable action buttons
- **LB, RB**: Left/Right bumpers
- **Start, Back**: Menu buttons
- **LStick, RStick**: Joystick click buttons

### Joystick Controls
- **Left Stick**: Primary movement control
- **Right Stick**: Secondary/rotation control

Both joysticks support angle-based control with configurable speed rules based on stick direction.

## How It Works

1. **Input Detection**: pygame captures gamepad input events
2. **Angle Calculation**: Joystick positions are converted to angles (0-360°)
3. **Rule Matching**: Angles are matched against configured rules to determine speed
4. **ROS Publishing**: Speed values are published to specified ROS topics as Float32MultiArray messages
5. **Real-time Updates**: Continuous loop processes input and publishes updates

## Testing

Use `test.py` to test your gamepad connectivity and view raw input values:

```bash
python test.py
```

This will display:
- Connected controller information
- Button press/release events
- Joystick positions and angles
- Hat/D-pad states

## Troubleshooting

### No Controller Detected
- Ensure your gamepad is properly connected
- Check if pygame recognizes your controller with `test.py`
- Try reconnecting the controller

### Cannot Connect to ROS
- Verify rosbridge is running: `rosnode list | grep rosbridge`
- Check the host and port settings in `config.yaml`
- Ensure your ROS environment is properly sourced

### Joystick Not Responding
- Adjust deadzone values in `config.yaml`
- Check if joystick calibration is needed
- Verify angle ranges don't have gaps

## File Structure

```
├── main.py          # Main controller application
├── test.py          # Gamepad testing utility
├── config.yaml      # Configuration file
└── README.md        # This documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions
- Refer to the troubleshooting section

---

**Note**: This project is designed for educational and research purposes. Ensure proper safety measures when controlling physical robotic systems.