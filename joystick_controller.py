import pygame
import time
from utils import DEADZONE_DEFAULT

# btn mapping
BTN_MAP = {
    0: "A", 1: "B", 2: "LB", 3: "X",
    4: "Y", 5: "RB", 6: "Back", 7: "Start",
    8: "Guide", 9: "LStick", 10: "RStick",
}

AXIS_LEFT = (0, 1)

class JoystickController:
    def __init__(self, cfg):
        self.cfg = cfg
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.last_axes = []
        self._reconnect_joystick()

        self.current_vec = [0.0, 0.0, 0.0, 0.0]
        cmd_vel_cfg = self.cfg.get('cmd_vel', {})
        self.max_linear_speed = cmd_vel_cfg.get('max_linear_speed', 0.5)
        self.max_angular_speed = cmd_vel_cfg.get('max_angular_speed', 2.0)
        self.cmd_vel_deadzone = cmd_vel_cfg.get('deadzone', DEADZONE_DEFAULT)
        self.current_cmd_vel = {
            'linear_x': 0.0,
            'angular_z': 0.0
        }
        self.last_published_cmd_vel = None

        # 初始化 AY 軸角度
        control_cfg = self.cfg.get('robot_arm_control', {})
        self.ay_axis_angle = control_cfg.get('ay_axis_initial_angle', 0.0)
        max_angle = control_cfg.get('ay_axis_max_angle', 90.0)
        min_angle = control_cfg.get('ay_axis_min_angle', -90.0)
        self.ay_axis_angle = max(min_angle, min(self.ay_axis_angle, max_angle))
        self.last_ay_button = None

    def _reconnect_joystick(self, ros_pub=None):
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.last_axes = [0.0] * self.joystick.get_numaxes()
            print(f"Joystick connected: {self.joystick.get_name()}")
        else:
            if self.joystick is not None:
                print("Joystick disconnected. Waiting for reconnection...")
                if ros_pub and 'BTN13' in self.cfg['buttons']:
                    btn13_signal = self.cfg['buttons']['BTN13']
                    ros_pub.send(btn13_signal)
                    print(f"[BTN DISCONNECTED] -> {btn13_signal}")
            else:
                print("No joystick detected. Waiting for connection...")
            self.joystick = None
            self.last_axes = []

    def process_events(self, ros_pub):
        if self.joystick is None:
            self._reconnect_joystick(ros_pub)
            time.sleep(1) # wait a bit before retrying
            return

        try:
            # This is the core event loop
            for e in pygame.event.get():
                if e.type == pygame.JOYDEVICEADDED:
                    if self.joystick is None:
                        print("Joystick device added. Attempting to connect.")
                        self._reconnect_joystick(ros_pub)
                        break  # Exit the event loop and let the main loop continue
                elif e.type == pygame.JOYDEVICEREMOVED:
                    print("Joystick device removed. Attempting to reconnect.")
                    self._reconnect_joystick(ros_pub)
                    break  # Exit the event loop and let the main loop continue
                elif e.type == pygame.JOYBUTTONDOWN:
                    self._handle_button_down(e, ros_pub)
                elif e.type == pygame.JOYAXISMOTION:
                    self._handle_axis_motion(e)
        except pygame.error as e:
            print(f"Joystick error: {e}. Attempting to reconnect.")
            self._reconnect_joystick(ros_pub)

        self._publish_cmd_vel(ros_pub)

    def _handle_button_down(self, event, ros_pub):
        name = BTN_MAP.get(event.button, f"BTN{event.button}")
        
        # 處理機械手臂按鈕 (A 和 Y)
        if name in ['A', 'Y'] and 'robot_arm_joints' in self.cfg:
            if name in self.cfg['robot_arm_joints']:
                self.last_ay_button = name
                joint_angles = self.cfg['robot_arm_joints'][name][:]
                joint_angles[-1] = self.ay_axis_angle
                ros_pub.send_arm_joints(joint_angles)
                print(f"[ARM BTN] {name} -> {joint_angles}°")
                return

        # 處理X, B 手臂角度調整
        if name in ['X', 'B'] and 'robot_arm_control' in self.cfg and self.last_ay_button:
            control_cfg = self.cfg['robot_arm_control']
            increment = control_cfg.get('angle_increment', 10.0)
            decrement = control_cfg.get('angle_decrement', -10.0)
            max_angle = control_cfg.get('ay_axis_max_angle', 90.0)
            min_angle = control_cfg.get('ay_axis_min_angle', -90.0)
            
            if name == 'B':
                self.ay_axis_angle += increment
            elif name == 'X':
                self.ay_axis_angle += decrement

            # 限制角度在最大值和最小值之間
            self.ay_axis_angle = max(min_angle, min(self.ay_axis_angle, max_angle))

            joint_angles = self.cfg['robot_arm_joints'][self.last_ay_button][:]
            joint_angles[-1] = self.ay_axis_angle
            ros_pub.send_arm_joints(joint_angles)
            print(f"[ARM BTN] {name} -> New Angle: {self.ay_axis_angle}°")
            return

        # 處理車輪控制按鈕
        if name in self.cfg['buttons']:
            self.current_vec = self.cfg['buttons'][name]
            ros_pub.send(self.current_vec)
            print(f"[BTN DOWN] {name} -> {self.current_vec}")

    def _handle_axis_motion(self, event):
        val = self.joystick.get_axis(event.axis)
        if abs(val - self.last_axes[event.axis]) < 0.05:
            return
        self.last_axes[event.axis] = val

        self.current_cmd_vel = self._process_cmd_vel_stick(AXIS_LEFT)

    def _process_cmd_vel_stick(self, axis_tuple):
        x = self.joystick.get_axis(axis_tuple[0])
        y = self.joystick.get_axis(axis_tuple[1])

        if abs(x) < self.cmd_vel_deadzone:
            x = 0.0
        if abs(y) < self.cmd_vel_deadzone:
            y = 0.0

        linear_x = -y * self.max_linear_speed

        return {
            'linear_x': linear_x,
            'angular_z': -x * self.max_angular_speed
        }

    def _publish_cmd_vel(self, ros_pub):
        self.current_cmd_vel = self._process_cmd_vel_stick(AXIS_LEFT)
        ros_pub.send_cmd_vel(
            self.current_cmd_vel['linear_x'],
            self.current_cmd_vel['angular_z']
        )
        rounded_cmd_vel = (
            round(self.current_cmd_vel['linear_x'], 3),
            round(self.current_cmd_vel['angular_z'], 3)
        )
        if rounded_cmd_vel != self.last_published_cmd_vel:
            self.last_published_cmd_vel = rounded_cmd_vel
            print(
                f"[cmd_vel] linear.x={self.current_cmd_vel['linear_x']:.3f} m/s, "
                f"angular.z={self.current_cmd_vel['angular_z']:.3f} rad/s"
            )
