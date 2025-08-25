import time
import pygame
import roslibpy
from utils import Utils
from joystick_controller import JoystickController
from ros_publisher import RosPublisher

class JoyToRosApp:
    def __init__(self, cfg_path):
        self.cfg = Utils.load_config(cfg_path)
        self.ros_client = roslibpy.Ros(
            host=self.cfg['rosbridge']['host'],
            port=self.cfg['rosbridge']['port']
        )
        self.joystick_ctrl = JoystickController(self.cfg)
        self.ros_pub = None

    def run(self):
        self.ros_client.run()
        while not self.ros_client.is_connected:
            time.sleep(0.1)
        print(f"Connected to rosbridge ws://{self.cfg['rosbridge']['host']}:{self.cfg['rosbridge']['port']}")

        self.ros_pub = RosPublisher(
            self.ros_client, 
            self.cfg['ros_topics'],
            self.cfg.get('robot_arm_topic')
        )

        try:
            while True:
                self.joystick_ctrl.process_events(self.ros_pub)
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Bye")
        finally:
            self.ros_pub.close()
            self.ros_client.terminate()
            pygame.quit()
