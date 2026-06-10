import copy
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QMessageBox, QHeaderView
)
from .edit_command_dialog import EditCommandDialog

DEFAULT_INTEGRATIONS = {
    "presentations": {
        "name": "Apresentações",
        "command_type": "keyboard",
        "commands": [
            {
                "gesture": "Mão aberta",
                "event": "GESTURE_OPEN_HAND",
                "command": "F5",
                "description": "Iniciar apresentação"
            },
            {
                "gesture": "Punho fechado",
                "event": "GESTURE_CLOSED_FIST",
                "command": "Esc",
                "description": "Sair da apresentação"
            },
            {
                "gesture": "Swipe direita",
                "event": "GESTURE_SWIPE_RIGHT",
                "command": "Right Arrow",
                "description": "Próximo slide"
            },
            {
                "gesture": "Swipe esquerda",
                "event": "GESTURE_SWIPE_LEFT",
                "command": "Left Arrow",
                "description": "Slide anterior"
            },
            {
                "gesture": "Polegar cima",
                "event": "GESTURE_THUMB_UP",
                "command": "Page Down",
                "description": "Avançar"
            },
            {
                "gesture": "Polegar baixo",
                "event": "GESTURE_THUMB_DOWN",
                "command": "Page Up",
                "description": "Voltar"
            }
        ]
    },
    "media": {
        "name": "Spotify / Mídia",
        "command_type": "media_key",
        "commands": [
            {
                "gesture": "Mão aberta",
                "event": "GESTURE_OPEN_HAND",
                "command": "PLAY_PAUSE",
                "description": "Tocar / Pausar"
            },
            {
                "gesture": "Punho fechado",
                "event": "GESTURE_CLOSED_FIST",
                "command": "MUTE",
                "description": "Mutar volume"
            },
            {
                "gesture": "Swipe direita",
                "event": "GESTURE_SWIPE_RIGHT",
                "command": "NEXT_TRACK",
                "description": "Próxima faixa"
            },
            {
                "gesture": "Swipe esquerda",
                "event": "GESTURE_SWIPE_LEFT",
                "command": "PREVIOUS_TRACK",
                "description": "Faixa anterior"
            },
            {
                "gesture": "Polegar cima",
                "event": "GESTURE_THUMB_UP",
                "command": "VOLUME_UP",
                "description": "Aumentar volume"
            },
            {
                "gesture": "Polegar baixo",
                "event": "GESTURE_THUMB_DOWN",
                "command": "VOLUME_DOWN",
                "description": "Diminuir volume"
            }
        ]
    }
}

class CommandSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração de comandos")
        self.resize(700, 450)
        
        # Keep an in-memory copy of settings
        self.integrations = copy.deepcopy(DEFAULT_INTEGRATIONS)
        self.current_integration_id = "presentations"
        
        self._setup_ui()
        self._load_integration_commands()
        
    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        self._create_integration_selector()
        self._create_commands_table()
        self._create_actions()
        
    def _create_integration_selector(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Integração:"))
        
        self.combo_integrations = QComboBox()
        for key, value in self.integrations.items():
            self.combo_integrations.addItem(value["name"], key)
            
        # Select "presentations" by default
        index = self.combo_integrations.findData("presentations")
        if index >= 0:
            self.combo_integrations.setCurrentIndex(index)
            
        self.combo_integrations.currentIndexChanged.connect(self._on_integration_changed)
        
        layout.addWidget(self.combo_integrations)
        layout.addStretch()
        
        self.main_layout.addLayout(layout)
        
    def _create_commands_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Gesto", "Evento interno", "Comando", "Descrição"])
        
        # Table configurations
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        self.main_layout.addWidget(self.table)
        
    def _create_actions(self):
        btn_layout = QHBoxLayout()
        
        self.btn_edit = QPushButton("Editar selecionado")
        self.btn_edit.clicked.connect(self._edit_selected_command)
        
        self.btn_save = QPushButton("Confirmar")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_restore = QPushButton("Restaurar padrão")
        self.btn_restore.clicked.connect(self._restore_defaults)
        
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_restore)
        
        self.main_layout.addLayout(btn_layout)
        
    def _on_integration_changed(self, index):
        integration_id = self.combo_integrations.itemData(index)
        if integration_id:
            self.current_integration_id = integration_id
            self._load_integration_commands()
            
    def _load_integration_commands(self):
        integration = self.integrations[self.current_integration_id]
        commands = integration["commands"]
        
        self.table.setRowCount(len(commands))
        for row, cmd in enumerate(commands):
            self.table.setItem(row, 0, QTableWidgetItem(cmd["gesture"]))
            self.table.setItem(row, 1, QTableWidgetItem(cmd["event"]))
            self.table.setItem(row, 2, QTableWidgetItem(cmd["command"]))
            self.table.setItem(row, 3, QTableWidgetItem(cmd["description"]))
            
    def _get_selected_command(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None, -1
            
        row = selected_rows[0].row()
        return self.integrations[self.current_integration_id]["commands"][row], row

    def _edit_selected_command(self):
        cmd_data, row = self._get_selected_command()
        
        if not cmd_data:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um comando para editar.")
            return
            
        cmd_type = self.integrations[self.current_integration_id]["command_type"]
        
        dialog = EditCommandDialog(cmd_data, cmd_type, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_cmd = dialog.get_updated_command()
            self.integrations[self.current_integration_id]["commands"][row] = updated_cmd
            self._load_integration_commands() # Reload table
            
    def _restore_defaults(self):
        reply = QMessageBox.question(
            self, "Confirmação", 
            "Tem certeza que deseja restaurar os comandos padrão desta integração?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Restore only the current integration from DEFAULT_INTEGRATIONS
            default_integration = copy.deepcopy(DEFAULT_INTEGRATIONS[self.current_integration_id])
            self.integrations[self.current_integration_id] = default_integration
            self._load_integration_commands()

    def get_integrations(self) -> dict:
        return self.integrations
