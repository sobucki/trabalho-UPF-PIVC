import cv2
import numpy as np
import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "models" / "gesture_data_hagrid.csv"
MODEL_PATH = Path(__file__).parent.parent / "models" / "gesture_model.xml"

GESTURES = [
    "call", "dislike", "fist", "four", "like", "mute",
    "ok", "one", "palm", "peace", "peace_inverted", "rock",
    "stop", "stop_inverted", "three", "three2", "two_up", "two_up_inverted",
]


def load_data():
    X, y = [], []
    with open(CSV_PATH, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if not row:
                continue
            X.append([float(v) for v in row[:-1]])
            y.append(int(row[-1]))
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def main():
    print("=== Treinamento SVM com HaGRID ===\n")

    if not CSV_PATH.exists():
        print(f"CSV não encontrado: {CSV_PATH}")
        print("Execute primeiro: python tools/convert_hagrid.py")
        return

    X, y = load_data()
    print(f"Total de amostras: {len(X)}")
    for idx, name in enumerate(GESTURES):
        count = np.sum(y == idx)
        print(f"  {idx:2d} {name:20s}: {count} amostras")

    # Embaralhar
    indices = np.arange(len(X))
    np.random.seed(42)
    np.random.shuffle(indices)
    X, y = X[indices], y[indices]

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    print(f"\nTreino: {len(X_train)} | Teste: {len(X_test)}")

    # Treinar SVM
    print("\nTreinando SVM...")
    svm = cv2.ml.SVM_create()
    svm.setType(cv2.ml.SVM_C_SVC)
    svm.setKernel(cv2.ml.SVM_RBF)
    svm.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 1000, 1e-6))
    svm.setGamma(0.5)
    svm.setC(10)
    svm.train(X_train, cv2.ml.ROW_SAMPLE, y_train)

    # Avaliar
    _, y_pred = svm.predict(X_test)
    y_pred = y_pred.flatten().astype(np.int32)
    accuracy = np.mean(y_pred == y_test) * 100
    print(f"Acurácia: {accuracy:.2f}%")

    # Matriz de confusão resumida (por classe)
    print("\nAcurácia por classe:")
    for idx, name in enumerate(GESTURES):
        mask = y_test == idx
        if mask.sum() == 0:
            continue
        acc = np.mean(y_pred[mask] == idx) * 100
        print(f"  {idx:2d} {name:20s}: {acc:.1f}%")

    svm.save(str(MODEL_PATH))
    print(f"\nModelo salvo em: {MODEL_PATH}")


if __name__ == "__main__":
    main()
