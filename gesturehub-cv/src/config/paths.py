from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

MODELS_DIR = ROOT_DIR / "models"

HAND_LANDMARKER_MODEL_PATH = MODELS_DIR / "hand_landmarker.task"
GESTURE_SVM_MODEL_PATH = MODELS_DIR / "gesture_model.xml"
GESTURE_DATA_PATH = MODELS_DIR / "gesture_data.csv"
