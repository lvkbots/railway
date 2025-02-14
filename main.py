import nest_asyncio 
nest_asyncio.apply()

import asyncio
import logging
import os
import threading
import random
from datetime import datetime
from flask import Flask
import aiosqlite
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
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

# Ressources médias (inchangées)
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

def generate_random_coefficient():
    """Génère un coefficient aléatoire avec une forte probabilité entre 10 et 600"""
    if random.random() < 0.9:  # 90% de chance d'être entre 10 et 600
        return round(random.uniform(10, 600), 2)
    else:  # 10% de chance d'être entre 600 et 1702.03
        return round(random.uniform(600, 1702.03), 2)

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



















import asyncio
import random
import logging
from datetime import datetime
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class BotHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.running = True

    async def start(self, context: ContextTypes.DEFAULT_TYPE):
        """Lance les trois tâches en parallèle."""
        self.running = True
        asyncio.create_task(self.broadcast_signal(context))
        asyncio.create_task(self.broadcast_marathon(context))
        asyncio.create_task(self.broadcast_bill_gates(context))

    async def send_message(self, context, user_id, text, photo_url, max_retries=3):
        """Envoie un message avec photo en gérant les erreurs et les tentatives."""
        for attempt in range(max_retries):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode='Markdown'
                )
                await asyncio.sleep(1)  # Pause entre le texte et la photo
                if photo_url:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo_url
                    )
                return True
            except Exception as e:
                logger.error(f"Erreur envoi à {user_id} (Tentative {attempt+1}/{max_retries}): {e}")
                await asyncio.sleep(2)
        return False

    async def broadcast_signal(self, context: ContextTypes.DEFAULT_TYPE):
        """Diffuse le signal de trading après un délai initial de 10 secondes."""
        await asyncio.sleep(10)  # Délai initial pour le signal
        while self.running:
            try:
                coefficient = round(random.uniform(1.5, 5.0), 2)
                mise = 3000
                gain = round(coefficient * mise, 2)
                message = (
                    f"🚀 **SIGNAL TOUR SUIVANT Aviator Prediction** 📈\n\n"
                    f"🎯 Coefficient : **{coefficient}x**\n"
                    f"💸 Mise : **{mise} FCFA** → Gain : **{gain} FCFA**\n"
                    f"⏰ Heure : {datetime.now().strftime('%H:%M:%S')}\n\n"
                    '💬 **Envoyez "BOT" à @moustaphalux** pour récupérer le bot gratuitement !\n'
                )
                await self.send_to_users(
                    context,
                    message,
                    'https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png'
                )
            except Exception as e:
                logger.error(f"Erreur dans broadcast_signal: {e}")
            finally:
                # Délai entre chaque signal
                await asyncio.sleep(3420)

    async def broadcast_marathon(self, context: ContextTypes.DEFAULT_TYPE):
        """Diffuse l'annonce du Marathon après un délai initial de 20 secondes."""
        await asyncio.sleep(20)  # Délai initial pour le marathon
        while self.running:
            try:
                message = (
                    "🏆 **MARATHON GAGNANT-GAGNANT** 🏆\n\n"
                    "🔥 **Gagnez 50 000 FCFA AUJOURD'HUI !**\n\n"
                    "📹 **Suivi en vidéo en direct !**\n\n"
                    "💬 **Envoyez 'MARATHON' pour participer !**\n\n"
                    "@moustaphalux\n"
                )
                await self.send_to_users(
                    context,
                    message,
                    "https://i.postimg.cc/zXtYv045/bandicam-2025-02-13-17-38-48-355.jpg"
                )
            except Exception as e:
                logger.error(f"Erreur dans broadcast_marathon: {e}")
            finally:
                # Délai entre chaque diffusion du marathon
                await asyncio.sleep(7070)

    async def broadcast_bill_gates(self, context: ContextTypes.DEFAULT_TYPE):
        """Diffuse le message promotionnel Bill Gates après un délai initial de 15 secondes."""
        await asyncio.sleep(15)  # Délai initial pour Bill Gates
        while self.running:
            try:
                base_message = (
                    "Besoin d'argent ? Contactez @moustaphalux pour découvrir mon programme.\n\n"
                    "Dépêchez-vous, places limitées !\n\n"
                    "@moustaphalux\n"
                )
                user_ids = await self.db_manager.get_all_users()
                success_count = 0
                for user_id in user_ids:
                    if not self.running:
                        break
                    try:
                        chat = await context.bot.get_chat(user_id)
                        first_name = chat.first_name if chat.first_name else "Ami"
                        message = f"Salut {first_name}!\n\n" + base_message
                        if await self.send_message(
                            context,
                            user_id,
                            message,
                            "https://i.postimg.cc/FHzmV207/bandicam-2025-02-13-17-32-31-633.jpg"
                        ):
                            success_count += 1
                        await asyncio.sleep(0.5)
                    except Exception as user_error:
                        logger.error(f"Erreur avec l'utilisateur {user_id}: {user_error}")
                logger.info(f"Message Bill Gates envoyé à {success_count}/{len(user_ids)} utilisateurs")
            except Exception as e:
                logger.error(f"Erreur dans broadcast_bill_gates: {e}")
            finally:
                # Délai entre chaque diffusion du message Bill Gates
                await asyncio.sleep(27354)

    async def send_to_users(self, context, message, photo_url):
        """Envoie le message à tous les utilisateurs enregistrés."""
        user_ids = await self.db_manager.get_all_users()
        success_count = 0
        for user_id in user_ids:
            if not self.running:
                break
            if await self.send_message(context, user_id, message, photo_url):
                success_count += 1
            await asyncio.sleep(0.5)
        logger.info(f"Message envoyé à {success_count}/{len(user_ids)} utilisateurs")


























    










    
    async def broadcast_to_users(self, context: ContextTypes.DEFAULT_TYPE, update: Update):
        """Diffuse le message à tous les utilisateurs."""
        user_ids = await self.db_manager.get_all_users()
        count = 0
        sem = asyncio.Semaphore(30)

        async def send_to_user(user_id):
            nonlocal count
            async with sem:
                try:
                    if update.message.text:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=update.message.text
                        )
                    elif update.message.photo:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=update.message.photo[-1].file_id,
                            caption=update.message.caption
                        )
                    elif update.message.video:
                        await context.bot.send_video(
                            chat_id=user_id,
                            video=update.message.video.file_id,
                            caption=update.message.caption
                        )
                    elif update.message.document:
                        await context.bot.send_document(
                            chat_id=user_id,
                            document=update.message.document.file_id,
                            caption=update.message.caption
                        )
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Erreur d'envoi à {user_id}: {e}")

        tasks = [send_to_user(user_id) for user_id in user_ids]
        await asyncio.gather(*tasks)
        
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"✅ Message envoyé à {count} utilisateurs."
        )

    async def handle_admin_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return
        await self.broadcast_to_users(context, update)

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
        
        application = Application.builder().token(TOKEN).build()
        
        # Handler pour la commande start
        application.add_handler(CommandHandler("start", bot_handler.start_command))
        
        # Handler pour les boutons
        application.add_handler(CallbackQueryHandler(bot_handler.handle_button))
        
        # Handler pour tous les messages de l'admin
        application.add_handler(MessageHandler(
            filters.ALL & filters.Chat(ADMIN_ID),
            bot_handler.handle_admin_message
        ))
        
        # Démarrer la diffusion automatique
        asyncio.create_task(bot_handler.auto_broadcast_signal(application))
        
        keep_alive()
        logger.info("Bot démarré!")
        await application.run_polling()
        
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
