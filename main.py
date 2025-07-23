import os
import math
import time
import yaml
import pygame
import roslibpy

BTN_MAP = {
    0: "A", 1: "B", 2: "X", 3: "Y",
    4: "LB", 5: "RB", 6: "Back", 7: "Start",
    8: "Guide", 9: "LStick", 10: "RStick",
}

AXIS_LEFT  = (0, 1)   # (x, y)
AXIS_RIGHT = (2, 3)

AXIS_EPS = 0.05
DEADZONE_DEFAULT = 0.15

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def angle_from_axes(x, y, deadzone):
    y = -y
    r = math.hypot(x, y)
    if r < deadzone:
        return None
    ang = math.degrees(math.atan2(y, x))  # -180~180
    return (ang + 360) % 360

def pick_speed_from_rules(angle, rules):
    if angle is None:
        return None
    for rule in rules:
        a, b = rule['range']
        if a <= b:
            if a <= angle <= b:
                return rule['speed']
        else:
            # wrap，例如 [330, 30]
            if angle >= a or angle <= b:
                return rule['speed']
    return None

def build_publishers(client, topics):
    pubs = []
    for t in topics:
        pubs.append({
            'indices': t['indices'],
            'pub': roslibpy.Topic(client, t['name'], 'std_msgs/Float32MultiArray')
        })
    return pubs

def send_to_topics(publishers, vec):
    for item in publishers:
        indices = item['indices']
        data_part = [vec[i] for i in indices]
        msg = {
            'layout': {'dim': [], 'data_offset': 0},
            'data': data_part
        }
        item['pub'].publish(roslibpy.Message(msg))

# ---------- 主程式 ----------
def main(cfg_path):
    # 無頭環境可開：
    # os.environ["SDL_VIDEODRIVER"] = "dummy"
    # os.environ["SDL_AUDIODRIVER"] = "dummy"

    cfg = load_config(cfg_path)

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("沒有偵測到任何搖桿/控制器")
        return
    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"Joystick: {js.get_name()}")

    host = cfg['rosbridge']['host']
    port = cfg['rosbridge']['port']
    client = roslibpy.Ros(host=host, port=port)
    client.run()
    while not client.is_connected:
        time.sleep(0.1)
    print(f"Connected to rosbridge ws://{host}:{port}")

    publishers = build_publishers(client, cfg['ros_topics'])

    # 狀態
    last_axes = [0.0] * js.get_numaxes()
    current_vec = [0.0, 0.0, 0.0, 0.0]

    try:
        while True:
            for e in pygame.event.get():
                if e.type == pygame.JOYBUTTONDOWN:
                    name = BTN_MAP.get(e.button, f"BTN{e.button}")
                    if name in cfg['buttons']:
                        current_vec = cfg['buttons'][name]
                        send_to_topics(publishers, current_vec)
                        print(f"[BTN DOWN] {name} -> {current_vec}")

                elif e.type == pygame.JOYAXISMOTION:
                    val = js.get_axis(e.axis)
                    if abs(val - last_axes[e.axis]) < AXIS_EPS:
                        continue
                    last_axes[e.axis] = val

                    lx = js.get_axis(AXIS_LEFT[0])
                    ly = js.get_axis(AXIS_LEFT[1])
                    left_cfg = cfg['axes_angle_map'].get('left_stick', {})
                    left_dead = left_cfg.get('deadzone', DEADZONE_DEFAULT)
                    left_angle = angle_from_axes(lx, ly, left_dead)
                    left_speed = None
                    if left_angle is not None and 'rules' in left_cfg:
                        left_speed = pick_speed_from_rules(left_angle, left_cfg['rules'])

                    rx = js.get_axis(AXIS_RIGHT[0])
                    ry = js.get_axis(AXIS_RIGHT[1])
                    right_cfg = cfg['axes_angle_map'].get('right_stick', {})
                    right_dead = right_cfg.get('deadzone', DEADZONE_DEFAULT)
                    right_angle = angle_from_axes(rx, ry, right_dead)
                    right_speed = None
                    if right_angle is not None and 'rules' in right_cfg:
                        right_speed = pick_speed_from_rules(right_angle, right_cfg['rules'])


                    if left_speed is not None:
                        current_vec = left_speed
                    if right_speed is not None:
                        current_vec = right_speed

                    if left_speed is not None or right_speed is not None:
                        send_to_topics(publishers, current_vec)
                        print(f"[AXIS] L={left_angle}°, R={right_angle}° -> {current_vec}")

                elif e.type == pygame.JOYBUTTONUP:
                    pass

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Bye")
    finally:
        for p in publishers:
            p['pub'].unadvertise()
        client.terminate()
        pygame.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python joy_to_ros.py config.yaml")
    else:
        main(sys.argv[1])
