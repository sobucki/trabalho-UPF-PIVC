from __future__ import annotations

import copy
import cv2
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QGroupBox, QMessageBox, QDialog, QCheckBox, QFileDialog, QFrame,
    QToolButton
)
from PySide6.QtCore import Qt, QTimer, QSize

from src.gui import icons

from .processing_view import ProcessingView
from .command_settings_dialog import CommandSettingsDialog
from .styles import (
    get_recognition_title_style,
    get_recognition_value_style,
    get_status_label_style,
    get_header_title_style,
    get_header_integration_style,
    get_header_integration_value_style,
    get_checkbox_inline_style,
    get_header_container_style,
    get_header_icon_style,
    get_header_subtitle_style,
    get_integration_card_style,
    get_footer_bar_style,
    get_recognition_panel_style,
    get_recognition_item_style,
    get_recognition_icon_style,
    get_recognition_header_icon_style,
    get_low_light_panel_style
)
from src.vision.gesture_pipeline import GesturePipeline
from src.gui.image_utils import cv_frame_to_qpixmap

from src.integrations.default_configs import DEFAULT_INTEGRATIONS
from src.integrations.command_mapper import CommandMapper
from src.integrations.command_executor import CommandExecutor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("GestureHub CV")
        self.resize(1000, 750)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.is_running = False
        self._enhance_low_light_enabled = False
        
        self._command_mapper = CommandMapper(DEFAULT_INTEGRATIONS, active_integration_id="presentations")
        self._command_executor = CommandExecutor()
        
        self._capture = None
        self._camera_timer = QTimer(self)
        self._camera_timer.timeout.connect(self._process_camera_frame)
        
        self._gesture_pipeline = None
        self._timestamp_ms = 0
        self._camera_index = 0
        self._video_source = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._create_header()
        
        self.content_wrapper = QWidget()
        self.content_layout = QVBoxLayout(self.content_wrapper)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)
        
        self._create_content()
        self._create_footer_controls()
        
        self.main_layout.addWidget(self.content_wrapper, stretch=1)
        
    def _create_header(self):
        header_card = QFrame()
        header_card.setStyleSheet(get_header_container_style())
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 12, 24, 12)
        
        # Left side
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(get_header_icon_style())
        icon_label.setPixmap(icons.icon_app_logo().pixmap(QSize(24, 24)))
        
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_label = QLabel("GestureHub CV")
        title_label.setStyleSheet(get_header_title_style())
        subtitle_label = QLabel("Controle configurável por gestos")
        subtitle_label.setStyleSheet(get_header_subtitle_style())
        title_box.addWidget(title_label)
        title_box.addWidget(subtitle_label)
        
        # Right side - Integration Badge
        integration_card = QFrame()
        integration_card.setStyleSheet(get_integration_card_style())
        integration_layout = QHBoxLayout(integration_card)
        integration_layout.setContentsMargins(12, 4, 12, 4)
        integration_layout.setSpacing(12)
        
        integ_icon = QLabel()
        integ_icon.setPixmap(icons.icon_integration().pixmap(QSize(14, 14)))
        integ_title = QLabel("Integração:")
        integ_title.setStyleSheet(get_header_integration_style())
        integ_value = QLabel("Apresentações")
        integ_value.setStyleSheet(get_header_integration_value_style())
        
        integ_box = QHBoxLayout()
        integ_box.setSpacing(6)
        integ_box.addWidget(integ_icon)
        integ_box.addWidget(integ_title)
        integ_box.addWidget(integ_value)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet(f"color: #DDE3EA; border: none; background-color: #DDE3EA; width: 1px;")
        
        status_title = QLabel("Status do sistema")
        status_title.setStyleSheet(get_header_integration_style())
        
        self.integration_status_label = QPushButton("PARADO")
        self.integration_status_label.setIcon(icons.icon_status("PARADO"))
        self.integration_status_label.setIconSize(QSize(14, 14))
        self.integration_status_label.setStyleSheet(get_status_label_style("PARADO"))
        # Hack to make QPushButton look exactly like our badge styling without button styles
        self.integration_status_label.setFlat(True)
        
        integration_layout.addLayout(integ_box)
        integration_layout.addWidget(separator)
        integration_layout.addWidget(status_title)
        integration_layout.addWidget(self.integration_status_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addSpacing(16)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(integration_card)
        
        self.main_layout.addWidget(header_card)
        
    def _create_content(self):
        content_layout_h = QHBoxLayout()
        content_layout_h.setSpacing(16)
        
        self.processing_view = ProcessingView()
        content_layout_h.addWidget(self.processing_view, stretch=3)
        
        self._create_recognition_panel(content_layout_h)
        
        self.content_layout.addLayout(content_layout_h)

    def _create_recognition_panel(self, parent_layout):
        from PySide6.QtWidgets import QFrame
        
        panel_card = QFrame()
        panel_card.setStyleSheet(get_recognition_panel_style())
        panel_layout = QVBoxLayout(panel_card)
        panel_layout.setContentsMargins(16, 20, 16, 16)
        panel_layout.setSpacing(0)
        
        header_hlayout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(icons.icon_gesture().pixmap(QSize(20, 20)))
        icon_label.setStyleSheet(get_recognition_header_icon_style())
        title_label = QLabel("Painel de reconhecimento")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        header_hlayout.addWidget(icon_label)
        header_hlayout.addSpacing(4)
        header_hlayout.addWidget(title_label)
        header_hlayout.addStretch()
        
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #2E9D3F; border: none; margin-top: 10px; margin-bottom: 8px;")
        
        panel_layout.addLayout(header_hlayout)
        panel_layout.addWidget(separator)
        
        self.gesture_value = self._create_recognition_field(panel_layout, "Gesto detectado", icons.icon_gesture(), "Aguardando gesto...")
        self.event_value = self._create_recognition_field(panel_layout, "Evento gerado", icons.icon_event(), "-")
        self.command_value = self._create_recognition_field(panel_layout, "Comando executado", icons.icon_command(), "-")
        self.confidence_value = self._create_recognition_field(panel_layout, "Confiança", icons.icon_confidence(), "-")
        self.status_value = self._create_recognition_field(panel_layout, "Status", icons.icon_recognition_status(), "ATIVO", is_status=True)
        self.cooldown_value = self._create_recognition_field(panel_layout, "Cooldown", icons.icon_cooldown(), "Pronto")
        
        panel_layout.addStretch()
        
        low_light_card = QFrame()
        low_light_card.setStyleSheet(get_low_light_panel_style())
        low_light_layout = QVBoxLayout(low_light_card)
        low_light_layout.setContentsMargins(12, 12, 12, 12)
        
        self.cb_low_light = QCheckBox("Otimizar baixa iluminação")
        self.cb_low_light.setStyleSheet(get_checkbox_inline_style())
        self.cb_low_light.toggled.connect(self._toggle_low_light)
        low_light_layout.addWidget(self.cb_low_light)
        
        panel_layout.addWidget(low_light_card)
        
        parent_layout.addWidget(panel_card, stretch=1)

    def _create_recognition_field(self, parent_layout, title, icon, default_text, is_status=False):
        container = QFrame()
        container.setStyleSheet(get_recognition_item_style())
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 12, 4, 12)
        
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(QSize(18, 18)))
        icon_label.setFixedWidth(28)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(get_recognition_title_style())
        
        value_label = QLabel(default_text)
        if is_status:
            value_label.setStyleSheet(get_status_label_style(default_text))
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        else:
            value_label.setStyleSheet(get_recognition_value_style())
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)
        
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        parent_layout.addWidget(container)
        return value_label

    def _create_footer_controls(self):
        from PySide6.QtWidgets import QFrame
        footer_card = QFrame()
        footer_card.setStyleSheet(get_footer_bar_style())
        footer_layout = QHBoxLayout(footer_card)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        
        BUTTON_ICON_SIZE = QSize(16, 16)
        
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.setObjectName("primaryButton")
        self.btn_iniciar.setIcon(icons.icon_play())
        self.btn_iniciar.setIconSize(BUTTON_ICON_SIZE)
        self.btn_iniciar.clicked.connect(lambda: self._set_running_state(True))
        
        self.btn_parar = QPushButton("Parar")
        self.btn_parar.setObjectName("dangerButton")
        self.btn_parar.setIcon(icons.icon_stop())
        self.btn_parar.setIconSize(BUTTON_ICON_SIZE)
        self.btn_parar.setEnabled(False)
        self.btn_parar.clicked.connect(lambda: self._set_running_state(False))
        
        self.btn_simular = QPushButton("Simular gesto")
        self.btn_simular.setObjectName("secondaryButton")
        self.btn_simular.setIcon(icons.icon_simulate())
        self.btn_simular.setIconSize(BUTTON_ICON_SIZE)
        self.btn_simular.clicked.connect(self._simulate_gesture)
        
        self.btn_configurar = QPushButton("Configurar comandos")
        self.btn_configurar.setObjectName("secondaryButton")
        self.btn_configurar.setIcon(icons.icon_settings())
        self.btn_configurar.setIconSize(BUTTON_ICON_SIZE)
        self.btn_configurar.clicked.connect(self._open_command_settings)
        
        self.btn_carregar_img = QPushButton("Carregar imagem")
        self.btn_carregar_img.setObjectName("secondaryButton")
        self.btn_carregar_img.setIcon(icons.icon_image())
        self.btn_carregar_img.setIconSize(BUTTON_ICON_SIZE)
        self.btn_carregar_img.clicked.connect(self._show_feature_not_available)
        
        self.btn_carregar_vid = QPushButton("Carregar vídeo")
        self.btn_carregar_vid.setObjectName("secondaryButton")
        self.btn_carregar_vid.setIcon(icons.icon_video())
        self.btn_carregar_vid.setIconSize(BUTTON_ICON_SIZE)
        self.btn_carregar_vid.clicked.connect(self._handle_video_btn)
        
        footer_layout.addWidget(self.btn_iniciar)
        footer_layout.addWidget(self.btn_parar)
        footer_layout.addWidget(self.btn_simular)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_configurar)
        footer_layout.addWidget(self.btn_carregar_img)
        footer_layout.addWidget(self.btn_carregar_vid)
        
        self.content_layout.addWidget(footer_card)

    def _handle_video_btn(self):
        if self._video_source is None:
            self._load_video()
        else:
            self._remove_video()

    def _load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Vídeo", "", "Vídeos (*.mp4 *.avi *.mkv *.mov);;Todos os Arquivos (*)"
        )
        if file_path:
            self._video_source = file_path
            filename = os.path.basename(file_path)
            self.btn_carregar_vid.setText(f"Remover Vídeo ({filename})")
            if self.is_running:
                self._stop_camera()

    def _remove_video(self):
        self._video_source = None
        self.btn_carregar_vid.setText("Carregar vídeo")
        if self.is_running:
            self._stop_camera()

    def _set_running_state(self, running: bool) -> None:
        if running:
            self._start_camera()
        else:
            self._stop_camera()

    def _start_camera(self) -> None:
        if self.is_running:
            return

        if self._video_source:
            self._capture = cv2.VideoCapture(self._video_source)
        else:
            self._capture = cv2.VideoCapture(self._camera_index)

        if not self._capture.isOpened():
            self._capture.release()
            self._capture = None
            self._set_error_state("Erro ao acessar fonte de vídeo.")
            QMessageBox.critical(self, "Erro de vídeo", "Não foi possível abrir a webcam ou o vídeo.")
            return

        try:
            self._gesture_pipeline = GesturePipeline()
            self._gesture_pipeline.enhance_low_light = self._enhance_low_light_enabled
            self._gesture_pipeline.start()
        except Exception as exc:
            self._release_camera()
            self._set_error_state(str(exc))
            QMessageBox.critical(self, "Erro ao iniciar reconhecimento", str(exc))
            return

        self._timestamp_ms = 0
        
        timer_interval = 30
        if self._video_source:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                timer_interval = int(1000 / fps)
                
        self._camera_timer.start(timer_interval)
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
            if self._video_source:
                self._capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._capture.read()
                if not ret:
                    self._stop_camera()
                    return
            else:
                self._set_error_state("Falha ao capturar frame da câmera.")
                self._stop_camera()
                return

        if not self._video_source:
            frame = cv2.flip(frame, 1)

        try:
            result = self._gesture_pipeline.process_frame(frame, self._timestamp_ms)
        except Exception as exc:
            self._set_error_state(str(exc))
            self._stop_camera()
            QMessageBox.critical(self, "Erro no processamento", str(exc))
            return

        self._timestamp_ms += 33

        execution_result = None

        if result.get("triggered") and result.get("event") != "NO_GESTURE":
            event_name = result.get("event")
            command_config = self._command_mapper.get_command_for_event(event_name)
            execution_result = self._command_executor.execute(command_config)

        self._update_processing_view(result)
        self._update_recognition_panel_from_result(result, execution_result)

    def _update_processing_view(self, result: dict) -> None:
        current_mode = self.processing_view.current_mode

        MODE_TO_FRAME_KEY = {
            "Original": "original_frame",
            "Pré-processamento": "enhanced_frame",
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
            "Pré-processamento": result["enhanced_frame"],
            "Resultado final": result["result_frame"],
        }

        for mode, frame in frames.items():
            pixmap = cv_frame_to_qpixmap(frame)
            self.processing_view.update_frame(mode, pixmap)

    def _update_recognition_panel_from_result(self, result: dict, execution_result: dict | None = None) -> None:
        gesture = result.get("gesture", "Nenhum")
        event = result.get("event", "NO_GESTURE")
        confidence = result.get("confidence", f'{result.get("stable_frames", 0)}/{result.get("required_frames", 5)}')
        cooldown = result.get("cooldown", "Pronto")

        if execution_result is not None:
            command = execution_result["command"] if execution_result.get("executed") else "-"
            status = execution_result.get("message", "-")
        else:
            command = "-"
            status = result.get("status", "-")

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

        self.integration_status_label.setText("ATIVO")
        self.integration_status_label.setIcon(icons.icon_status("ATIVO"))
        self.integration_status_label.setStyleSheet(get_status_label_style("ATIVO"))
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

        self.integration_status_label.setText("PARADO")
        self.integration_status_label.setIcon(icons.icon_status("PARADO"))
        self.integration_status_label.setStyleSheet(get_status_label_style("PARADO"))
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)
        self.btn_simular.setEnabled(True)

        self._set_recognition_idle_state()

    def _set_error_state(self, message: str) -> None:
        self.is_running = False
        self.processing_view.set_running(False)
        
        self.integration_status_label.setText("ERRO")
        self.integration_status_label.setIcon(icons.icon_status("ERRO"))
        self.integration_status_label.setStyleSheet(get_status_label_style("ERRO"))
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
        
        # Puxa o status cru e exibe visualmente usando dicionario de cores do styles (se ele existir)
        # O _format_status_for_panel idealmente daria as strings corretas, mas passamos a do ML direto
        # O style map se ajeita usando upper, entao vamos apenas enviar
        status_key = status.upper().replace(" ", "_")
        # Mas para garantir, voltamos pro status 'ATIVO', 'PARADO', 'ERRO' pros rotulos estaticos da UI se não achou match visual no styles.
        if "PRONTO" in status_key or "SUCESSO" in status_key:
            self.status_value.setStyleSheet(get_status_label_style("ATIVO"))
        else:
            self.status_value.setStyleSheet(get_status_label_style(status_key))
            
        self.cooldown_value.setText(cooldown)

    def _set_recognition_idle_state(self):
        self._update_recognition_panel("-", "-", "-", "-", "Parado", "-")

    def _toggle_low_light(self, checked: bool):
        self._enhance_low_light_enabled = checked
        if self._gesture_pipeline is not None:
            self._gesture_pipeline.enhance_low_light = checked

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
        dialog = CommandSettingsDialog(self, integrations=self._command_mapper.integrations)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_integrations = dialog.get_integrations()
            self._command_mapper.update_integrations(updated_integrations)

    def _show_feature_not_available(self):
        QMessageBox.information(self, "Aviso", "Esta funcionalidade será implementada em uma etapa futura.")
        
    def closeEvent(self, event):
        """Garante a liberacao segura dos recursos C/C++ ao fechar o form"""
        self._stop_camera()
        super().closeEvent(event)
