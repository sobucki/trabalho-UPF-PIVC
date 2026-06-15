import json
import csv
import os
import numpy as np
from pathlib import Path

HAGRID_DIR = Path(__file__).parent.parent.parent / "HAgrid" / "ann_train_val"
OUTPUT_CSV = Path(__file__).parent.parent / "models" / "gesture_data_hagrid.csv"

GESTURES = [
    "call", "dislike", "fist", "four", "like", "mute",
    "ok", "one", "palm", "peace", "peace_inverted", "rock",
    "stop", "stop_inverted", "three", "three2", "two_up", "two_up_inverted",
]

LABEL_MAP = {name: idx for idx, name in enumerate(GESTURES)}


def normalize_landmarks(landmarks):
    coords = np.array(landmarks, dtype=np.float32)  # shape (21, 2)
    wrist = coords[0]
    coords -= wrist
    max_dist = np.max(np.linalg.norm(coords, axis=1))
    if max_dist == 0:
        return None
    return (coords / max_dist).flatten()


def convert():
    rows = []

    for gesture_name in GESTURES:
        json_path = HAGRID_DIR / f"{gesture_name}.json"
        if not json_path.exists():
            print(f"[AVISO] Arquivo não encontrado: {json_path}")
            continue

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for sample in data.values():
            labels = sample.get("labels", [])
            landmarks_list = sample.get("landmarks", [])

            for label, landmarks in zip(labels, landmarks_list):
                if label != gesture_name:
                    continue
                if len(landmarks) != 21:
                    continue

                features = normalize_landmarks(landmarks)
                if features is None:
                    continue

                rows.append(list(features) + [LABEL_MAP[gesture_name]])
                count += 1

        print(f"  {gesture_name:20s} (label {LABEL_MAP[gesture_name]:2d}): {count} amostras")

    if not rows:
        print("Nenhuma amostra extraída. Verifique o caminho do HaGRID.")
        return

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        header = [f"f{i}" for i in range(42)] + ["label"]
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\nTotal: {len(rows)} amostras salvas em {OUTPUT_CSV}")
    print("\nMapeamento de labels:")
    for name, idx in LABEL_MAP.items():
        print(f"  {idx:2d} = {name}")


if __name__ == "__main__":
    print("=== Conversão HaGRID → CSV ===\n")
    convert()
