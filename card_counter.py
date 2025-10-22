import re
from typing import Dict

class CardCounter:
    SYMBOLS = ("♠️", "♥️", "♦️", "♣️", "♠", "♥", "♦", "♣")
    _TOTAL = {s: 0 for s in ("♠️", "♥️", "♦️", "♣️")}

    def extract_first_group(self, text: str) -> str:
        m = re.search(r"\(([^)]*)\)", text)
        return m.group(1) if m else ""

    def normalize(self, s: str) -> str:
        return s if s.endswith("️") else s + "️"

    # ---- comptage : 1 par SYMBOLE unique (sans doublon) ----
    def count_symbols(self, group: str) -> Dict[str, int]:
        counts = {s: 0 for s in ("♠️", "♥️", "♦️", "♣️")}
        
        # Parcourir chaque symbole et compter UNE SEULE fois chaque occurrence
        seen_positions = set()
        for sym in self.SYMBOLS:
            normalized = self.normalize(sym)
            # Chercher toutes les positions du symbole
            start = 0
            while True:
                pos = group.find(sym, start)
                if pos == -1:
                    break
                # Vérifier si cette position n'a pas déjà été comptée
                if pos not in seen_positions:
                    counts[normalized] += 1
                    seen_positions.add(pos)
                start = pos + 1
        
        return counts

    def add(self, text: str) -> None:
        g = self.extract_first_group(text)
        if not g: return
        counts = self.count_symbols(g)
        for s, c in counts.items():
            self._TOTAL[s] += c

    # ---- rapport SANS reset (instantané) ----
    def build_report(self) -> str:
        total = sum(self._TOTAL.values())
        if total == 0:
            return "📈 Compteur instantané\nAucune carte pour le moment."
        lines = ["📈 Compteur instantané"]
        for s in ("♠️", "♥️", "♦️", "♣️"):
            pct = self._TOTAL[s] * 100 / total
            lines.append(f"{s} : {self._TOTAL[s]}  ({pct:.1f} %)")
        return "\n".join(lines)

    # ---- bilan + reset (intervalle) ----
    def report_and_reset(self) -> str:
        msg = self.build_report().replace("📈 Compteur instantané", "📊 Bilan cumulé (cartes)")
        self._TOTAL = {s: 0 for s in ("♠️", "♥️", "♦️", "♣️")}
        return msg

    def reset(self) -> None:
        self._TOTAL = {s: 0 for s in ("♠️", "♥️", "♦️", "♣️")}
        
