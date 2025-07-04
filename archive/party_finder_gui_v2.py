import sys
import itertools
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QCheckBox, QSpinBox, QGroupBox,
    QGridLayout, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- 1. Сначала персонажи и параметры ---
characters = [
    {"Класс": "Менестрель", "Сила": 50, "Жизнь": 64, "Интеллект": 64, "Информированность": 56, "Талант": 78, "Скорость": 74, "Ближний бой": False},
    {"Класс": "Следопыт", "Сила": 50, "Жизнь": 58, "Интеллект": 56, "Информированность": 76, "Талант": 76, "Скорость": 70, "Ближний бой": False},
    {"Класс": "Охотник", "Сила": 66, "Жизнь": 52, "Интеллект": 50, "Информированность": 78, "Талант": 66, "Скорость": 74, "Ближний бой": False},
    {"Класс": "Фермер", "Сила": 74, "Жизнь": 74, "Интеллект": 50, "Информированность": 74, "Талант": 56, "Скорость": 60, "Ближний бой": True},
    {"Класс": "Пастух", "Сила": 50, "Жизнь": 76, "Интеллект": 70, "Информированность": 76, "Талант": 50, "Скорость": 64, "Ближний бой": True},
    {"Класс": "Бродячий артист", "Сила": 76, "Жизнь": 64, "Интеллект": 50, "Информированность": 60, "Талант": 76, "Скорость": 60, "Ближний бой": False},
    {"Класс": "Монах", "Сила": 68, "Жизнь": 76, "Интеллект": 76, "Информированность": 50, "Талант": 56, "Скорость": 60, "Ближний бой": True},
    {"Класс": "Кузнец", "Сила": 74, "Жизнь": 78, "Интеллект": 50, "Информированность": 60, "Талант": 66, "Скорость": 58, "Ближний бой": True},
    {"Класс": "Подпасок", "Сила": 74, "Жизнь": 60, "Интеллект": 50, "Информированность": 68, "Талант": 56, "Скорость": 78, "Ближний бой": False},
    {"Класс": "Ученый", "Сила": 50, "Жизнь": 50, "Интеллект": 78, "Информированность": 66, "Талант": 74, "Скорость": 68, "Ближний бой": False},
    {"Класс": "Дровосек", "Сила": 78, "Жизнь": 64, "Интеллект": 50, "Информированность": 74, "Талант": 54, "Скорость": 66, "Ближний бой": False},
    {"Класс": "Алхимик", "Сила": 50, "Жизнь": 54, "Интеллект": 76, "Информированность": 60, "Талант": 70, "Скорость": 76, "Ближний бой": False},
    {"Класс": "Травник", "Сила": 50, "Жизнь": 58, "Интеллект": 76, "Информированность": 76, "Талант": 64, "Скорость": 62, "Ближний бой": False}
]
params = ["Сила", "Жизнь", "Интеллект", "Информированность", "Талант", "Скорость"]

def find_parties(
    min_value,
    fixed_classes=None,
    min_params=None,
    require_counts=None
):
    if fixed_classes is None:
        fixed_classes = []
    if min_params is None:
        min_params = {}
    if require_counts is None:
        require_counts = {}

    result = []
    available = [ch for ch in characters if ch["Класс"] not in fixed_classes]
    fixed_chars = [ch for ch in characters if ch["Класс"] in fixed_classes]
    n_to_select = 4 - len(fixed_chars)
    for combo in itertools.combinations(available, n_to_select):
        party = list(fixed_chars) + list(combo)
        melee_count = sum(ch["Ближний бой"] for ch in party)
        ranged_count = sum(not ch["Ближний бой"] for ch in party)
        if melee_count < 1 or ranged_count < 1:
            continue
        max_stats = {p: max(ch[p] for ch in party) for p in params}
        ok = True
        for p in params:
            check_min = min_params[p] if p in min_params else min_value
            if check_min is not None and max_stats[p] < check_min:
                ok = False
                break
        if not ok:
            continue
        for p, (need_val, need_count) in require_counts.items():
            if sum(ch[p] >= need_val for ch in party) < need_count:
                ok = False
                break
        if not ok:
            continue
        result.append(party)
    return result

