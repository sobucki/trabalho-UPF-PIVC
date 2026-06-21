from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFormLayout
)

from .edit_command_dialog import ALLOWED_COMMANDS


class AddCommandDialog(QDialog):
    """Diálogo para cadastrar um novo comando dentro de uma integração."""

    def __init__(self, available_gestures: list[dict], command_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo comando")
        self.resize(350, 250)

        self.available_gestures = available_gestures
        self.command_type = command_type

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.gesture_combo = QComboBox()
        for gesture in self.available_gestures:
            self.gesture_combo.addItem(gesture["gesture"], gesture["event"])
        form_layout.addRow("Gesto", self.gesture_combo)

        self.cmd_combo = QComboBox()
        self.cmd_combo.addItems(ALLOWED_COMMANDS.get(self.command_type, []))
        form_layout.addRow("Tecla / Comando", self.cmd_combo)

        self.desc_input = QLineEdit()
        form_layout.addRow("Descrição", self.desc_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Adicionar")
        btn_save.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def get_new_command(self) -> dict:
        index = self.gesture_combo.currentIndex()
        return {
            "gesture": self.gesture_combo.currentText(),
            "event": self.gesture_combo.itemData(index),
            "command": self.cmd_combo.currentText(),
            "description": self.desc_input.text(),
        }
