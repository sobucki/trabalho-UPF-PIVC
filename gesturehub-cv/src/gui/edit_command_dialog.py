from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QFormLayout
)
from PySide6.QtCore import Qt

class EditCommandDialog(QDialog):
    def __init__(self, command_data: dict, command_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar comando")
        self.resize(350, 250)
        
        self.command_data = command_data.copy()
        self.command_type = command_type
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Labels for read-only fields
        header_layout = QVBoxLayout()
        header_layout.addWidget(QLabel(f"<b>Gesto:</b> {self.command_data.get('gesture', '')}"))
        header_layout.addWidget(QLabel(f"<b>Evento:</b> {self.command_data.get('event', '')}"))
        layout.addLayout(header_layout)
        
        layout.addSpacing(10)
        
        form_layout = QFormLayout()
        
        # Tipo de Comando (read only display)
        tipo_combo = QComboBox()
        tipo_combo.addItem("Teclado" if self.command_type == "keyboard" else "Mídia")
        tipo_combo.setEnabled(False)
        form_layout.addRow("Tipo de comando", tipo_combo)
        
        # Command / Key Dropdown
        self.cmd_combo = QComboBox()
        allowed_commands = self._get_allowed_commands()
        self.cmd_combo.addItems(allowed_commands)
        
        current_cmd = self.command_data.get('command', '')
        if current_cmd in allowed_commands:
            self.cmd_combo.setCurrentText(current_cmd)
        
        form_layout.addRow("Tecla / Comando", self.cmd_combo)
        
        # Description Input
        self.desc_input = QLineEdit()
        self.desc_input.setText(self.command_data.get('description', ''))
        form_layout.addRow("Descrição", self.desc_input)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Salvar alteração")
        btn_save.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        
    def _get_allowed_commands(self) -> list:
        if self.command_type == "keyboard":
            return [
                "F5", "Esc", "Right Arrow", "Left Arrow", 
                "Page Down", "Page Up", "Space", "Enter"
            ]
        elif self.command_type == "media_key":
            return [
                "PLAY_PAUSE", "NEXT_TRACK", "PREVIOUS_TRACK", 
                "VOLUME_UP", "VOLUME_DOWN", "MUTE"
            ]
        return []

    def get_updated_command(self) -> dict:
        self.command_data['command'] = self.cmd_combo.currentText()
        self.command_data['description'] = self.desc_input.text()
        return self.command_data
