import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config.paths import validate_model_files

def main():
    missing = validate_model_files()
    if missing:
        print("Arquivos ausentes:")
        for f in missing:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("Todos os assets necessários foram encontrados.")

if __name__ == "__main__":
    main()
