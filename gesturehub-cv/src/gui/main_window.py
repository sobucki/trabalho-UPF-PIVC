from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Slot

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GestureHub CV")
        self.resize(800, 600)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self._setup_ui()
        
    def _setup_ui(self):
        self._create_header()
        self._create_content()
        self._create_controls()
        
    def _create_header(self):
        header_layout = QHBoxLayout()
        
        title_label = QLabel("<b>GestureHub CV</b>")
        title_label.setStyleSheet("font-size: 24px;")
        
        integration_label = QLabel("Integração ativa: <b>Apresentações</b>")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(integration_label)
        
        self.main_layout.addLayout(header_layout)
        
    def _create_content(self):
        content_layout = QHBoxLayout()
        
        # Camera Area
        self.camera_frame = QFrame()
        self.camera_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.camera_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.camera_frame.setMinimumSize(480, 360)
        
        camera_layout = QVBoxLayout(self.camera_frame)
        self.camera_label = QLabel("Câmera desligada")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("color: gray; font-size: 18px;")
        camera_layout.addWidget(self.camera_label)
        
        content_layout.addWidget(self.camera_frame, stretch=2)
        
        # Recognition Panel
        self._create_recognition_panel()
        content_layout.addWidget(self.recognition_group, stretch=1)
        
        self.main_layout.addLayout(content_layout)
        
    def _create_recognition_panel(self):
        self.recognition_group = QGroupBox("Reconhecimento")
        panel_layout = QGridLayout(self.recognition_group)
        
        # Labels
        self.status_value = QLabel("Parado")
        self.status_value.setStyleSheet("color: red; font-weight: bold;")
        
        self.gesto_value = QLabel("-")
        self.evento_value = QLabel("-")
        self.comando_value = QLabel("-")
        self.confianca_value = QLabel("-")
        
        # Add widgets to grid (row, col)
        panel_layout.addWidget(QLabel("Status:"), 0, 0)
        panel_layout.addWidget(self.status_value, 0, 1)
        
        panel_layout.addWidget(QLabel("Gesto detectado:"), 1, 0)
        panel_layout.addWidget(self.gesto_value, 1, 1)
        
        panel_layout.addWidget(QLabel("Evento gerado:"), 2, 0)
        panel_layout.addWidget(self.evento_value, 2, 1)
        
        panel_layout.addWidget(QLabel("Comando executado:"), 3, 0)
        panel_layout.addWidget(self.comando_value, 3, 1)
        
        panel_layout.addWidget(QLabel("Confiança:"), 4, 0)
        panel_layout.addWidget(self.confianca_value, 4, 1)
        
        panel_layout.setRowStretch(5, 1) # Push everything to top
        
    def _create_controls(self):
        controls_layout = QHBoxLayout()
        
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.clicked.connect(self._on_iniciar_clicked)
        
        self.btn_parar = QPushButton("Parar")
        self.btn_parar.setEnabled(False)
        self.btn_parar.clicked.connect(self._on_parar_clicked)
        
        self.btn_configurar = QPushButton("Configurar comandos")
        self.btn_carregar_img = QPushButton("Carregar imagem")
        self.btn_carregar_vid = QPushButton("Carregar vídeo")
        
        controls_layout.addWidget(self.btn_iniciar)
        controls_layout.addWidget(self.btn_parar)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_configurar)
        controls_layout.addWidget(self.btn_carregar_img)
        controls_layout.addWidget(self.btn_carregar_vid)
        
        self.main_layout.addLayout(controls_layout)

    @Slot()
    def _on_iniciar_clicked(self):
        self.status_value.setText("Ativo")
        self.status_value.setStyleSheet("color: green; font-weight: bold;")
        self.gesto_value.setText("Aguardando gesto...")
        self.camera_label.setText("Câmera Iniciada (Simulação)")
        self.camera_label.setStyleSheet("color: black; font-size: 18px;")
        
        self.btn_iniciar.setEnabled(False)
        self.btn_parar.setEnabled(True)

    @Slot()
    def _on_parar_clicked(self):
        self.status_value.setText("Parado")
        self.status_value.setStyleSheet("color: red; font-weight: bold;")
        self.gesto_value.setText("-")
        self.evento_value.setText("-")
        self.comando_value.setText("-")
        self.confianca_value.setText("-")
        
        self.camera_label.setText("Câmera desligada")
        self.camera_label.setStyleSheet("color: gray; font-size: 18px;")
        
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)
