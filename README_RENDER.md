# Package de2000 - Déploiement Render.com

## 🚀 Instructions de déploiement sur Render.com:

1. **Créer un compte Render.com**
   - Aller sur https://render.com
   - S'inscrire ou se connecter avec GitHub

2. **Créer un nouveau Web Service**
   - Cliquer sur "New +" → "Web Service"
   - Connecter votre repository GitHub ou uploader le code

3. **Configuration du service**
   - **Name**: telegram-card-counter-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Port**: 10000 (automatique via render.yaml)

4. **Configurer les variables d'environnement**
   Dans l'onglet "Environment", ajouter:
   - `API_ID`: Votre Telegram API ID (my.telegram.org)
   - `API_HASH`: Votre Telegram API Hash
   - `BOT_TOKEN`: Token du bot (@BotFather)
   - `ADMIN_ID`: Votre Telegram User ID
   - `DISPLAY_CHANNEL`: ID du canal d'affichage (optionnel)
   - `PORT`: 10000 (déjà configuré)

5. **Déployer**
   - Cliquer sur "Create Web Service"
   - Le déploiement démarre automatiquement
   - Vérifier les logs pour confirmer la connexion

## 📋 Caractéristiques de2000:
✅ **Port 10000**: Configuration Render.com optimisée
✅ **Base YAML**: Stockage sans PostgreSQL
✅ **Gestion file d'attente**: Messages ⏰ → ✅/🔰
✅ **Comptage unique**: Anti-double comptage avec hash SHA256
✅ **Rapports automatiques**: Intervalle configurable
✅ **Prédictions**: Système de prédictions de cartes
✅ **Health Check**: Endpoint /health pour monitoring

## 🔧 Commandes disponibles:
- `/status` - État complet du système
- `/set_stat [id]` - Configurer canal source
- `/set_display [id]` - Configurer canal affichage
- `/intervalle [min]` - Intervalle rapports (1-120 min)
- `/bilan` - Rapport immédiat et reset
- `/reset` - Réinitialiser compteur
- `/deploy` - Package render_deploy.zip
- `/dep` - Package de2000.zip (Render.com optimisé)

## 📊 Architecture:
- **main.py**: Application principale avec port 10000
- **card_counter.py**: Logique de comptage de cartes
- **predictor.py**: Système de prédictions
- **yaml_manager.py**: Gestion données YAML
- **scheduler.py**: Planification automatique
- **render.yaml**: Configuration déploiement Render.com

## 🌐 Endpoints:
- `GET /health`: Health check (retourne "Bot OK")
- `GET /`: Root endpoint (retourne "Bot OK")

## 🗄️ Stockage YAML:
- `data/bot_config.yaml`: Configuration persistante
- `data/predictions.yaml`: Historique prédictions
- `data/auto_predictions.yaml`: Planification auto
- `data/message_log.yaml`: Anti-doublon messages
- `bot_config.json`: Backup configuration
- `interval.json`: Intervalle rapports

## ⚙️ Fonctionnement:
1. **Messages en attente (⏰)**: Mis en file d'attente
2. **Messages édités**: Détection ⏰ → ✅/🔰
3. **Messages finalisés (✅/🔰)**: Comptage immédiat
4. **Anti-doublon**: Hash SHA256 + YAML log
5. **Rapports**: Instantanés + périodiques configurables

## ⚠️ Important:
- Le dossier `data/` est créé automatiquement
- Les sessions Telegram sont générées au démarrage
- Configuration sauvegardée en YAML + JSON
- Port 10000 OBLIGATOIRE pour Render.com
- Variables d'environnement via dashboard Render.com

## 🚀 Déploiement rapide:
```bash
# 1. Décompresser de2000.zip
unzip de2000.zip

# 2. Upload sur Render.com ou GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# 3. Connecter sur Render.com et déployer
# Les variables sont dans .env.example
```

## 📈 Monitoring:
- Logs en temps réel dans dashboard Render.com
- Health check automatique: `https://your-app.onrender.com/health`
- Console output détaillé avec timestamps

🎯 Package de2000 prêt pour déploiement Render.com avec port 10000!
