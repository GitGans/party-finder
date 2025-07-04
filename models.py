import itertools
from data import characters, params

class Character:
    def __init__(self, data):
        self.data = data
    def __getitem__(self, key):
        return self.data[key]
    @property
    def klass(self):
        return self.data["Класс"]

class PartyFinder:
    def __init__(self):
        self.characters = [Character(ch) for ch in characters]
        self.params = params

    def find_parties(self, min_value, fixed_classes=None, min_params=None, require_counts=None):
        if fixed_classes is None:
            fixed_classes = []
        if min_params is None:
            min_params = {}
        if require_counts is None:
            require_counts = {}

        result = []
        available = [ch for ch in self.characters if ch.klass not in fixed_classes]
        fixed_chars = [ch for ch in self.characters if ch.klass in fixed_classes]
        n_to_select = 4 - len(fixed_chars)
        for combo in itertools.combinations(available, n_to_select):
            party = list(fixed_chars) + list(combo)
            melee_count = sum(ch["Ближний бой"] for ch in party)
            ranged_count = sum(not ch["Ближний бой"] for ch in party)
            if melee_count < 1 or ranged_count < 1:
                continue
            max_stats = {p: max(ch[p] for ch in party) for p in self.params}
            ok = True
            for p in self.params:
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

    def get_party_contributions(self, party, min_value, min_params, require_counts):
        param_min = {p: min_params[p] if p in min_params else min_value for p in self.params}
        max_stats = {p: max(ch[p] for ch in party) for p in self.params}
        contributors = {p: None for p in self.params}
        for p in self.params:
            check_min = param_min[p]
            if check_min is not None and max_stats[p] >= check_min:
                for ch in party:
                    if ch[p] == max_stats[p]:
                        contributors[p] = ch.klass
                        break
        count_contributors = {}
        for p, (need_val, need_count) in require_counts.items():
            filtered = [ch for ch in party if ch[p] >= need_val]
            for ch in filtered[:need_count]:
                count_contributors.setdefault(ch.klass, []).append(f"{p}({ch[p]})")
        class2params = {ch.klass: [] for ch in party}
        for p, klass in contributors.items():
            if klass:
                class2params[klass].append(f"{p}({max_stats[p]})")
        for klass, feats in count_contributors.items():
            class2params[klass].extend(feats)
        for klass in class2params:
            class2params[klass] = list(sorted(set(class2params[klass])))
        return class2params
