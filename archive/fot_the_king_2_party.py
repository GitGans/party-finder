import itertools

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
        # Ближний/дальний бой (минимум по 1)
        melee_count = sum(ch["Ближний бой"] for ch in party)
        ranged_count = sum(not ch["Ближний бой"] for ch in party)
        if melee_count < 1 or ranged_count < 1:
            continue
        # Максимумы по параметрам
        max_stats = {p: max(ch[p] for ch in party) for p in params}
        # Проверка мин. значений: отдельные > общая > не проверяем
        ok = True
        for p in params:
            check_min = min_params[p] if p in min_params else min_value
            if check_min is not None and max_stats[p] < check_min:
                ok = False
                break
        if not ok:
            continue
        # Требования по количеству персонажей с хар-кой
        for p, (need_val, need_count) in require_counts.items():
            if sum(ch[p] >= need_val for ch in party) < need_count:
                ok = False
                break
        if not ok:
            continue
        # Сохраняем сами объекты, не только имена, для подробного вывода
        result.append(party)
    return result

def format_params(min_value, min_params, require_counts):
    lines = []
    if min_params:
        lines.append("Минимальные параметры по отдельным характеристикам:")
        for k, v in min_params.items():
            lines.append(f"  {k} >= {v}")
    if min_value is not None:
        lines.append(f"Общий минимум для остальных: {min_value}")
    if require_counts:
        lines.append("Требования по количеству персонажей с характеристикой:")
        for k, (v, cnt) in require_counts.items():
            lines.append(f"  Не менее {cnt} с {k} >= {v}")
    return "\n".join(lines)

def get_party_contributions(party, params, min_value, min_params, require_counts):
    """
    Возвращает словарь: Класс -> список 'характеристика(значение)' — те параметры,
    по которым этот персонаж дал максимальное значение для прохождения фильтра.
    """
    # Какие минимумы надо обеспечить по каждому параметру
    param_min = {p: min_params[p] if p in min_params else min_value for p in params}
    # Для всех max'ов: характеристика -> max значение
    max_stats = {p: max(ch[p] for ch in party) for p in params}

    # Кто дал максимальное значение? (на случай равенства — берём первого подходящего)
    contributors = {p: None for p in params}
    for p in params:
        # Только если минималка требуется
        check_min = param_min[p]
        if check_min is not None and max_stats[p] >= check_min:
            for ch in party:
                if ch[p] == max_stats[p]:
                    contributors[p] = ch["Класс"]
                    break

    # Требования по количеству персонажей с характеристикой (например: 2 с 'Скорость' >= 70)
    # Для них тоже фиксируем вклад (прямо имена персонажей)
    count_contributors = {}
    for p, (need_val, need_count) in require_counts.items():
        # список классов, кто подходит под требование
        filtered = [ch for ch in party if ch[p] >= need_val]
        # если таких больше нужного, возьмём только первых need_count
        for ch in filtered[:need_count]:
            count_contributors.setdefault(ch["Класс"], []).append(f"{p}({ch[p]})")

    # Собираем всё по персонажам
    class2params = {ch["Класс"]: [] for ch in party}
    for p, klass in contributors.items():
        if klass:
            class2params[klass].append(f"{p}({max_stats[p]})")
    # Добавляем "count_contributors"
    for klass, feats in count_contributors.items():
        class2params[klass].extend(feats)
    # Чтобы не было дубликатов
    for klass in class2params:
        class2params[klass] = list(sorted(set(class2params[klass])))
    return class2params

if __name__ == "__main__":
    # Пример вызова:
    min_value = 70
    min_params = {}  # Можно указать пустой словарь или None
    require_counts = {}  # Можно указать пустой словарь или None
    fixed_classes = ["Травник", "Ученый", "Монах"]

    print(format_params(min_value, min_params, require_counts))
    print(f"Фиксированные классы: {', '.join(fixed_classes) if fixed_classes else 'Нет'}")
    parties = find_parties(
        min_value=min_value,
        fixed_classes=fixed_classes,
        min_params=min_params,
        require_counts=require_counts
    )
    print(f"Всего подходящих патий: {len(parties)}")
    for party in parties:
        class2params = get_party_contributions(
            party, params, min_value, min_params, require_counts
        )
        out = []
        for ch in party:
            name = ch["Класс"]
            params_str = ', '.join(class2params[name])
            if params_str:
                out.append(f"{name} - {params_str}")
            else:
                out.append(name)
        print(", ".join(out))
