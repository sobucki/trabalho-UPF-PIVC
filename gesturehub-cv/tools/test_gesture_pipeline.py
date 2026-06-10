import sys
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.vision.gesture_pipeline import GesturePipeline

def main():
    print("Iniciando teste do GesturePipeline...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Aviso: Webcam nao pode ser aberta no ambiente de teste atual.")
        print("Finalizando teste com graciosidade.")
        return

    with GesturePipeline() as pipeline:
        timestamp_ms = 0

        print("Pressione 'q' para sair da janela de teste (se renderizada).")
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            result = pipeline.process_frame(frame, timestamp_ms)
            timestamp_ms += 33

            print(
                f"Gesto: {result['gesture']} | "
                f"Evento: {result['event']} | "
                f"Status: {result['status']} | "
                f"Confianca: {result['confidence']} | "
                f"Cooldown: {result['cooldown']}"
            )

            cv2.imshow("GesturePipeline Test", result["result_frame"])

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
