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

    def report_and_reset(self) -> str:
        total = sum(self._TOTAL.values())
        if total == 0:
            return "📊 Aucune carte cumulée pour le moment."
        lines = ["📊 Bilan cumulé (cartes)"]
        for s in ("♠️", "♥️", "♦️", "♣️"):
            pct = self._TOTAL[s] * 100 / total
            lines.append(f"{s} : {self._TOTAL[s]}  ({pct:.1f} %)")
        self._TOTAL = {s: 0 for s in ("♠️", "♥️", "♦️", "♣️")}
        return "\n".join(lines)
                  
