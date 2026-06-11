from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QButtonGroup, QPushButton, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from .styles import (
    get_processing_view_style, get_processing_card_style,
    get_processing_title_style, get_processing_description_style,
    get_roi_style, get_roi_label_style
)

PROCESSING_MODES = [
    "Original",
    "HSV",
    "Máscara / Threshold",
    "Contornos",
    "Resultado final",
    "Grade"
]

class ProcessingView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.is_running = False
        self.current_mode = "Original"
        
        # Armazena as imagens reais mais recentes para cada modo (usado no resizeEvent)
        self._last_pixmaps: dict[str, QPixmap] = {}
        
        # Internal layouts and widgets references
        self.view_container = None
        self.view_layout = None
        
        # Single View widgets
        self.single_view_frame = None
        self.single_view_label = None
        self.single_view_title = None
        
        # Grid View widgets
        self.grid_cards = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header / Title
        title_label = QLabel("Processamento OpenCV")
        title_label.setStyleSheet(get_processing_title_style())
        self.main_layout.addWidget(title_label)
        
        # Mode Controls
        self._create_controls()
        
        # View Container (this will hold either single view or grid view)
        self.view_container = QWidget()
        self.view_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.view_layout = QVBoxLayout(self.view_container)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.view_container, stretch=1)
        
        # Initialize default view
        self.show_single_view(self.current_mode)
        
    def _create_controls(self):
        controls_layout = QHBoxLayout()
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        for i, mode in enumerate(PROCESSING_MODES):
            btn = QPushButton(mode)
            btn.setCheckable(True)
            if mode == self.current_mode:
                btn.setChecked(True)
                
            self.btn_group.addButton(btn)
            controls_layout.addWidget(btn)
            
            btn.toggled.connect(lambda checked, m=mode: self.set_mode(m) if checked else None)
            
        controls_layout.addStretch()
        self.main_layout.addLayout(controls_layout)
        
    def set_running(self, is_running: bool):
        self.is_running = is_running
        if not is_running:
            self._last_pixmaps.clear()
        self._update_placeholders()
        
    def set_mode(self, mode: str):
        if self.current_mode == mode:
            return
            
        self.current_mode = mode
        
        if mode == "Grade":
            self.show_grid_view()
        else:
            self.show_single_view(mode)
            
        # Reaplicar imagens armazenadas em cache logo apos trocar o modo, para não piscar placeholder se a camerta ta on
        self._refresh_current_pixmaps()
            
    def _clear_view(self):
        # Remove all widgets from the view layout
        while self.view_layout.count():
            item = self.view_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        self.single_view_frame = None
        self.single_view_label = None
        self.single_view_title = None
        self.grid_cards.clear()

    def show_single_view(self, mode: str):
        self._clear_view()
        
        self.single_view_frame = QFrame()
        self.single_view_frame.setStyleSheet(get_processing_view_style())
        
        layout = QVBoxLayout(self.single_view_frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.single_view_title = QLabel(f"Modo de visualização: {mode}")
        self.single_view_title.setStyleSheet(get_processing_title_style())
        self.single_view_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        description_text = self._get_mode_description(mode)
        desc_label = QLabel(description_text)
        desc_label.setStyleSheet(get_processing_description_style())
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        header_layout = QVBoxLayout()
        header_layout.addWidget(self.single_view_title)
        header_layout.addWidget(desc_label)
        header_layout.setSpacing(2)
        
        layout.addLayout(header_layout)
        layout.addStretch()
        
        self.single_view_label = QLabel()
        self.single_view_label.setMinimumSize(1, 1)
        self.single_view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.single_view_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.single_view_label)
        
        layout.addStretch()
        
        self.view_layout.addWidget(self.single_view_frame)
        self._update_placeholders()

    def show_grid_view(self):
        self._clear_view()
        
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(10)
        
        modes_to_show = [
            ("Original", 0, 0),
            ("HSV", 0, 1),
            ("Contornos", 1, 0),
            ("Resultado final", 1, 1)
        ]
        
        for mode, row, col in modes_to_show:
            card, img_label = self._create_processing_card(mode, self._get_mode_description(mode))
            self.grid_cards[mode] = img_label
            grid_layout.addWidget(card, row, col)
            
        self.view_layout.addWidget(grid_container)
        self._update_placeholders()

    def _create_processing_card(self, title: str, description: str):
        card = QFrame()
        card.setStyleSheet(get_processing_card_style())
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(get_processing_title_style())
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(get_processing_description_style())
        
        img_label = QLabel()
        img_label.setMinimumSize(1, 1)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(img_label, stretch=1)
        layout.addStretch()
        
        return card, img_label

    def _get_mode_description(self, mode: str) -> str:
        descriptions = {
            "Original": "Frame original capturado da webcam.",
            "HSV": "Conversão de cor BGR para HSV usando OpenCV.",
            "Máscara / Threshold": "Máscara binária gerada por threshold para demonstrar segmentação.",
            "Contornos": "Visualização estrutural com landmarks da mão ou bordas Canny.",
            "Resultado final": "Frame anotado com landmarks, gesto, evento e status.",
            "Grade": "Comparação simultânea das principais etapas de processamento."
        }
        return descriptions.get(mode, "")

    def _update_placeholders(self):
        text = "Aguardando frame..." if self.is_running else "Câmera desligada"
        
        if self.current_mode == "Grade":
            for label in self.grid_cards.values():
                if not self.is_running:
                    label.clear()
                if not label.pixmap() or label.pixmap().isNull():
                    label.setText(text)
        else:
            if self.single_view_label:
                if not self.is_running:
                    self.single_view_label.clear()
                if not self.single_view_label.pixmap() or self.single_view_label.pixmap().isNull():
                    self.single_view_label.setText(text)

    def _set_label_pixmap(self, label: QLabel, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            return
            
        label.clear() # limpa o texto do placeholder
        scaled_pixmap = pixmap.scaled(
            label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def update_frame(self, mode: str, pixmap: QPixmap) -> None:
        """
        Recebe o frame recem-processado do modo correspondente, guarda no dicionário 
        e atualiza sua respectiva QLabel na tela.
        """
        if pixmap is None or pixmap.isNull():
            return
            
        self._last_pixmaps[mode] = pixmap
            
        if self.current_mode == "Grade":
            label = self.grid_cards.get(mode)
            if label is not None:
                self._set_label_pixmap(label, pixmap)
        else:
            if mode == self.current_mode and self.single_view_label is not None:
                self._set_label_pixmap(self.single_view_label, pixmap)
                
    def _refresh_current_pixmaps(self) -> None:
        """Força o redesenho dos pixmaps correntes na UI usando o estado interno guardado"""
        if not self.is_running:
            return
            
        if self.current_mode == "Grade":
            for mode_key, label in self.grid_cards.items():
                if mode_key in self._last_pixmaps:
                    self._set_label_pixmap(label, self._last_pixmaps[mode_key])
        else:
            if self.current_mode in self._last_pixmaps and self.single_view_label is not None:
                self._set_label_pixmap(self.single_view_label, self._last_pixmaps[self.current_mode])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_current_pixmaps()
