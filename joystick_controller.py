import pygame
import time
from utils import Utils, DEADZONE_DEFAULT

# btn mapping
BTN_MAP = {
    0: "A", 1: "B", 2: "LB", 3: "X",
    4: "Y", 5: "RB", 6: "Back", 7: "Start",
    8: "Guide", 9: "LStick", 10: "RStick",
}

AXIS_LEFT = (0, 1)
AXIS_RIGHT = (2, 3)

class JoystickController:
    def __init__(self, cfg):
        self.cfg = cfg
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.last_axes = []
        self._reconnect_joystick()

        self.current_vec = [0.0, 0.0, 0.0, 0.0]

        # 初始化 AY 軸角度
        control_cfg = self.cfg.get('robot_arm_control', {})
        self.ay_axis_angle = control_cfg.get('ay_axis_initial_angle', 0.0)
        max_angle = control_cfg.get('ay_axis_max_angle', 90.0)
        min_angle = control_cfg.get('ay_axis_min_angle', -90.0)
        self.ay_axis_angle = max(min_angle, min(self.ay_axis_angle, max_angle))
        self.last_ay_button = None

    def _reconnect_joystick(self):
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
            else:
                print("No joystick detected. Waiting for connection...")
            self.joystick = None
            self.last_axes = []

    def process_events(self, ros_pub):
        if self.joystick is None:
            self._reconnect_joystick()
            time.sleep(1) # wait a bit before retrying
            return

        try:
            # This is the core event loop
            for e in pygame.event.get():
                if e.type == pygame.JOYDEVICEADDED:
                    if self.joystick is None:
                        print("Joystick device added. Attempting to connect.")
                        self._reconnect_joystick()
                        break  # Exit the event loop and let the main loop continue
                elif e.type == pygame.JOYDEVICEREMOVED:
                    print("Joystick device removed. Attempting to reconnect.")
                    self._reconnect_joystick()
                    break  # Exit the event loop and let the main loop continue
                elif e.type == pygame.JOYBUTTONDOWN:
                    self._handle_button_down(e, ros_pub)
                elif e.type == pygame.JOYAXISMOTION:
                    self._handle_axis_motion(e, ros_pub)
        except pygame.error as e:
            print(f"Joystick error: {e}. Attempting to reconnect.")
            self._reconnect_joystick()

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

    def _handle_axis_motion(self, event, ros_pub):
        val = self.joystick.get_axis(event.axis)
        if abs(val - self.last_axes[event.axis]) < 0.05:
            return
        self.last_axes[event.axis] = val

        left_speed = self._process_stick(AXIS_LEFT, 'left_stick')
        right_speed = self._process_stick(AXIS_RIGHT, 'right_stick')

        if left_speed is not None:
            self.current_vec = left_speed
        if right_speed is not None:
            self.current_vec = right_speed

        if left_speed is not None or right_speed is not None:
            ros_pub.send(self.current_vec)
            print(f"[AXIS] L={self._stick_angle_str('left_stick')}, "
                  f"R={self._stick_angle_str('right_stick')} -> {self.current_vec}")

    def _process_stick(self, axis_tuple, stick_name):
        x = self.joystick.get_axis(axis_tuple[0])
        y = self.joystick.get_axis(axis_tuple[1])
        stick_cfg = self.cfg['axes_angle_map'].get(stick_name, {})
        dead = stick_cfg.get('deadzone', DEADZONE_DEFAULT)
        angle = Utils.angle_from_axes(x, y, dead)
        if angle is not None and 'rules' in stick_cfg:
            return Utils.pick_speed_from_rules(angle, stick_cfg['rules'])
        return None

    def _stick_angle_str(self, stick_name):
        axis_tuple = AXIS_LEFT if stick_name == 'left_stick' else AXIS_RIGHT
        x = self.joystick.get_axis(axis_tuple[0])
        y = self.joystick.get_axis(axis_tuple[1])
        angle = Utils.angle_from_axes(x, y, DEADZONE_DEFAULT)
        return f"{angle:.1f}°" if angle is not None else "None"