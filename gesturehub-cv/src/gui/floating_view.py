from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class FloatingView(QWidget):
    def __init__(self, parent=None):
        # Usar Window para ser independente, mas sempre no topo
        super().__init__(parent, Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        self.setWindowTitle("GestureHub - Mini View")
        self.resize(320, 240)
        self.setStyleSheet("background-color: #111827;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000000;")
        self.layout.addWidget(self.video_label)
        
    def update_frame(self, pixmap: QPixmap):
        """Atualiza a imagem mostrada na janela flutuante."""
        # Redimensionar pixmap para caber na janela, mantendo a proporção
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """Quando o usuário fecha a mini janela, apenas ocultamos."""
        self.hide()
        event.ignore()
