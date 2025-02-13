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
    ConversationHandler,
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

# --- Application Flask pour garder le bot actif ---
app = Flask(__name__)

@app.route("/")
def home():
    return f"Bot actif et opérationnel depuis {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# --- Paramètres du bot ---
TOKEN = "7859942806:AAHy4pNgFunsgO4lA2wK8TLa89tSzZjvY58"
ADMIN_ID = 7392567951  # Remplacez par votre identifiant Telegram

# --- Médias ---
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
    """Crée le clavier avec les boutons pour l'utilisateur."""
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

# --- Gestion de la base de données SQLite pour le stockage persistant des utilisateurs ---
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
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

# --- Commande /start pour les utilisateurs ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await add_user(chat_id)
    try:
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

# --- Gestion des boutons pour les utilisateurs ---
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# --- Interface de gestion pour l'admin (conversation pour composer un broadcast) ---
BROADCAST_MESSAGE, CONFIRM_BROADCAST = range(2)

async def compose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /compose pour initier l'envoi d'un message via le bot (réservée à l'admin)."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Vous n'avez pas la permission d'utiliser cette commande.")
        return ConversationHandler.END
    await update.message.reply_text("Veuillez envoyer le message à diffuser à tous les utilisateurs.")
    return BROADCAST_MESSAGE

async def received_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Réception du message de broadcast saisi par l'admin."""
    text = update.message.text
    context.user_data["broadcast_message"] = text
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Oui", callback_data="confirm_yes"),
            InlineKeyboardButton("Non", callback_data="confirm_no"),
        ]
    ])
    await update.message.reply_text(
        "Voulez-vous vraiment diffuser ce message à tous les utilisateurs ?", reply_markup=keyboard
    )
    return CONFIRM_BROADCAST

async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirme ou annule le broadcast en fonction du choix de l'admin."""
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_yes":
        message = context.user_data.get("broadcast_message")
        if message:
            user_ids = await get_all_users()
            count = 0
            semaphore = asyncio.Semaphore(30)
            async def send_to_user(user_id):
                nonlocal count
                async with semaphore:
                    try:
                        await context.bot.send_message(chat_id=user_id, text=message)
                        count += 1
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi au chat {user_id}: {e}")
            tasks = [asyncio.create_task(send_to_user(user_id)) for user_id in user_ids]
            await asyncio.gather(*tasks)
            await query.edit_message_text(text=f"Message broadcast envoyé à {count} utilisateurs.")
        else:
            await query.edit_message_text(text="Aucun message à diffuser.")
    else:
        await query.edit_message_text(text="Broadcast annulé.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Annule la conversation."""
    await update.message.reply_text("Opération annulée.")
    return ConversationHandler.END

# --- Fonction pour garder le bot actif via Flask ---
def keep_alive():
    def run():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    thread = threading.Thread(target=run)
    thread.start()

# --- Fonction principale ---
async def main():
    try:
        await init_db()  # Initialiser la base de données
        application = Application.builder().token(TOKEN).build()

        # Gestionnaires pour les commandes utilisateur
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CallbackQueryHandler(handle_button))

       

        # Démarrer Flask pour garder le bot actif
        keep_alive()

        logger.info("Bot démarré avec succès!")
        await application.run_polling()
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}")
        raise




# --- Diffusion automatique améliorée avec options supplémentaires ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:  # Vérifie si l'utilisateur est l'administrateur
        return

    user_ids = await get_all_users()  # Récupère la liste de tous les utilisateurs
    count = 0
    semaphore = asyncio.Semaphore(30)  # Limite le nombre de messages envoyés simultanément à 30

    # Fonction pour envoyer un message à un utilisateur
    async def send_to_user(user_id, media=None, text=None, caption=None, reply_markup=None):
        nonlocal count
        async with semaphore:
            try:
                if text:
                    # Envoi d'un texte
                    await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
                elif media:
                    # Envoi de photos, vidéos ou fichiers
                    if isinstance(media, str) and media.endswith(('.jpg', '.png', '.jpeg')):
                        # Envoi d'une photo
                        await context.bot.send_photo(chat_id=user_id, photo=media, caption=caption, reply_markup=reply_markup)
                    elif isinstance(media, str) and media.endswith(('.mp4', '.mov')):
                        # Envoi d'une vidéo
                        await context.bot.send_video(chat_id=user_id, video=media, caption=caption, reply_markup=reply_markup)
                    elif isinstance(media, str) and media.endswith(('.pdf', '.zip')):
                        # Envoi d'un fichier
                        await context.bot.send_document(chat_id=user_id, document=media, caption=caption, reply_markup=reply_markup)
                    elif isinstance(media, list):
                        # Envoi de groupe de médias
                        await context.bot.send_media_group(chat_id=user_id, media=media)
                count += 1
                await asyncio.sleep(0.1)  # Délai pour éviter les erreurs

            except Exception as e:
                logger.error(f"Erreur d'envoi au chat {user_id}: {e}")

    tasks = []
    
    # Option de filtrage des utilisateurs (exemple: envoyer uniquement à un groupe spécifique)
    filtered_users = user_ids  # Par défaut, tous les utilisateurs reçoivent le message
    # Exemple de filtrage: si vous voulez envoyer le message uniquement aux utilisateurs qui ont un chat_id particulier
    # filtered_users = [user_id for user_id in user_ids if user_id == 123456789]

    # Vérifie le type de contenu à envoyer (texte, image, vidéo, etc.)
    if update.message.text:
        # Si c'est du texte
        text = update.message.text
        caption = "Voici votre message personnalisé"  # Texte personnalisé pour accompagner le message
        tasks = [asyncio.create_task(send_to_user(user_id, text=text, caption=caption)) for user_id in filtered_users]
    
    elif update.message.photo:
        # Si c'est une photo
        photo_url = update.message.photo[-1].file_id  # Récupère la dernière photo envoyée
        caption = "Voici une photo envoyée par l'administrateur"
        tasks = [asyncio.create_task(send_to_user(user_id, media=photo_url, caption=caption)) for user_id in filtered_users]
    
    elif update.message.video:
        # Si c'est une vidéo
        video_url = update.message.video.file_id  # Récupère la vidéo
        caption = "Voici une vidéo envoyée par l'administrateur"
        tasks = [asyncio.create_task(send_to_user(user_id, media=video_url, caption=caption)) for user_id in filtered_users]
    
    elif update.message.document:
        # Si c'est un fichier (PDF, ZIP, etc.)
        document_url = update.message.document.file_id  # Récupère le fichier
        caption = "Voici un fichier envoyé par l'administrateur"
        tasks = [asyncio.create_task(send_to_user(user_id, media=document_url, caption=caption)) for user_id in filtered_users]
    
    # Envoi des messages avec des boutons personnalisés
    elif update.message.text and "button" in update.message.text.lower():
        # Si le texte contient "button", ajouter un bouton dans le message
        button = InlineKeyboardButton("Cliquez ici", url="https://example.com")
        reply_markup = InlineKeyboardMarkup([[button]])
        text = "Voici un message avec un bouton personnalisé"
        tasks = [asyncio.create_task(send_to_user(user_id, text=text, reply_markup=reply_markup)) for user_id in filtered_users]
    
    # Envoie de la diffusion
    await asyncio.gather(*tasks)
    await update.message.reply_text(f"📢 Message envoyé à {count} utilisateurs.")



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
