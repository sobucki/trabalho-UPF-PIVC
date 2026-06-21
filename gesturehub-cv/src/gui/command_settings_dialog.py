import copy
import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QMessageBox, QHeaderView, QInputDialog
)
from .edit_command_dialog import EditCommandDialog
from .add_command_dialog import AddCommandDialog

from src.integrations.default_configs import DEFAULT_INTEGRATIONS
from src.vision.gesture_labels import list_assignable_gestures

class CommandSettingsDialog(QDialog):
    def __init__(self, parent=None, integrations=None, active_integration_id="presentations"):
        super().__init__(parent)
        self.setWindowTitle("Configuração de comandos")
        self.resize(700, 450)

        # Keep an in-memory copy of settings
        if integrations is not None:
            self.integrations = copy.deepcopy(integrations)
        else:
            self.integrations = copy.deepcopy(DEFAULT_INTEGRATIONS)

        self.current_integration_id = active_integration_id

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
            
        index = self.combo_integrations.findData(self.current_integration_id)
        if index >= 0:
            self.combo_integrations.setCurrentIndex(index)
            
        self.combo_integrations.currentIndexChanged.connect(self._on_integration_changed)

        layout.addWidget(self.combo_integrations)
        layout.addStretch()

        self.btn_new_integration = QPushButton("Nova integração")
        self.btn_new_integration.clicked.connect(self._create_new_integration)
        layout.addWidget(self.btn_new_integration)

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
        
        self.btn_add = QPushButton("Adicionar comando")
        self.btn_add.clicked.connect(self._add_command)

        self.btn_edit = QPushButton("Editar selecionado")
        self.btn_edit.clicked.connect(self._edit_selected_command)

        self.btn_delete = QPushButton("Excluir selecionado")
        self.btn_delete.clicked.connect(self._delete_selected_command)

        self.btn_save = QPushButton("Confirmar")
        self.btn_save.clicked.connect(self.accept)

        self.btn_restore = QPushButton("Restaurar padrão")
        self.btn_restore.clicked.connect(self._restore_defaults)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
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
            
    def _add_command(self):
        integration = self.integrations[self.current_integration_id]
        used_events = {cmd["event"] for cmd in integration["commands"]}
        available_gestures = [
            gesture for gesture in list_assignable_gestures()
            if gesture["event"] not in used_events
        ]

        if not available_gestures:
            QMessageBox.information(
                self, "Aviso",
                "Todos os gestos disponíveis já estão mapeados nesta integração."
            )
            return

        dialog = AddCommandDialog(available_gestures, integration["command_type"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_command = dialog.get_new_command()
            integration["commands"].append(new_command)
            self._load_integration_commands()

    def _delete_selected_command(self):
        cmd_data, row = self._get_selected_command()

        if not cmd_data:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um comando para excluir.")
            return

        reply = QMessageBox.question(
            self, "Confirmação",
            f"Tem certeza que deseja excluir o comando do gesto \"{cmd_data['gesture']}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.integrations[self.current_integration_id]["commands"][row]
            self._load_integration_commands()

    COMMAND_TYPE_LABELS = {
        "Teclado (atalhos de teclas, ex: Esc, Seta Direita, F5)": "keyboard",
        "Teclas de mídia (play/pause, volume, próxima faixa)": "media_key",
    }

    def _create_new_integration(self):
        name, ok = QInputDialog.getText(self, "Nova integração", "Nome da integração:")
        if not ok or not name.strip():
            return

        integration_id = self._generate_integration_id(name)

        type_label, ok = QInputDialog.getItem(
            self, "Nova integração", "Tipo de comando:",
            list(self.COMMAND_TYPE_LABELS.keys()), editable=False
        )
        if not ok:
            return

        command_type = self.COMMAND_TYPE_LABELS[type_label]

        self.integrations[integration_id] = {
            "name": name.strip(),
            "command_type": command_type,
            "commands": [],
        }

        self.combo_integrations.addItem(name.strip(), integration_id)
        index = self.combo_integrations.findData(integration_id)
        self.combo_integrations.setCurrentIndex(index)

    def _generate_integration_id(self, name: str) -> str:
        base_id = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_") or "integration"
        integration_id = base_id
        counter = 2
        while integration_id in self.integrations:
            integration_id = f"{base_id}_{counter}"
            counter += 1
        return integration_id

    def _restore_defaults(self):
        if self.current_integration_id not in DEFAULT_INTEGRATIONS:
            QMessageBox.information(
                self, "Aviso",
                "Esta integração foi criada por você e não possui um padrão para restaurar."
            )
            return

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
