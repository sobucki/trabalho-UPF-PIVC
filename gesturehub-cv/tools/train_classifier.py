import cv2
import numpy as np
import csv
import os

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config.paths import GESTURE_DATA_PATH, GESTURE_SVM_MODEL_PATH

CSV_PATH = str(GESTURE_DATA_PATH)
MODEL_PATH = str(GESTURE_SVM_MODEL_PATH)

def carregar_dados():
    """Lê o arquivo CSV de landmarks e retorna os arrays X (características) e y (rótulos)."""
    if not os.path.exists(CSV_PATH):
        print(f"Erro: O arquivo de dados '{CSV_PATH}' não existe. Execute o collect_data.py primeiro.")
        return None, None
        
    X = []
    y = []
    
    with open(CSV_PATH, mode='r') as f:
        reader = csv.reader(f)
        header = next(reader) # Pular cabeçalho
        
        for row in reader:
            if not row:
                continue
            # As primeiras 42 colunas são as características (features)
            features = [float(val) for val in row[:-1]]
            # A última coluna é o rótulo (label)
            label = int(row[-1])
            
            X.append(features)
            y.append(label)
            
    # Converter para arrays numpy com tipos exigidos pelo OpenCV ML:
    # X deve ser float32, y deve ser int32 (como vetor coluna ou vetor linha)
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)
    
    return X, y

def main():
    print("=== Treinamento do Classificador de Gestos (OpenCV SVM) ===")
    
    # 1. Carregar os dados
    X, y = carregar_dados()
    if X is None or len(X) == 0:
        return
        
    print(f"Total de amostras carregadas: {len(X)}")
    for lbl in np.unique(y):
        contagem = np.sum(y == lbl)
        nome_gesto = {0: "Mao Aberta", 1: "Punho Fechado", 2: "Apontar Direita"}.get(lbl, "Desconhecido")
        print(f" - Classe {lbl} ({nome_gesto}): {contagem} amostras")
        
    if len(np.unique(y)) < 2:
        print("Erro: É necessário ter pelo menos 2 classes diferentes coletadas para treinar o classificador.")
        return

    # 2. Embaralhar e dividir em Treino (80%) e Teste (20%)
    indices = np.arange(len(X))
    np.random.seed(42)
    np.random.shuffle(indices)
    
    X = X[indices]
    y = y[indices]
    
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"\nDividindo dados: {len(X_train)} amostras para treino, {len(X_test)} para teste.")

    # 3. Configurar e treinar o classificador SVM da OpenCV
    print("Treinando o modelo SVM...")
    svm = cv2.ml.SVM_create()
    
    # Configurações do SVM
    svm.setType(cv2.ml.SVM_C_SVC)           # Classificação multiclasse C-Support Vector Classification
    svm.setKernel(cv2.ml.SVM_LINEAR)        # Kernel linear é muito bom e rápido para landmarks de mão
    svm.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER, 1000, 1e-6))
    
    # Treinar o classificador
    # cv2.ml.ROW_SAMPLE indica que cada linha do array representa uma amostra
    svm.train(X_train, cv2.ml.ROW_SAMPLE, y_train)

    # 4. Avaliar o modelo no conjunto de teste
    print("Avaliando o modelo no conjunto de teste...")
    _, y_pred = svm.predict(X_test)
    
    # Converter para arrays de 1 dimensão para calcular métricas
    y_pred = y_pred.flatten().astype(np.int32)
    y_test = y_test.flatten()
    
    acuracia = np.mean(y_pred == y_test) * 100
    print(f"\nAcurácia do modelo no teste: {acuracia:.2f}%")
    
    # Exibir matriz de confusão simplificada
    print("\nMatriz de Confusão:")
    classes = np.unique(y)
    print("Real \\ Pred ->", end="")
    for c in classes:
        print(f"\t[{c}]", end="")
    print()
    
    for real in classes:
        print(f"[{real}]", end="")
        for pred in classes:
            count = np.sum((y_test == real) & (y_pred == pred))
            print(f"\t{count}", end="")
        print()

    # 5. Salvar o modelo treinado
    svm.save(MODEL_PATH)
    print(f"\nModelo salvo com sucesso em: {MODEL_PATH}")

if __name__ == "__main__":
    main()
