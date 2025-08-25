import math
import yaml

AXIS_EPS = 0.05
DEADZONE_DEFAULT = 0.15

class Utils:
    @staticmethod
    def load_config(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def angle_from_axes(x, y, deadzone=DEADZONE_DEFAULT):
        y = -y
        r = math.hypot(x, y)
        if r < deadzone:
            return None
        angle = math.degrees(math.atan2(y, x))
        return (angle + 360) % 360

    @staticmethod
    def pick_speed_from_rules(angle, rules):
        if angle is None:
            return None
        for rule in rules:
            a, b = rule['range']
            if a <= b:
                if a <= angle <= b:
                    return rule['speed']
            else:  # wrap-around
                if angle >= a or angle <= b:
                    return rule['speed']
        return None
