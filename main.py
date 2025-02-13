import nest_asyncio
nest_asyncio.apply()  # Permet d'utiliser des boucles imbriquées

import asyncio
import logging
import os
import threading
from datetime import datetime
from flask import Flask
import aiosqlite
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Configuration du logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# --- Application Flask pour Railway ---
app = Flask(__name__)

@app.route("/")
def home():
    return f"Bot actif et opérationnel depuis {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# --- Paramètres du bot ---
TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"
ADMIN_ID = 7392567951  # Remplacez par votre identifiant Telegram

# --- Médias (Toutes les images sont maintenues) ---
INTRO_VIDEO = "https://drive.google.com/uc?export=download&id=1NREjyyYDfdgGtx4r-Lna-sKgpCHIC1ia"
MAIN_IMAGE = "https://i.ytimg.com/vi/KolFup7TxOM/hq720.jpg"
BOTTOM_IMAGE = "https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png"

PAYMENT_PROOF_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/4/4e/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/1/1e/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/3/3f/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/5/5f/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/7/7f/Example-image.png"
]

INFO_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/8/8f/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/6/6f/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/2/2f/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/a/a0/Example-image.png",
    "https://upload.wikimedia.org/wikipedia/commons/c/cf/Example-image.png"
]

# --- Gestion de la base de données SQLite ---
DB_PATH = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY)""")
        await db.commit()

async def add_user(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

# --- Création des boutons ---
def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎯 Infos sur les bots", callback_data="info_bots")],
        [InlineKeyboardButton("💰 Retrait du casino", callback_data="casino_withdrawal")],
        [InlineKeyboardButton("📱 Contacter l'expert", url="https://t.me/judespronos")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_program_button():
    keyboard = [[InlineKeyboardButton("🚀 OBTENIR LE PROGRAMME MAINTENANT", url="https://t.me/judespronos")]]
    return InlineKeyboardMarkup(keyboard)

# --- Commande /start ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await add_user(chat_id)
    try:
        await context.bot.send_video(chat_id=chat_id, video=INTRO_VIDEO, caption="🎮 Découvrez notre méthode révolutionnaire ! 🎰")

        message = f"""🎯 BILL GATES, BONJOUR ❗️

Je suis un programmeur vénézuélien et je connais la combine pour retirer l'argent du jeu des casinos.

✅ 1800 personnes ont déjà gagné avec moi.
🔥 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}"""
        
        await update.message.reply_photo(photo=MAIN_IMAGE, caption=message, reply_markup=create_keyboard())
        await context.bot.send_photo(chat_id=chat_id, photo=BOTTOM_IMAGE, caption="🏆 Rejoignez les gagnants dès aujourd'hui !")

    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")

# --- Gestion des boutons ---
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id

    try:
        if query.data == "casino_withdrawal":
            await context.bot.send_message(chat_id=chat_id, text="🎰 Preuves de paiement récentes")
            media_group = [InputMediaPhoto(media=url) for url in PAYMENT_PROOF_IMAGES]
            await context.bot.send_media_group(chat_id=chat_id, media=media_group)
            await context.bot.send_message(chat_id=chat_id, text="🌟 Prêt à commencer ?", reply_markup=create_program_button())

        elif query.data == "info_bots":
            await context.bot.send_message(chat_id=chat_id, text="🤖 Notre technologie unique")
            media_group = [InputMediaPhoto(media=url) for url in INFO_IMAGES]
            await context.bot.send_media_group(chat_id=chat_id, media=media_group)
            await context.bot.send_message(chat_id=chat_id, text="🚀 Prêt à révolutionner vos gains ?", reply_markup=create_program_button())

    except Exception as e:
        logger.error(f"Erreur lors du traitement du bouton: {e}")

# --- Diffusion automatique ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    user_ids = await get_all_users()
    count = 0
    semaphore = asyncio.Semaphore(30)

    async def send_to_user(user_id):
        nonlocal count
        async with semaphore:
            try:
                await context.bot.send_message(chat_id=user_id, text=update.message.text)
                count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Erreur d'envoi au chat {user_id}: {e}")

    tasks = [asyncio.create_task(send_to_user(user_id)) for user_id in user_ids]
    await asyncio.gather(*tasks)
    await update.message.reply_text(f"📢 Message envoyé à {count} utilisateurs.")

# --- Garder le bot actif ---
def keep_alive():
    def run():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    thread = threading.Thread(target=run)
    thread.start()

# --- Lancement du bot ---
async def main():
    await init_db()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, broadcast))

    keep_alive()
    logger.info("Bot démarré avec succès!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
