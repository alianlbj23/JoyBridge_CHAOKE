import os
# 無頭環境用：
# os.environ["SDL_VIDEODRIVER"] = "dummy"
# os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import time
import math
DEADZONE = 0.15  # 小於這個半徑就當作沒有動

BTN_MAP = {
    0: "A", 1: "B", 2: "X", 3: "Y",
    4: "LB", 5: "RB", 6: "Back", 7: "Start",
    8: "Guide", 9: "LStick", 10: "RStick",
}

AXIS_EPS = 0.05   # 軸變動門檻，超過才視為「有動」
last_axes = []
last_hats  = []

def axes_to_angle(x, y, invert_y=True):
    """將搖桿XY轉成 0~360 度。回傳 (angle_deg, radius)。"""
    if invert_y:
        y = -y  # pygame 的 Y 通常上是負，這行可視需要移除
    r = math.hypot(x, y)
    if r < DEADZONE:
        return None, r
    ang = math.degrees(math.atan2(y, x))  # -180~180
    ang = (ang + 360) % 360               # 0~360
    return ang, r

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("沒有偵測到任何搖桿/控制器")
        return

    js = pygame.joystick.Joystick(0)
    js.init()
    print(f"使用控制器：{js.get_name()}，按鈕數：{js.get_numbuttons()}，軸數：{js.get_numaxes()}，帽數：{js.get_numhats()}")

    global last_axes, last_hats
    last_axes = [0.0] * js.get_numaxes()
    last_hats  = [(0, 0)] * js.get_numhats()

    try:
        while True:
            # 取出所有事件
            for e in pygame.event.get():
                if e.type == pygame.JOYBUTTONDOWN:
                    print(f"[BTN DOWN] {BTN_MAP.get(e.button, f'BTN{e.button}')}")
                elif e.type == pygame.JOYBUTTONUP:
                    print(f"[BTN UP]   {BTN_MAP.get(e.button, f'BTN{e.button}')}")
                elif e.type == pygame.JOYAXISMOTION:
                    # 更新快取
                    val = js.get_axis(e.axis)
                    if abs(val - last_axes[e.axis]) >= AXIS_EPS:
                        last_axes[e.axis] = val

                        # 左搖桿(0,1)
                        lx, ly = last_axes[0], last_axes[1]
                        left_ang, left_r = axes_to_angle(lx, ly)

                        # 右搖桿(2,3)
                        rx, ry = last_axes[2], last_axes[3]
                        right_ang, right_r = axes_to_angle(rx, ry)

                        out = []
                        if left_ang is not None:
                            out.append(f"LeftStick: {left_ang:.1f}° (r={left_r:.2f})")
                        if right_ang is not None:
                            out.append(f"RightStick: {right_ang:.1f}° (r={right_r:.2f})")

                        if out:
                            print(" | ".join(out))

                elif e.type == pygame.JOYHATMOTION:
                    hat_val = js.get_hat(e.hat)
                    if hat_val != last_hats[e.hat]:
                        print(f"[HAT] {e.hat} -> {hat_val}")
                        last_hats[e.hat] = hat_val

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n離開")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
