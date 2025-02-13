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












class BotHandler:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.last_broadcast_time = datetime.now()

    async def auto_broadcast_signal(self, context: ContextTypes.DEFAULT_TYPE):
        """Envoie automatiquement un signal de trading toutes les 10 secondes (+/- 1 seconde)"""
        while True:
            try:
                # Attendre 10 secondes avec une marge aléatoire de +/- 1 seconde
                wait_time = 10 + random.uniform(-1, 1)
                await asyncio.sleep(wait_time)
                
                coefficient = generate_random_coefficient()
                mise = 3000
                gain = round(coefficient * mise, 2)
                
                message = (
                    f"🚀 **SIGNAL TOUR SUIVANT Aviator Prediction** 📈\n\n"
                    f"🎯 Le coefficient pour ce tour est de **{coefficient}x**.\n\n"
                    f"💸 Imagine si tu avais misé **{mise} FCFA** et que tu gagnes **{gain} FCFA** ! 💰\n"
                    f"⚡️ Viens récupérer le hack pour le **tour suivant** ! ⏱️\n\n"
                    f"⏰ **Heure actuelle** : {datetime.now().strftime('%H:%M:%S')}\n\n"
                    '💬 **Envoie-moi le mot "BOT" par SMS @moustaphalux** pour récupérer le bot gratuitement !\n'
                )
                
                image_url = 'https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png'
                user_ids = await self.db_manager.get_all_users()
                for user_id in user_ids:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=image_url
                        )
                        await asyncio.sleep(0.1)  # Petite pause entre chaque envoi
                    except Exception as e:
                        logger.error(f"Erreur d'envoi à {user_id}: {e}")
                        
            except Exception as e:
                logger.error(f"Erreur dans auto_broadcast_signal: {e}")
                await asyncio.sleep(5)  # Attendre en cas d'erreur

    async def auto_broadcast_marathon(self, context: ContextTypes.DEFAULT_TYPE):
        """Envoie automatiquement l'annonce du Marathon Gagnant-Gagnant toutes les 2 heures (+/- 60 secondes)"""
        while True:
            try:
                # Attendre 2 heures (7200 secondes) avec une marge aléatoire de +/- 60 secondes
                wait_time = 11 + random.uniform(-2, 3)
                await asyncio.sleep(wait_time)

                message = (
                    "🏆 **MARATHON GAGNANT-GAGNANT** 🏆\n\n"
                    "🔥 **Objectif** : Faire gagner **50 000 FCFA** à chaque participant **AUJOURD’HUI** !\n\n"
                    "⏳ **Durée** : 1 heure\n\n"
                    "📹 **Je vous guiderai personnellement avec une liaison vidéo !**\n\n"
                    "💬 **Envoyez-moi 'MARATHON'** pour participer !\n\n"
                    "@moustaphalux @moustaphalux @moustaphalux"
                )

                image_url = "https://i.postimg.cc/zXtYv045/bandicam-2025-02-13-17-38-48-355.jpg"
                user_ids = await self.db_manager.get_all_users()

                for user_id in user_ids:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=message,
                            parse_mode="Markdown"
                        )
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=image_url
                        )
                        await asyncio.sleep(0.1)  # Petite pause entre chaque envoi
                    except Exception as e:
                        logger.error(f"Erreur d'envoi à {user_id}: {e}")

            except Exception as e:
                logger.error(f"Erreur dans auto_broadcast_marathon: {e}")
                await asyncio.sleep(60)  # Attendre 1 minute avant de réessayer en cas d'erreur
































    










    
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
