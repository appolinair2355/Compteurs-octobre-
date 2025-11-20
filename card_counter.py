import re
from typing import Dict

class CardCounter:
    # On ne garde que les clés principales normalisées ici
    # Les variantes textes sont gérées dans la logique de comptage
    SYMBOLS_KEYS = ("♠️", "♥️", "♦️", "♣️")
    
    def __init__(self):
        self._TOTAL = {s: 0 for s in self.SYMBOLS_KEYS}

    def extract_first_group(self, text: str) -> str:
        """Extrait UNIQUEMENT le 1er groupe entre parenthèses"""
        groups = re.findall(r"\(([^)]*)\)", text)
        return groups[0] if len(groups) >= 1 else ""

    def count_symbols(self, group: str) -> Dict[str, int]:
        """
        Compte les symboles de manière séquentielle pour éviter les doublons.
        Priorité aux émojis, puis au texte simple.
        """
        counts = {s: 0 for s in self.SYMBOLS_KEYS}
        temp_group = group  # Copie de travail

        # 1. D'abord compter les Émojis complets (ex: ♠️)
        # On utilise une liste explicite pour l'ordre de traitement
        emojis = ["♠️", "♥️", "♦️", "♣️"]
        for emoji in emojis:
            count = temp_group.count(emoji)
            counts[emoji] += count
            # IMPORTANT: On retire l'émoji trouvé pour qu'il ne soit pas 
            # recompté comme symbole texte simple ensuite
            if count > 0:
                temp_group = temp_group.replace(emoji, "")

        # 2. Ensuite compter les symboles texte restants (ex: ♠)
        # Mapping du symbole texte vers la clé émoji
        text_variants = {"♠": "♠️", "♥": "♥️", "♦": "♦️", "♣": "♣️"}
        for text_char, target_key in text_variants.items():
            count = temp_group.count(text_char)
            if count > 0:
                counts[target_key] += count

        return counts

    def add(self, text: str) -> None:
        """Compte les symboles du 1er groupe uniquement"""
        first_group = self.extract_first_group(text)
        if not first_group: return
        
        # Utiliser la nouvelle logique de comptage sécurisée
        counts = self.count_symbols(first_group)
        
        for s, c in counts.items():
            self._TOTAL[s] += c

    # ---- rapport SANS reset (instantané) ----
    def build_report(self) -> str:
        total = sum(self._TOTAL.values())
        if total == 0:
            return "📈 Compteur instantané\n♠️ : 0  (0.0 %)\n♥️ : 0  (0.0 %)\n♦️ : 0  (0.0 %)\n♣️ : 0  (0.0 %)"
        
        lines = ["📈 Compteur instantané"]
        
        for s in self.SYMBOLS_KEYS:
            count = self._TOTAL[s]
            pct = count * 100 / total
            lines.append(f"{s} : {count}  ({pct:.1f} %)")
        
        return "\n".join(lines)

    # ---- bilan + reset (intervalle) ----
    def report_and_reset(self) -> str:
        total = sum(self._TOTAL.values())
        if total == 0:
            # Reset même si vide pour garder la cohérence
            self._TOTAL = {s: 0 for s in self.SYMBOLS_KEYS}
            return "╔════════════════════╗\n📊 Bilan 📊\n╚════════════════════╝\n\n🔍 Aucune carte comptabilisée"
        
        lines = [
            "╔════════════════════╗",
            "📊 Bilan 📊",
            "╚════════════════════╝",
            ""
        ]
        
        # Symboles avec émojis colorés
        symbols_data = {
            "♠️": {"name": "PIQUE", "emoji": "⬛", "color": "🖤"},
            "♥️": {"name": "COEUR", "emoji": "🟥", "color": "❤️"},
            "♦️": {"name": "CARREAU", "emoji": "🔶", "color": "🧡"},
            "♣️": {"name": "TRÈFLE", "emoji": "🟩", "color": "💚"}
        }
        
        for s in self.SYMBOLS_KEYS:
            count = self._TOTAL[s]
            pct = count * 100 / total
            data = symbols_data[s]
            
            # Barre de progression visuelle
            bar_length = int(pct / 10)
            bar = data["emoji"] * bar_length + "⬜" * (10 - bar_length)
            
            lines.append(f"{data['color']} **{s} {data['name']}**")
            lines.append(f"├─ Compteur: **{count}** carte{'s' if count > 1 else ''}")
            lines.append(f"├─ Pourcentage: **{pct:.1f}%**")
            lines.append(f"└─ {bar}")
            lines.append("")
        
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📌 Total: {total} carte{'s' if total > 1 else ''}")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        
        # Reset après le rapport
        self._TOTAL = {s: 0 for s in self.SYMBOLS_KEYS}
        return "\n".join(lines)

    def reset(self) -> None:
        self._TOTAL = {s: 0 for s in self.SYMBOLS_KEYS}
