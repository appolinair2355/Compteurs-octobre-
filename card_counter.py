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

    # ---- comptage : 1 par SYMBOLE (sans doublon) ----
    def count_symbols(self, group: str) -> Dict[str, int]:
        counts = {s: 0 for s in ("♠️", "♥️", "♦️", "♣️")}
        for sym in self.SYMBOLS:
            counts[self.normalize(sym)] += group.count(sym)
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
        
