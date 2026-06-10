import copy
import cv2
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGroupBox, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QTimer

from .processing_view import ProcessingView
from .command_settings_dialog import CommandSettingsDialog, DEFAULT_INTEGRATIONS
from .styles import (
    get_recognition_title_style,
    get_recognition_value_style,
    get_status_label_style
)
from src.vision.gesture_pipeline import GesturePipeline
from src.gui.image_utils import cv_frame_to_qpixmap


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
        
        self._capture = None
        self._camera_timer = QTimer(self)
        self._camera_timer.timeout.connect(self._process_camera_frame)
        
        self._gesture_pipeline = None
        self._timestamp_ms = 0
        self._camera_index = 0
        
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
        
        self.processing_view = ProcessingView()
        content_layout.addWidget(self.processing_view, stretch=3)
        
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

    def _set_running_state(self, running: bool) -> None:
        if running:
            self._start_camera()
        else:
            self._stop_camera()

    def _start_camera(self) -> None:
        if self.is_running:
            return

        self._capture = cv2.VideoCapture(self._camera_index)

        if not self._capture.isOpened():
            self._capture.release()
            self._capture = None
            self._set_error_state("Erro ao acessar câmera.")
            QMessageBox.critical(self, "Erro de câmera", "Não foi possível abrir a webcam.")
            return

        try:
            self._gesture_pipeline = GesturePipeline()
            self._gesture_pipeline.start()
        except Exception as exc:
            self._release_camera()
            self._set_error_state(str(exc))
            QMessageBox.critical(self, "Erro ao iniciar reconhecimento", str(exc))
            return

        self._timestamp_ms = 0
        self._camera_timer.start(30)
        self._set_ui_running_state()

    def _stop_camera(self) -> None:
        if self._camera_timer.isActive():
            self._camera_timer.stop()

        self._release_camera()
        self._close_pipeline()
        self._set_ui_stopped_state()

    def _release_camera(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def _close_pipeline(self) -> None:
        if self._gesture_pipeline is not None:
            self._gesture_pipeline.close()
            self._gesture_pipeline = None

    def _process_camera_frame(self) -> None:
        if self._capture is None or self._gesture_pipeline is None:
            return

        ret, frame = self._capture.read()

        if not ret:
            self._set_error_state("Falha ao capturar frame da câmera.")
            self._stop_camera()
            return

        frame = cv2.flip(frame, 1)

        try:
            result = self._gesture_pipeline.process_frame(frame, self._timestamp_ms)
        except Exception as exc:
            self._set_error_state(str(exc))
            self._stop_camera()
            QMessageBox.critical(self, "Erro no processamento", str(exc))
            return

        self._timestamp_ms += 33

        self._update_processing_view(result)
        self._update_recognition_panel_from_result(result)

    def _update_processing_view(self, result: dict) -> None:
        current_mode = self.processing_view.current_mode

        MODE_TO_FRAME_KEY = {
            "Original": "original_frame",
            "HSV": "hsv_frame",
            "Máscara / Threshold": "mask_frame",
            "Contornos": "contours_frame",
            "Resultado final": "result_frame",
        }

        if current_mode == "Grade":
            self._update_processing_grid(result)
        else:
            frame_key = MODE_TO_FRAME_KEY.get(current_mode, "result_frame")
            frame_to_show = result[frame_key]
            pixmap = cv_frame_to_qpixmap(frame_to_show)
            self.processing_view.update_frame(current_mode, pixmap)

    def _update_processing_grid(self, result: dict) -> None:
        frames = {
            "Original": result["original_frame"],
            "HSV": result["hsv_frame"],
            "Contornos": result["contours_frame"],
            "Resultado final": result["result_frame"],
        }

        for mode, frame in frames.items():
            pixmap = cv_frame_to_qpixmap(frame)
            self.processing_view.update_frame(mode, pixmap)

    def _update_recognition_panel_from_result(self, result: dict) -> None:
        gesture = result.get("gesture", "Nenhum")
        event = result.get("event", "NO_GESTURE")
        confidence = result.get("confidence", f'{result.get("stable_frames", 0)}/{result.get("required_frames", 5)}')
        status = result.get("status", "Aguardando gesto...")
        cooldown = result.get("cooldown", "Pronto")

        triggered = result.get("triggered", False)
        default_action = result.get("default_action", "-")

        command = default_action if triggered else "-"

        self._update_recognition_panel(
            gesture=gesture,
            event=event,
            command=command,
            confidence=confidence,
            status=status,
            cooldown=cooldown,
        )

    def _set_ui_running_state(self) -> None:
        self.is_running = True
        self.processing_view.set_running(True)

        self.integration_label.setText("Integração: Apresentações | ATIVO")
        self.btn_iniciar.setEnabled(False)
        self.btn_parar.setEnabled(True)
        self.btn_simular.setEnabled(False)

        self._update_recognition_panel(
            gesture="Aguardando...",
            event="-",
            command="-",
            confidence="0/5",
            status="Ativo",
            cooldown="Pronto",
        )

    def _set_ui_stopped_state(self) -> None:
        self.is_running = False
        self.processing_view.set_running(False)

        self.integration_label.setText("Integração: Apresentações | PARADO")
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)
        self.btn_simular.setEnabled(True)

        self._set_recognition_idle_state()

    def _set_error_state(self, message: str) -> None:
        self.is_running = False
        self.processing_view.set_running(False)
        
        self.integration_label.setText("Integração: Apresentações | ERRO")
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)
        self.btn_simular.setEnabled(True)

        self._update_recognition_panel(
            gesture="-",
            event="-",
            command=message,
            confidence="-",
            status="Erro",
            cooldown="-",
        )

    def _update_recognition_panel(self, gesture: str, event: str, command: str, confidence: str, status: str, cooldown: str):
        self.gesture_value.setText(gesture)
        self.event_value.setText(event)
        self.command_value.setText(command)
        self.confidence_value.setText(confidence)
        
        self.status_value.setText(status)
        self.status_value.setStyleSheet(get_status_label_style(status))
        
        self.cooldown_value.setText(cooldown)

    def _set_recognition_idle_state(self):
        self._update_recognition_panel("-", "-", "-", "-", "Parado", "-")

    def _simulate_gesture(self):
        if not self.is_running:
            self.status_value.setText("AGUARDANDO")
            self.status_value.setStyleSheet(get_status_label_style("AGUARDANDO"))
            QMessageBox.information(self, "Aviso", "Inicie a aplicação primeiro para simular gestos.")
            return
            
        self._update_recognition_panel(
            "Swipe direita", 
            "GESTURE_SWIPE_RIGHT", 
            "Right Arrow", 
            "92%", 
            "COMANDO EXECUTADO", 
            "0.7s"
        )

    def _open_command_settings(self):
        dialog = CommandSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.integrations = dialog.get_integrations()

    def _show_feature_not_available(self):
        QMessageBox.information(self, "Aviso", "Esta funcionalidade será implementada em uma etapa futura.")
        
    def closeEvent(self, event):
        """Garante a liberacao segura dos recursos C/C++ ao fechar o form"""
        self._stop_camera()
        super().closeEvent(event)
