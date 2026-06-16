from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

MODELS_DIR = ROOT_DIR / "models"

HAND_LANDMARKER_MODEL_PATH = MODELS_DIR / "hand_landmarker.task"
GESTURE_SVM_MODEL_PATH = MODELS_DIR / "gesture_model.xml"
GESTURE_DATA_PATH = MODELS_DIR / "gesture_data.csv"

def validate_model_files() -> list[str]:
    missing_files = []

    required_files = [
        HAND_LANDMARKER_MODEL_PATH,
        GESTURE_SVM_MODEL_PATH,
        GESTURE_DATA_PATH,
    ]

    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))

    return missing_files
