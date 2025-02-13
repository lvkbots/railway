import nest_asyncio 
nest_asyncio.apply()

import asyncio
import logging
import os
import threading
from datetime import datetime
from flask import Flask
import aiosqlite
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configuration du logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Application Flask
app = Flask(__name__)

@app.route("/")
def home():
    return f"Bot actif depuis {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Configuration
TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"
ADMIN_ID = 7392567951

# Ressources médias
MEDIA_RESOURCES = {
    "intro_video": "https://drive.google.com/uc?export=download&id=1NREjyyYDfdgGtx4r-Lna-sKgpCHIC1ia",
    "main_image": "https://i.ytimg.com/vi/KolFup7TxOM/hq720.jpg",
    "bottom_image": "https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png",
    "payment_proofs": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png"
    ],
    "info_images": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Circle_sign_2.svg/1024px-Circle_sign_2.svg.png"
    ]
}

# États de conversation
BROADCAST_MESSAGE, CONFIRM_BROADCAST = range(2)

class DatabaseManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY
                )
            """)
            await db.commit()

    async def add_user(self, chat_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
            await db.commit()

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT chat_id FROM users") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

class KeyboardManager:
    @staticmethod
    def create_main_keyboard():
        keyboard = [
            [InlineKeyboardButton("🎯 Informations sur les bots", callback_data="info_bots")],
            [InlineKeyboardButton("💰 Retrait du casino", callback_data="casino_withdrawal")],
            [InlineKeyboardButton("📱 Contacter l'expert", url="https://t.me/judespronos")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_program_button():
        keyboard = [[InlineKeyboardButton("🚀 OBTENIR LE PROGRAMME MAINTENANT", url="https://t.me/judespronos")]]
        return InlineKeyboardMarkup(keyboard)

class BotHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await self.db_manager.add_user(chat_id)
        try:
            await context.bot.send_video(
                chat_id=chat_id,
                video=MEDIA_RESOURCES["intro_video"],
                caption="🎮 Découvrez notre méthode révolutionnaire ! 🎰"
            )
            
            message = f"""🎯 BILL GATES, BONJOUR ❗️

Je suis un programmeur vénézuélien et je connais la combine pour retirer l'argent du jeu des casinos.

✅ 1800 personnes ont déjà gagné avec moi. Et je peux vous garantir en toute confiance que vous gagnerez.

💫 Vous pouvez gagner de l'argent sans rien faire, car j'ai déjà fait tout le programme pour vous.

🔥 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}"""

            await update.message.reply_photo(
                photo=MEDIA_RESOURCES["main_image"],
                caption=message,
                reply_markup=KeyboardManager.create_main_keyboard()
            )
            
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=MEDIA_RESOURCES["bottom_image"],
                caption="🏆 Rejoignez les gagnants dès aujourd'hui !"
            )
            
        except Exception as e:
            logger.error(f"Erreur start: {chat_id}: {e}")

    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = update.effective_chat.id
        
        try:
            if query.data == "casino_withdrawal":
                await self._handle_withdrawal(context, chat_id)
            elif query.data == "info_bots":
                await self._handle_info(context, chat_id)
                
        except Exception as e:
            logger.error(f"Erreur bouton {chat_id}: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Une erreur est survenue. Réessayez."
            )

    async def _handle_withdrawal(self, context, chat_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="""🎰 PREUVES DE PAIEMENT RÉCENTES 🎰

💎 Ces retraits ont été effectués dans les dernières 24 heures
✨ Nos utilisateurs gagnent en moyenne 500€ par jour
⚡️ Méthode 100% automatisée et garantie
🔒 Aucun risque de perte

👇 Voici les preuves en images 👇"""
        )
        media_group = [InputMediaPhoto(media=url) for url in MEDIA_RESOURCES["payment_proofs"]]
        await context.bot.send_media_group(chat_id=chat_id, media=media_group)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🌟 Prêt à commencer votre succès ?",
            reply_markup=KeyboardManager.create_program_button()
        )

    async def _handle_info(self, context, chat_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text="""🤖 NOTRE TECHNOLOGIE UNIQUE 🤖

✅ Intelligence artificielle avancée
🎯 Taux de réussite de 98.7%
💫 Mise à jour quotidienne des algorithmes
⚡️ Plus de 1800 utilisateurs satisfaits

👇 Découvrez notre système en images 👇"""
        )
        media_group = [InputMediaPhoto(media=url) for url in MEDIA_RESOURCES["info_images"]]
        await context.bot.send_media_group(chat_id=chat_id, media=media_group)
        await context.bot.send_message(
            chat_id=chat_id,
            text="🚀 Prêt à révolutionner vos gains ?",
            reply_markup=KeyboardManager.create_program_button()
        )

class AdminHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def compose(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("Permission refusée.")
            return ConversationHandler.END
        await update.message.reply_text("Envoyez le message à diffuser.")
        return BROADCAST_MESSAGE

    async def broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Oui", callback_data="confirm_yes"),
            InlineKeyboardButton("Non", callback_data="confirm_no")
        ]])
        context.user_data["broadcast_message"] = message
        await update.message.reply_text("Voulez-vous vraiment diffuser ce message à tous les utilisateurs ?", reply_markup=keyboard)
        return CONFIRM_BROADCAST

    async def confirm_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_yes":
            message = context.user_data.get("broadcast_message")
            if message:
                await self._send_broadcast(context, message, query)
            else:
                await query.edit_message_text("Aucun message à diffuser.")
        else:
            await query.edit_message_text("Broadcast annulé.")
        return ConversationHandler.END

    async def _send_broadcast(self, context, message, query):
        user_ids = await self.db_manager.get_all_users()
        count = 0
        sem = asyncio.Semaphore(30)

        async def send_to_user(user_id):
            nonlocal count
            async with sem:
                try:
                    await context.bot.send_message(chat_id=user_id, text=message)
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Erreur broadcast {user_id}: {e}")

        tasks = [send_to_user(user_id) for user_id in user_ids]
        await asyncio.gather(*tasks)
        await query.edit_message_text(f"Message envoyé à {count} utilisateurs.")

def keep_alive():
    def run():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    thread = threading.Thread(target=run)
    thread.start()

async def main():
    try:
        db_manager = DatabaseManager()
        await db_manager.init_db()
        
        bot_handler = BotHandler(db_manager)
        admin_handler = AdminHandler(db_manager)
        
        application = Application.builder().token(TOKEN).build()
        
        # Handlers utilisateur
        application.add_handler(CommandHandler("start", bot_handler.start_command))
        application.add_handler(CallbackQueryHandler(bot_handler.handle_button))
        
        # Handlers admin
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("compose", admin_handler.compose)],
            states={
                BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler.broadcast_message)],
                CONFIRM_BROADCAST: [CallbackQueryHandler(admin_handler.confirm_broadcast)]
            },
            fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
        )
        application.add_handler(conv_handler)
        
        keep_alive()
        logger.info("Bot démarré!")
        await application.run_polling()
        
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
