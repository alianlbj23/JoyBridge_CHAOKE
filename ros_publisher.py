import roslibpy
import math
import time
class RosPublisher:
    def __init__(self, client, topics_config, arm_config=None):
        self.publishers = []
        for t in topics_config:
            self.publishers.append({
                'indices': t['indices'],
                'pub': roslibpy.Topic(client, t['name'], 'std_msgs/Float32MultiArray')
            })

        # 機械手臂發布器
        self.arm_publisher = None
        self.arm_config = arm_config
        if self.arm_config:
            self.arm_publisher = roslibpy.Topic(
                client,
                self.arm_config['name'],
                self.arm_config['msg_type']
            )

    def send_arm_joints(self, joint_angles_deg):
        """發送機械手臂關節角度 (輸入為度，轉換為弧度發布)"""
        if self.arm_publisher:
            # 將角度從度轉換為弧度
            joint_angles_rad = [math.radians(angle) for angle in joint_angles_deg]

            # 創建 JointTrajectory message
            msg = {
                'joint_names': self.arm_config.get('joint_names', []),
                'points': [
                    {
                        'positions': joint_angles_rad,
                        'velocities': [],
                        'accelerations': [],
                        'effort': [],
                        'time_from_start': {'secs': 1, 'nsecs': 0}
                    }
                ]
            }

            self.arm_publisher.publish(roslibpy.Message(msg))
            print(f"[ARM] Published joint angles: {joint_angles_deg}° -> {joint_angles_rad} rad")

    def send(self, vec):
        for item in self.publishers:
            data_part = [vec[i] for i in item['indices']]
            msg = {'layout': {'dim': [], 'data_offset': 0}, 'data': data_part}
            item['pub'].publish(roslibpy.Message(msg))

    def close(self):
        for item in self.publishers:
            item['pub'].unadvertise()
        if self.arm_publisher:
            self.arm_publisher.unadvertise()