def get_party_contributions(party, params, min_value, min_params, require_counts):
    param_min = {p: min_params[p] if p in min_params else min_value for p in params}
    max_stats = {p: max(ch[p] for ch in party) for p in params}
    contributors = {p: None for p in params}
    for p in params:
        check_min = param_min[p]
        if check_min is not None and max_stats[p] >= check_min:
            for ch in party:
                if ch[p] == max_stats[p]:
                    contributors[p] = ch["Класс"]
                    break
    count_contributors = {}
    for p, (need_val, need_count) in require_counts.items():
        filtered = [ch for ch in party if ch[p] >= need_val]
        for ch in filtered[:need_count]:
            count_contributors.setdefault(ch["Класс"], []).append(f"{p}({ch[p]})")
    class2params = {ch["Класс"]: [] for ch in party}
    for p, klass in contributors.items():
        if klass:
            class2params[klass].append(f"{p}({max_stats[p]})")
    for klass, feats in count_contributors.items():
        class2params[klass].extend(feats)
    for klass in class2params:
        class2params[klass] = list(sorted(set(class2params[klass])))
    return class2params

class PartyFinderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Party Finder — RPG Team Generator")
        self.resize(1050, 700)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # --- Верхний горизонтальный layout для фильтров и классов ---
        top_hbox = QHBoxLayout()

        # ---- Левая часть: блок фильтров ----
        params_box = QGroupBox("Фильтры")
        params_box.setFont(QFont("Arial", weight=QFont.Bold))
        grid = QGridLayout()

        # Минимальный общий порог
        grid.addWidget(self._bold_label("Общий минимум параметра:"), 0, 0)
        self.min_value_edit = QSpinBox()
        self.min_value_edit.setRange(0, 150)
        self.min_value_edit.setFixedWidth(70)
        self.min_value_edit.setValue(74)
        grid.addWidget(self.min_value_edit, 0, 1)

        # По характеристикам (отдельные мин значения)
        self.param_min_edits = {}
        row = 1
        for p in params:
            grid.addWidget(self._bold_label(f"{p} ≥"), row, 0)
            edit = QSpinBox()
            edit.setRange(0, 150)
            edit.setFixedWidth(70)
            edit.setValue(0)
            self.param_min_edits[p] = edit
            grid.addWidget(edit, row, 1)
            row += 1

        # Требование по количеству
        grid.addWidget(self._bold_label("Требование: не менее"), row, 0)
        self.req_param_count = QSpinBox()
        self.req_param_count.setRange(0, 4)
        self.req_param_count.setFixedWidth(70)
        self.req_param_count.setValue(0)
        grid.addWidget(self.req_param_count, row, 1)

        grid.addWidget(self._bold_label("... с характеристикой"), row+1, 0)
        self.req_param_name = QLineEdit()
        self.req_param_name.setPlaceholderText("например, Скорость")
        self.req_param_name.setFixedWidth(110)
        grid.addWidget(self.req_param_name, row+1, 1)

        grid.addWidget(self._bold_label("... ≥"), row+2, 0)
        self.req_param_value = QSpinBox()
        self.req_param_value.setRange(0, 150)
        self.req_param_value.setFixedWidth(70)
        grid.addWidget(self.req_param_value, row+2, 1)
        row += 3

        params_box.setLayout(grid)
        params_box.setFixedWidth(240)
        top_hbox.addWidget(params_box, alignment=Qt.AlignTop)

        # ---- Правая часть: блок с классами ----
        class_group = QGroupBox("Фиксированные классы (всегда в пати)")
        class_group.setFont(QFont("Arial", weight=QFont.Bold))
        layout_classes = QVBoxLayout()
        self.class_checkboxes = []
        for ch in characters:
            cb = QCheckBox(ch["Класс"])
            self.class_checkboxes.append(cb)
            layout_classes.addWidget(cb)
        class_group.setLayout(layout_classes)
        class_group.setFixedWidth(230)
        top_hbox.addWidget(class_group, alignment=Qt.AlignTop)

        # ---- Собираем верхнюю часть ----
        main_layout.addLayout(top_hbox)

        # --- Кнопка поиска ---
        btn_find = QPushButton("Подобрать пати")
        btn_find.setFont(QFont("Arial", weight=QFont.Bold))
        btn_find.setFixedHeight(28)
        main_layout.addWidget(btn_find)
        btn_find.clicked.connect(self.on_find)

        # --- Таблица результатов ---
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
        parties = find_parties(
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
            class2params = get_party_contributions(
                party, params, min_value, min_params, require_counts
            )
            for ch in party:
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(
                    ", ".join(ch["Класс"] for ch in party)
                ))
                self.table.setItem(row_idx, 1, QTableWidgetItem(ch["Класс"]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(
                    ", ".join(class2params[ch["Класс"]]) if class2params[ch["Класс"]] else "-"
                ))
                self.table.setItem(row_idx, 3, QTableWidgetItem(
                    ", ".join(f"{p}:{ch[p]}" for p in params)
                ))
                row_idx += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = PartyFinderApp()
    wnd.show()
    sys.exit(app.exec_())
