from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QGroupBox, QGridLayout,
    QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt, Slot

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GestureHub CV")
        self.resize(900, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.is_running = False
        
        self._setup_ui()
        
    def _setup_ui(self):
        self._create_header()
        self._create_content()
        self._create_visualization_controls()
        self._create_footer_controls()
        
    def _create_header(self):
        header_layout = QHBoxLayout()
        
        title_label = QLabel("<b>GestureHub CV</b>")
        title_label.setStyleSheet("font-size: 24px;")
        
        self.integration_label = QLabel("Integração: Apresentações | PARADO")
        self.integration_label.setStyleSheet("font-size: 16px;")
        self.integration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.integration_label)
        
        self.main_layout.addLayout(header_layout)
        
    def _create_content(self):
        content_layout = QHBoxLayout()
        self._create_camera_area(content_layout)
        self._create_recognition_panel(content_layout)
        self.main_layout.addLayout(content_layout)

    def _create_camera_area(self, parent_layout):
        # Frame containing camera elements
        camera_container = QFrame()
        camera_container.setStyleSheet("background-color: #1e1e1e;")
        camera_container.setMinimumSize(640, 480)
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Display label for current visual mode
        self.vis_mode_label = QLabel("Modo de visualização: Original")
        self.vis_mode_label.setStyleSheet("color: white; font-size: 14px;")
        self.vis_mode_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        camera_layout.addWidget(self.vis_mode_label)
        camera_layout.addStretch()
        
        self.camera_label = QLabel("Câmera desligada")
        self.camera_label.setStyleSheet("color: #aaaaaa; font-size: 20px;")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_layout.addWidget(self.camera_label)
        
        # Simulated ROI Frame
        self.roi_frame = QFrame()
        self.roi_frame.setFixedSize(200, 200)
        self.roi_frame.setStyleSheet("""
            QFrame {
                border: 2px dashed #4caf50;
                background-color: transparent;
            }
        """)
        roi_layout = QVBoxLayout(self.roi_frame)
        self.roi_label = QLabel("Área de controle da mão")
        self.roi_label.setStyleSheet("color: #4caf50; border: none;")
        self.roi_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        roi_layout.addWidget(self.roi_label)
        self.roi_frame.setVisible(False)
        camera_layout.addWidget(self.roi_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        
        camera_layout.addStretch()
        parent_layout.addWidget(camera_container, stretch=2)

    def _create_recognition_panel(self, parent_layout):
        self.recognition_group = QGroupBox("Painel de reconhecimento")
        panel_layout = QVBoxLayout(self.recognition_group)
        panel_layout.setSpacing(15)
        
        self.gesto_value = self._create_recognition_field(panel_layout, "Gesto detectado", "-")
        self.evento_value = self._create_recognition_field(panel_layout, "Evento gerado", "-")
        self.comando_value = self._create_recognition_field(panel_layout, "Comando executado", "-")
        self.confianca_value = self._create_recognition_field(panel_layout, "Confiança", "-")
        self.status_value = self._create_recognition_field(panel_layout, "Status", "Parado")
        self.cooldown_value = self._create_recognition_field(panel_layout, "Cooldown", "-")
        
        panel_layout.addStretch()
        parent_layout.addWidget(self.recognition_group, stretch=1)

    def _create_recognition_field(self, parent_layout, title, default_text):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: gray; font-size: 12px;")
        
        value_label = QLabel(default_text)
        value_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        parent_layout.addWidget(container)
        return value_label

    def _create_visualization_controls(self):
        vis_layout = QHBoxLayout()
        vis_label = QLabel("Visualização:")
        vis_label.setStyleSheet("font-weight: bold;")
        vis_layout.addWidget(vis_label)
        
        self.vis_group = QButtonGroup(self)
        
        modes = ["Original", "Segmentada", "Contornos", "Resultado final"]
        for i, mode in enumerate(modes):
            rb = QRadioButton(mode)
            if i == 0:
                rb.setChecked(True)
            rb.toggled.connect(lambda checked, m=mode: self._set_visualization_mode(m) if checked else None)
            self.vis_group.addButton(rb)
            vis_layout.addWidget(rb)
            
        vis_layout.addStretch()
        self.main_layout.addLayout(vis_layout)

    def _create_footer_controls(self):
        footer_layout = QHBoxLayout()
        
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.clicked.connect(lambda: self._set_running_state(True))
        
        self.btn_parar = QPushButton("Parar")
        self.btn_parar.setEnabled(False)
        self.btn_parar.clicked.connect(lambda: self._set_running_state(False))
        
        self.btn_simular = QPushButton("Simular gesto")
        self.btn_simular.clicked.connect(self._simulate_gesture)
        
        self.btn_configurar = QPushButton("Configurar comandos")
        self.btn_carregar_img = QPushButton("Carregar imagem")
        self.btn_carregar_vid = QPushButton("Carregar vídeo")
        
        footer_layout.addWidget(self.btn_iniciar)
        footer_layout.addWidget(self.btn_parar)
        footer_layout.addWidget(self.btn_simular)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_configurar)
        footer_layout.addWidget(self.btn_carregar_img)
        footer_layout.addWidget(self.btn_carregar_vid)
        
        self.main_layout.addLayout(footer_layout)

    def _set_running_state(self, running: bool):
        self.is_running = running
        
        if running:
            self.integration_label.setText("Integração: Apresentações | ATIVO")
            self.btn_iniciar.setEnabled(False)
            self.btn_parar.setEnabled(True)
            
            self.camera_label.setText("Aguardando frame da câmera...")
            self.camera_label.setVisible(True)
            self.roi_frame.setVisible(True)
            
            self.gesto_value.setText("Aguardando gesto...")
            self.evento_value.setText("-")
            self.comando_value.setText("-")
            self.confianca_value.setText("-")
            self.status_value.setText("Ativo")
            self.cooldown_value.setText("Pronto")
        else:
            self.integration_label.setText("Integração: Apresentações | PARADO")
            self.btn_iniciar.setEnabled(True)
            self.btn_parar.setEnabled(False)
            
            self._reset_recognition_state()

    def _reset_recognition_state(self):
        self.camera_label.setText("Câmera desligada")
        self.camera_label.setVisible(True)
        self.roi_frame.setVisible(False)
        
        self.gesto_value.setText("-")
        self.evento_value.setText("-")
        self.comando_value.setText("-")
        self.confianca_value.setText("-")
        self.status_value.setText("Parado")
        self.cooldown_value.setText("-")

    def _simulate_gesture(self):
        if not self.is_running:
            QMessageBox.information(self, "Aviso", "Inicie a aplicação primeiro para simular gestos.")
            return
            
        self.gesto_value.setText("Swipe direita")
        self.evento_value.setText("GESTURE_SWIPE_RIGHT")
        self.comando_value.setText("Right Arrow")
        self.confianca_value.setText("92%")
        self.status_value.setText("Comando executado")
        self.cooldown_value.setText("0.7s")

    def _set_visualization_mode(self, mode: str):
        self.vis_mode_label.setText(f"Modo de visualização: {mode}")
