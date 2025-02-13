import nest_asyncio
nest_asyncio.apply()  # Permet d'utiliser des boucles imbriquées

import asyncio
import logging
import os
import threading
from datetime import datetime
from flask import Flask
import aiosqlite
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration du logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app pour garder le bot actif
app = Flask(__name__)

@app.route("/")
def home():
    return f"Bot actif et opérationnel depuis {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Token du bot et ID admin
TOKEN = "7184666905:AAFd2arfmIFZ86cp9NNVp57dKkH6hAVi4iM"
ADMIN_ID = 123456789  # Remplace par ton identifiant Telegram

# Médias
INTRO_VIDEO = "https://drive.google.com/uc?export=download&id=1NREjyyYDfdgGtx4r-Lna-sKgpCHIC1ia"
MAIN_IMAGE = "https://i.ytimg.com/vi/KolFup7TxOM/hq720.jpg"
BOTTOM_IMAGE = "https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png"

PAYMENT_PROOF_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png"
]

INFO_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png"
]

def create_keyboard():
    """Crée le clavier avec les boutons."""
    keyboard = [
        [InlineKeyboardButton("🎯 Informations sur les bots", callback_data="info_bots")],
        [InlineKeyboardButton("💰 Retrait du casino", callback_data="casino_withdrawal")],
        [InlineKeyboardButton("📱 Contacter l'expert", url="https://t.me/judespronos")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_program_button():
    """Crée le bouton pour obtenir le programme."""
    keyboard = [[InlineKeyboardButton("🚀 OBTENIR LE PROGRAMME MAINTENANT", url="https://t.me/judespronos")]]
    return InlineKeyboardMarkup(keyboard)

# --- Gestion de la base de données SQLite pour un stockage persistant des utilisateurs ---

DB_PATH = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY
            )
        """)
        await db.commit()

async def add_user(chat_id: int):
    """Ajoute un utilisateur dans la base de données."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
        await db.commit()

async def get_all_users():
    """Récupère tous les utilisateurs depuis la base de données."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

# --- Commandes du bot ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /start, enregistre l'utilisateur et envoie des messages de bienvenue."""
    chat_id = update.effective_chat.id
    await add_user(chat_id)
    try:
        # Envoie la vidéo d'introduction
        await context.bot.send_video(
            chat_id=chat_id,
            video=INTRO_VIDEO,
            caption="🎮 Découvrez notre méthode révolutionnaire ! 🎰"
        )
        message = f"""🎯 BILL GATES, BONJOUR ❗️

Je suis un programmeur vénézuélien et je connais la combine pour retirer l'argent du jeu des casinos.

✅ 1800 personnes ont déjà gagné avec moi. Et je peux vous garantir en toute confiance que vous gagnerez.

💫 Vous pouvez gagner de l'argent sans rien faire, car j'ai déjà fait tout le programme pour vous.

🔥 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}"""
        reply_markup = create_keyboard()
        await update.message.reply_photo(
            photo=MAIN_IMAGE,
            caption=message,
            reply_markup=reply_markup
        )
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=BOTTOM_IMAGE,
            caption="🏆 Rejoignez les gagnants dès aujourd'hui !"
        )
        logger.info(f"Nouvel utilisateur enregistré: {chat_id}")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage pour le chat {chat_id}: {e}")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    try:
        if query.data == "casino_withdrawal":
            await context.bot.send_message(
                chat_id=chat_id,
                text="""🎰 PREUVES DE PAIEMENT RÉCENTES 🎰

💎 Ces retraits ont été effectués dans les dernières 24 heures
✨ Nos utilisateurs gagnent en moyenne 500€ par jour
⚡️ Méthode 100% automatisée et garantie
🔒 Aucun risque de perte

👇 Voici les preuves en images 👇"""
            )
            media_group = [InputMediaPhoto(media=url) for url in PAYMENT_PROOF_IMAGES]
            await context.bot.send_media_group(
                chat_id=chat_id,
                media=media_group
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text="🌟 Prêt à commencer votre succès ?",
                reply_markup=create_program_button()
            )
        elif query.data == "info_bots":
            await context.bot.send_message(
                chat_id=chat_id,
                text="""🤖 NOTRE TECHNOLOGIE UNIQUE 🤖

✅ Intelligence artificielle avancée
🎯 Taux de réussite de 98.7%
💫 Mise à jour quotidienne des algorithmes
⚡️ Plus de 1800 utilisateurs satisfaits

👇 Découvrez notre système en images 👇"""
            )
            media_group = [InputMediaPhoto(media=url) for url in INFO_IMAGES]
            await context.bot.send_media_group(
                chat_id=chat_id,
                media=media_group
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text="🚀 Prêt à révolutionner vos gains ?",
                reply_markup=create_program_button()
            )
        logger.info(f"Bouton {query.data} cliqué par l'utilisateur {chat_id}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du bouton pour le chat {chat_id}: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Une erreur est survenue. Veuillez réessayer."
        )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Commande /broadcast réservée à l'admin.
    Envoie un message (passé en argument) à tous les utilisateurs enregistrés.
    Utilise un contrôle de la concurrence pour éviter de saturer l'API Telegram.
    """
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Vous n'avez pas la permission d'utiliser cette commande.")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Veuillez fournir un message à diffuser.")
        return

    user_ids = await get_all_users()
    count = 0
    semaphore = asyncio.Semaphore(30)  # Limite de 30 envois simultanés

    async def send_to_user(user_id):
        nonlocal count
        async with semaphore:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                count += 1
                await asyncio.sleep(0.1)  # Pause pour éviter de saturer l'API
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi au chat {user_id}: {e}")

    tasks = [asyncio.create_task(send_to_user(user_id)) for user_id in user_ids]
    await asyncio.gather(*tasks)
    await update.message.reply_text(f"Message broadcast envoyé à {count} utilisateurs.")

def keep_alive():
    """Lance le serveur Flask pour garder le bot actif."""
    def run():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    thread = threading.Thread(target=run)
    thread.start()

async def main():
    """Fonction principale pour démarrer le bot."""
    try:
        await init_db()  # Initialiser la base de données
        application = Application.builder().token(TOKEN).build()

        # Ajout des gestionnaires de commandes et callbacks
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CallbackQueryHandler(handle_button))
        application.add_handler(CommandHandler("broadcast", broadcast))  # Commande réservée à l'admin

        # Démarrage du serveur Flask
        keep_alive()

        logger.info("Bot démarré avec succès!")
        await application.run_polling()
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
