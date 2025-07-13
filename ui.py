from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QCheckBox, QSpinBox, QGroupBox,
    QGridLayout, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models import PartyFinder
from data import params, characters


class PartyFinderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Party Finder — For The King II")
        self.resize(1050, 700)
        self.setFont(QFont("Arial", 12))
        self.party_finder = PartyFinder()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        top_hbox = QHBoxLayout()

        # ===== ФИЛЬТРЫ =====
        params_box = QGroupBox("Фильтры")
        params_box.setFont(QFont("Arial", weight=QFont.Bold))
        grid = QGridLayout()

        grid.addWidget(self._bold_label("Общий минимум:"), 0, 0)
        self.min_value_edit = QSpinBox()
        self.min_value_edit.setRange(0, 150)
        self.min_value_edit.setFixedWidth(70)
        self.min_value_edit.setValue(74)
        grid.addWidget(self.min_value_edit, 0, 1)

        self.param_min_edits = {}
        row = 1
        for p in params:
            grid.addWidget(self._bold_label(f"{p}:"), row, 0)
            edit = QSpinBox()
            edit.setRange(0, 150)
            edit.setFixedWidth(70)
            edit.setValue(0)
            self.param_min_edits[p] = edit
            grid.addWidget(edit, row, 1)
            row += 1

        grid.addWidget(self._bold_label("Минимум персонажей:"), row, 0)
        self.req_param_count = QSpinBox()
        self.req_param_count.setRange(0, 4)
        self.req_param_count.setFixedWidth(70)
        self.req_param_count.setValue(0)
        grid.addWidget(self.req_param_count, row, 1)

        grid.addWidget(self._bold_label("с характеристикой:"), row + 1, 0)
        hbox = QHBoxLayout()
        self.req_param_name = QLineEdit()
        self.req_param_name.setPlaceholderText("например, Скорость")
        self.req_param_name.setFixedWidth(185)
        hbox.addWidget(self.req_param_name)

        hbox.addSpacing(20)
        self.req_param_value = QSpinBox()
        self.req_param_value.setRange(0, 150)
        self.req_param_value.setFixedWidth(70)
        hbox.addWidget(self.req_param_value)

        grid.addLayout(hbox, row + 2, 0, 1, 2)
        row += 3

        params_box.setLayout(grid)
        params_box.setFixedWidth(300)
        top_hbox.addWidget(params_box, alignment=Qt.AlignTop)

        # ===== ТАБЛИЦА ХАРАКТЕРИСТИК =====
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(len(params) + 1)
        self.stats_table.setHorizontalHeaderLabels(["Класс"] + params)
        self.stats_table.setRowCount(len(characters))

        for row_index, ch in enumerate(characters):
            self.stats_table.setItem(row_index, 0, QTableWidgetItem(ch["Класс"]))
            for col_index, param in enumerate(params):
                value = ch.get(param, "")
                self.stats_table.setItem(row_index, col_index + 1, QTableWidgetItem(str(value)))

        self.stats_table.setFixedWidth(420)
        self.stats_table.setMaximumHeight(300)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.resizeColumnsToContents()
        top_hbox.addWidget(self.stats_table, alignment=Qt.AlignTop)

        # ===== ЧЕКБОКСЫ КЛАССОВ =====
        class_group = QGroupBox("Добавить в пати:")
        class_group.setFont(QFont("Arial", weight=QFont.Bold))
        layout_classes = QVBoxLayout()
        self.class_checkboxes = []
        for ch in characters:
            cb = QCheckBox(ch["Класс"])
            self.class_checkboxes.append(cb)
            layout_classes.addWidget(cb)
        class_group.setLayout(layout_classes)
        class_group.setFixedWidth(200)
        top_hbox.addWidget(class_group, alignment=Qt.AlignTop)

        # ===== КНОПКА + ТАБЛИЦА РЕЗУЛЬТАТОВ =====
        main_layout.addLayout(top_hbox)

        btn_find = QPushButton("Подобрать пати")
        btn_find.setFont(QFont("Arial", weight=QFont.Bold))
        btn_find.setFixedHeight(28)
        main_layout.addWidget(btn_find)
        btn_find.clicked.connect(self.on_find)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Пати", "Класс", "Вклад", "Параметры"])
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def _bold_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", weight=QFont.Bold))
        return lbl

    def on_find(self):
        min_value = self.min_value_edit.value()
        min_params = {p: edit.value() for p, edit in self.param_min_edits.items() if edit.value() > 0}
        req_count = self.req_param_count.value()
        req_param = self.req_param_name.text()
        req_val = self.req_param_value.value()
        require_counts = {}
        if req_count > 0 and req_param in params and req_val > 0:
            require_counts[req_param] = (req_val, req_count)
        fixed_classes = [cb.text() for cb in self.class_checkboxes if cb.isChecked()]
        parties = self.party_finder.find_parties(
            min_value=min_value,
            fixed_classes=fixed_classes,
            min_params=min_params,
            require_counts=require_counts
        )
        self.table.setRowCount(0)
        if not parties:
            QMessageBox.information(self, "Результат", "Нет подходящих партий!")
            return
        row_idx = 0
        for party in parties:
            class2params = self.party_finder.get_party_contributions(
                party, min_value, min_params, require_counts
            )
            for ch in party:
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(", ".join(ch.klass for ch in party)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(ch.klass))
                self.table.setItem(row_idx, 2, QTableWidgetItem(
                    ", ".join(class2params[ch.klass]) if class2params[ch.klass] else "-"
                ))
                self.table.setItem(row_idx, 3, QTableWidgetItem(
                    ", ".join(f"{p}:{ch[p]}" for p in params)
                ))
                row_idx += 1
