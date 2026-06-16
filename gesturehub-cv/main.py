import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.gui.styles import get_app_stylesheet

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Default clean look
    app.setStyleSheet(get_app_stylesheet())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
