import sys
from app import JoyToRosApp

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py config.yaml")
    else:
        app = JoyToRosApp(sys.argv[1])
        app.run()
