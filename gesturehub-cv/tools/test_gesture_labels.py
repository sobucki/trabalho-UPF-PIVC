import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.vision.gesture_labels import (
    get_gesture_info,
    get_gesture_name,
    get_event_name,
    is_known_label,
    list_supported_gestures,
)

def main():
    print("Gestos suportados:")
    for item in list_supported_gestures():
        print(item)

    print("\nTestes unitarios isolados:")
    print(get_gesture_info(0))
    print(get_gesture_name(1))
    print(get_event_name(2))
    print(is_known_label(99))

if __name__ == "__main__":
    main()
