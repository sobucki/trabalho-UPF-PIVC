import copy
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGroupBox, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from .processing_view import ProcessingView
from .command_settings_dialog import CommandSettingsDialog, DEFAULT_INTEGRATIONS
from .styles import (
    get_recognition_title_style,
    get_recognition_value_style,
    get_status_label_style
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GestureHub CV")
        self.resize(1000, 750)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.is_running = False
        self.integrations = copy.deepcopy(DEFAULT_INTEGRATIONS)
        
        self._setup_ui()
        
    def _setup_ui(self):
        self._create_header()
        self._create_content()
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
        
        # Area de visualização do processamento
        self.processing_view = ProcessingView()
        content_layout.addWidget(self.processing_view, stretch=3)
        
        # Painel de Reconhecimento
        self._create_recognition_panel(content_layout)
        
        self.main_layout.addLayout(content_layout)

    def _create_recognition_panel(self, parent_layout):
        self.recognition_group = QGroupBox("Painel de reconhecimento")
        panel_layout = QVBoxLayout(self.recognition_group)
        panel_layout.setSpacing(15)
        
        self.gesture_value = self._create_recognition_field(panel_layout, "Gesto detectado", "-")
        self.event_value = self._create_recognition_field(panel_layout, "Evento gerado", "-")
        self.command_value = self._create_recognition_field(panel_layout, "Comando executado", "-")
        self.confidence_value = self._create_recognition_field(panel_layout, "Confiança", "-")
        self.status_value = self._create_recognition_field(panel_layout, "Status", "PARADO")
        self.status_value.setStyleSheet(get_status_label_style("PARADO"))
        self.cooldown_value = self._create_recognition_field(panel_layout, "Cooldown", "-")
        
        panel_layout.addStretch()
        parent_layout.addWidget(self.recognition_group, stretch=1)

    def _create_recognition_field(self, parent_layout, title, default_text):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(get_recognition_title_style())
        
        value_label = QLabel(default_text)
        value_label.setStyleSheet(get_recognition_value_style())
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        parent_layout.addWidget(container)
        return value_label

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
        self.btn_configurar.clicked.connect(self._open_command_settings)
        
        self.btn_carregar_img = QPushButton("Carregar imagem")
        self.btn_carregar_img.clicked.connect(self._show_feature_not_available)
        
        self.btn_carregar_vid = QPushButton("Carregar vídeo")
        self.btn_carregar_vid.clicked.connect(self._show_feature_not_available)
        
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
        self.processing_view.set_running(running)
        
        if running:
            self.integration_label.setText("Integração: Apresentações | ATIVO")
            self.btn_iniciar.setEnabled(False)
            self.btn_parar.setEnabled(True)
            self._set_recognition_running_state()
        else:
            self.integration_label.setText("Integração: Apresentações | PARADO")
            self.btn_iniciar.setEnabled(True)
            self.btn_parar.setEnabled(False)
            self._set_recognition_idle_state()

    def _update_recognition_panel(self, gesture: str, event: str, command: str, confidence: str, status: str, cooldown: str):
        self.gesture_value.setText(gesture)
        self.event_value.setText(event)
        self.command_value.setText(command)
        self.confidence_value.setText(confidence)
        
        self.status_value.setText(status)
        self.status_value.setStyleSheet(get_status_label_style(status))
        
        self.cooldown_value.setText(cooldown)

    def _set_recognition_idle_state(self):
        self._update_recognition_panel("-", "-", "-", "-", "PARADO", "-")

    def _set_recognition_running_state(self):
        self._update_recognition_panel("Aguardando gesto...", "-", "-", "-", "ATIVO", "Pronto")

    def _set_recognition_simulated_gesture(self):
        self._update_recognition_panel(
            "Swipe direita", 
            "GESTURE_SWIPE_RIGHT", 
            "Right Arrow", 
            "92%", 
            "COMANDO EXECUTADO", 
            "0.7s"
        )

    def _simulate_gesture(self):
        if not self.is_running:
            self.status_value.setText("AGUARDANDO")
            self.status_value.setStyleSheet(get_status_label_style("AGUARDANDO"))
            QMessageBox.information(self, "Aviso", "Inicie a aplicação primeiro para simular gestos.")
            return
            
        self._set_recognition_simulated_gesture()

    def _open_command_settings(self):
        dialog = CommandSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.integrations = dialog.get_integrations()

    def _show_feature_not_available(self):
        # TODO: Implementar carregamento real de imagem e vídeo em etapa futura
        QMessageBox.information(self, "Aviso", "Esta funcionalidade será implementada em uma etapa futura.")
