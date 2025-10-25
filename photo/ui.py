from anki.hooks import addHook
from aqt.utils import tooltip
from aqt.browser import Browser
from PyQt6 import QtWidgets


class UIDialog:
    width_spin = None
    height_spin = None
    text_edit = None
    count_spin = None
    target_combo = None
    source_combo_1 = None
    source_combo_2 = None

    def setup_ui(self, dialog: QtWidgets.QDialog):
        dialog.setWindowTitle("Add Images")
        dialog.resize(670, 400)

        main_layout = QtWidgets.QVBoxLayout(dialog)

        # text
        self.text_edit = QtWidgets.QTextEdit(dialog)
        self.text_edit.setReadOnly(True)
        main_layout.addWidget(self.text_edit)

        # num layout
        num_layout = QtWidgets.QGridLayout()
        main_layout.addLayout(num_layout)

        # count
        num_layout.addWidget(QtWidgets.QLabel("Count:"), 0, 0)
        self.count_spin = QtWidgets.QSpinBox()
        self.count_spin.setRange(1, 5)  # Ограничение до 5
        num_layout.addWidget(self.count_spin, 0, 1)

        # width
        num_layout.addWidget(QtWidgets.QLabel("Width:"), 1, 0)
        self.width_spin = QtWidgets.QSpinBox()
        self.width_spin.setRange(1, 9999)
        self.width_spin.setValue(500)
        num_layout.addWidget(self.width_spin, 1, 1)

        # height
        num_layout.addWidget(QtWidgets.QLabel("Height:"), 2, 0)
        self.height_spin = QtWidgets.QSpinBox()
        self.height_spin.setRange(1, 9999)
        self.height_spin.setValue(500)
        num_layout.addWidget(self.height_spin, 2, 1)

        # key layout
        key_layout = QtWidgets.QGridLayout()
        main_layout.addLayout(key_layout)

        # target
        key_layout.addWidget(QtWidgets.QLabel("Target Field:"), 0, 0)
        self.target_combo = QtWidgets.QComboBox()
        key_layout.addWidget(self.target_combo, 0, 1)

        # source 1
        key_layout.addWidget(QtWidgets.QLabel("Source Field 1:"), 1, 0)
        self.source_combo_1 = QtWidgets.QComboBox()
        key_layout.addWidget(self.source_combo_1, 1, 1)

        # source 2
        key_layout.addWidget(QtWidgets.QLabel("Source Field 2:"), 2, 0)
        self.source_combo_2 = QtWidgets.QComboBox()
        key_layout.addWidget(self.source_combo_2, 2, 1)

    def add_text(self, text: str):
        self.text_edit.append(text)

    def set_target_fields(self, fields: list[str], default: str):
        self.target_combo.addItems(fields)
        self.target_combo.setCurrentText(default)

    def set_source_1_fields(self, fields: list[str], default: str):
        self.source_combo_1.addItems(fields)
        self.source_combo_1.setCurrentText(default)

    def set_source_2_fields(self, fields: list[str], default: str):
        self.source_combo_2.addItems(fields)
        self.source_combo_2.setCurrentText(default)