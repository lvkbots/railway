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
from telegram.ext import MessageHandler, filters
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
    "main_image": "https://i.postimg.cc/05CCgr53/photo-2025-02-17-09-41-43.jpg",
    "bottom_image": "https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png",
    "payment_proofs": [
        "https://i.postimg.cc/fRDSWT41/photo-2025-02-13-14-41-26-2.jpg",
        "https://i.postimg.cc/VNHJFqSc/photo-2025-02-13-14-41-25-2.jpg",
        "https://i.postimg.cc/RF6NpWfJ/photo-2025-02-13-14-41-25.jpg",
        "https://i.postimg.cc/MH1Xxg9W/photo-2025-02-13-14-41-26.jpg",
        "https://i.postimg.cc/zDkrZJjy/bandicam-2025-02-13-17-36-48-522.jpg"
    ],
    "info_images": [
        
        "https://i.postimg.cc/6QGXDnjK/bandicam-2025-02-13-17-33-14-929.jpg",
        "https://i.postimg.cc/zf3B3yx2/bandicam-2025-02-13-17-24-18-009.jpg",
        "https://i.postimg.cc/FHzmV207/bandicam-2025-02-13-17-32-31-633.jpg",
        "https://i.postimg.cc/mgn4X8SV/bandicam-2025-02-13-17-33-57-485.jpg",
        "https://media.licdn.com/dms/image/D5622AQGO3fuy3Xsi1w/feedshare-shrink_2048_1536/0/1717229135545?e=2147483647&v=beta&t=bj-cWzd74icpjK9Vb5mL6DhXXvdCz12alcJLQvqSg3s"
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
            [InlineKeyboardButton("🎯 COMMENT LE HACK FONCTIONNE", callback_data="info_bots")],
            [InlineKeyboardButton("💰 PREUVES DE RETRAIT", callback_data="casino_withdrawal")],
            [InlineKeyboardButton("📱 Contacter l'expert", url="https://t.me/BILLGATESHACK")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def create_program_button():
        keyboard = [[InlineKeyboardButton("🚀 OBTENIR LE PROGRAMME MAINTENANT", url="https://t.me/BILLGATESHACK")]]
        return InlineKeyboardMarkup(keyboard)



















import asyncio
import logging
import random
from datetime import datetime
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler, filters
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)

class MessageBroadcaster(ABC):
    def __init__(self, db_manager, delay_seconds):
        self.db_manager = db_manager
        self.delay = delay_seconds
        self.running = True

    async def send_message_with_photo(self, context, user_id, text, photo_url, max_retries=3):
        """Méthode commune pour envoyer un message avec photo"""
        for attempt in range(max_retries):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode='Markdown'
                )
                if photo_url:
                    await asyncio.sleep(0.5)
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo_url
                    )
                return True
            except Exception as e:
                logger.error(f"Tentative {attempt + 1}/{max_retries} échouée pour {user_id}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        return False

    @abstractmethod
    async def get_message(self, user_id=None, context=None):
        """Chaque classe doit implémenter sa propre logique de message"""
        pass

    @abstractmethod
    def get_photo_url(self):
        """Chaque classe doit fournir son URL de photo"""
        pass

    async def broadcast(self, context):
        """Méthode commune de diffusion"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    await self.send_message_with_photo(
                        context,
                        user_id,
                        message,
                        self.get_photo_url()
                    )
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)

class SignalBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=10)
    
    def get_photo_url(self):
        return 'https://aviator.com.in/wp-content/uploads/2024/04/Aviator-Predictor-in-India.png'
    
    async def get_message(self, user_id=None, context=None):
        # Génération du coefficient avec distribution ciblée
        random_val = random.random()
        if random_val < 0.7:  # 70% entre 200 et 800
            coefficient = round(200 + (600 * random.random()), 2)
        elif random_val < 0.85:  # 15% entre 30.09 et 200
            coefficient = round(30.09 + (169.91 * random.random()), 2)
        else:  # 15% entre 800 et 1700.01
            coefficient = round(800 + (900.01 * random.random()), 2)
        
        mise = 3000
        gain = round(coefficient * mise, 2)
        
        # Utilisez simplement l'heure UTC ou l'heure du serveur
        current_time = datetime.now().strftime('%H:%M:%S')
        
        return (
            f"🚀 **SIGNAL TOUR SUIVANT Aviator Prediction** 📈\n\n"
            f"🎯 Le coefficient pour ce tour est de **{coefficient}x**.\n\n"
            f"💸 Mise potentielle: **{mise} FCFA** → Gain: **{gain} FCFA** ! 💰\n"
            f"⚡️ Récupère le hack pour le **tour suivant** ! ⏱️\n\n"
            f"⏰ **Heure** : {current_time} 🌍 Afrique !\n\n"
            '💬 **Envoie "BOT" à @BILLGATESHACK** pour obtenir le bot gratuitement !'
        )

class MarathonBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=87156)

    def get_photo_url(self):
        return "https://i.postimg.cc/zXtYv045/bandicam-2025-02-13-17-38-48-355.jpg"

    async def get_message(self, user_id=None, context=None):
        return (
            "🏆 **MARATHON GAGNANT-GAGNANT** 🏆\n\n"
            "🔥 **Objectif** : Faire gagner **50 000 FCFA** à chaque participant **AUJOURD'HUI** !\n\n"
            "⏳ **Durée** : 1 heure\n\n"
            "📹 **Guide personnel avec liaison vidéo !**\n\n"
            "💬 **Envoyez 'MARATHON'** pour participer !\n\n"
            "@BILLGATESHACK @BILLGATESHACK @BILLGATESHACK"
        )


class Billgates1(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=15)
    
    def get_photo_url(self):
        return "https://i.postimg.cc/Kz573z4T/photo-2025-03-14-11-13-44.jpg"
    
    async def get_message(self, user_id=None, context=None):
        return (
            "🔍 **SCHÉMA DÉVELOPPÉ POUR AVIATOR !!!** 🔍\n\n"
            "🔐 **ALGORITHME SECRET !!** 🔐\n\n"
            "⚠️ **LE PLUS IMPORTANT ! PRÉCISION DE 96 %** ⚠️\n\n"
            "👥 **JE PRENDS 5 PERSONNES MAINTENANT !!** 👥\n\n"
            "💰 **ON VA GAGNER 63 000 F AUJOURD'HUI !** 💰"
        )
    
    async def broadcast(self, context):
        """Méthode modifiée pour envoyer le texte comme caption de l'image"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    photo_url = self.get_photo_url()
                    
                    # Envoi du message comme caption de l'image en un seul message
                    try:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_url,
                            caption=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi à {user_id}: {str(e)}")
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)
                
                

class Billgates2(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=25956)
    
    def get_photo_url(self):
        return "https://i.postimg.cc/t4VhtDYp/photo-2025-03-05-19-11-53.jpg"
    
    async def get_message(self, user_id=None, context=None):
        return (
            "📱  \"Avant, je rêvais juste d'avoir un iPhone, là ! 😄 Maintenant, grâce à mon bot Telegram, j'achète tout ce que je veux sans même y penser.\"\n\n" 
            "💰 **GAINS DU JOUR:** iPad, AirPods, PlayStation… et +200 000 F aujourd'hui!\n\n" 
            "✨ **SIMPLICITÉ:** Trop facile !!!! 💸🔥\n\n" 
            "❓ **QUESTION:** Comment vous trouvez mon résultat ? Toi aussi, tu peux y arriver.\n\n" 
            "🚀 **OFFRE:** Avec juste 1500 F pour commencer, transformez ça en 10 000 F en une heure. Rejoignez @BILLGATESHACK maintenant!"
        )
    
    async def broadcast(self, context):
        """Méthode modifiée pour envoyer le texte comme caption de l'image"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    photo_url = self.get_photo_url()
                    
                    # Envoi du message comme caption de l'image en un seul message
                    try:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_url,
                            caption=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi à {user_id}: {str(e)}")
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)
        
        
        
class PromoBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=15027)

    def get_photo_url(self):
        return "https://i.postimg.cc/FHzmV207/bandicam-2025-02-13-17-32-31-633.jpg"

    async def get_message(self, user_id=None, context=None):
        first_name = "Ami"
        if context and user_id:
            try:
                chat = await context.bot.get_chat(user_id)
                first_name = chat.first_name if chat.first_name else "Ami"
            except:
                pass

        return (
            f"👋 Bonjour {first_name} !\n\n"
            "Vous avez besoin d'argent? Écrivez-moi @BILLGATESHACKe pour comprendre le programme.\n\n"
            "Dépêchez-vous !!! Les places sont limitées !\n\n"
            "@BILLGATESHACK\n\n"
            "@BILLGATESHACK\n\n"
            "@BILLGATESHACK"
        )

class InvitationBroadcaster(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=29232)

    def get_photo_url(self):
        return "https://i.postimg.cc/yxn4FPdm/bandicam-2025-02-13-17-35-47-978.jpg"

    async def get_message(self, user_id=None, context=None):
        first_name = "Ami"
        if context and user_id:
            try:
                chat = await context.bot.get_chat(user_id)
                first_name = chat.first_name if chat.first_name else "Ami"
            except:
                pass

        return (
            f"👋 Bonjour {first_name} !\n\n"
            "💰 **Avez-vous gagné de l'argent aujourd'hui ?** 💭\n\n"
            "❌ Si la réponse est non, qu'attendez-vous ? 🤔\n\n"
            "🎯 Un signe particulier ? \n\n"
            "💵 Le voici $ 💫\n\n"
            "👨‍🏫 Je suis prêt à accueillir deux nouveaux élèves et à les amener à des résultats dès aujourd'hui !\n\n"
            "@BILLGATESHACK"
        )
    
    async def broadcast(self, context):
        """Méthode modifiée pour envoyer le texte comme caption de l'image"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    photo_url = self.get_photo_url()
                    
                    # Envoi du message comme caption de l'image en un seul message
                    try:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_url,
                            caption=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi à {user_id}: {str(e)}")
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)
                
                
                
                






class Billgates3(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=44200)  # Délai de 12 heures (43200 secondes)

    def get_photo_url(self):
        return "https://i.postimg.cc/k4CF58M9/photo-2025-03-15-17-38-19.jpg"

    async def get_message(self, user_id=None, context=None):
        return (
            "🔺 Les signaux GRATOS de la journée, ça démarre demain à 15h40.\n"
            "🔺 Les signaux GRATOS du soir, c'est à 21h15.\n"
            "On joue sur 1xCasino 👇🏼\n"
            "🔺 https://casaff.top/L?tag=d_4168199m_79150c_&site=4168199&ad=79150&r=registration\n"
            "(Le bot est intégré dans le code de cette page ! Faut ABSOLUMENT passer par ce lien !)\n"
            "Allez-y et mettez au moins 900 F sur votre compte ! C'est comme ça que le bot va marcher.\n"
            "Si tu sais pas comment gagner avec le bot, écris-moi \"START\" ici \n"
            "👉 @BILLGATESHACK"
        )
    
    async def broadcast(self, context):
        """Méthode modifiée pour envoyer le texte comme caption de l'image"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    photo_url = self.get_photo_url()
                    
                    # Envoi du message comme caption de l'image en un seul message
                    try:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_url,
                            caption=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi à {user_id}: {str(e)}")
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)










class Billgates5(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=32400)  # Délai de 9 heures (32400 secondes)

    def get_photo_url(self):
        return "https://i.postimg.cc/7L30j63R/photo-2025-03-06-15-02-56.jpg"

    async def get_message(self, user_id=None, context=None):
        return (
            "Yo, les gars !💰 \n\n"
            "J'ai une équipe de développeurs programmateurs balèzes avec moi. Ensemble, on a créé un bot Telegram spécial qui déchire dans Aviator, en prédisant les coefficients🚀\n\n"
            "« Comment l'utiliser ? » Facile ! 😎 \n\n"
            "Je te donne l'accès, tu demandes un coefficient pour jouer (si t'as assez de balance sur ton compte). \n\n"
            "Le bot t'envoie le coefficient, et faut vite retirer ta mise avant que l'avion dans Aviator s'envole ! @BILLGATESHACK 💸"
        )
    
    async def broadcast(self, context):
        """Méthode modifiée pour envoyer le texte comme caption de l'image"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    photo_url = self.get_photo_url()
                    
                    # Envoi du message comme caption de l'image en un seul message
                    try:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_url,
                            caption=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi à {user_id}: {str(e)}")
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)









class Billgates4(MessageBroadcaster):
    def __init__(self, db_manager):
        super().__init__(db_manager, delay_seconds=36000)  # Délai de 10 heures (36000 secondes)

    def get_photo_url(self):
        return "https://i.postimg.cc/6QJCHRvR/photo-2025-03-07-08-13-47.jpg"

    async def get_message(self, user_id=None, context=None):
        return (
            "Ici, les gars et les filles gagnent de l'argent grâce au bot et aux signaux. 💰🤖\n"
            "Même les filles jouent et gagnent ! 🎰🔥\n"
            "Et vous, les hommes, qu'attendez-vous ? 😏\n"
            "Écris-moi et commençons à faire fortune ensemble ! 🚀💵\n"
            "Write to me, we gonna blow up this casino @BILLGATESHACK 🤫💸"
        )
    
    async def broadcast(self, context):
        """Méthode modifiée pour envoyer le texte comme caption de l'image"""
        while self.running:
            try:
                logger.info(f"Début de la diffusion pour {self.__class__.__name__}")
                users = await self.db_manager.get_all_users()
                
                for user_id in users:
                    if not self.running:
                        break
                    
                    message = await self.get_message(user_id, context)
                    photo_url = self.get_photo_url()
                    
                    # Envoi du message comme caption de l'image en un seul message
                    try:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_url,
                            caption=message,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'envoi à {user_id}: {str(e)}")
                    
                    await asyncio.sleep(0.5)

                logger.info(f"Diffusion terminée pour {self.__class__.__name__}")
                await asyncio.sleep(self.delay)

            except Exception as e:
                logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}")
                await asyncio.sleep(5)






class BotHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.signal_broadcaster = SignalBroadcaster(db_manager)
        self.marathon_broadcaster = MarathonBroadcaster(db_manager)
        self.promo_broadcaster = PromoBroadcaster(db_manager)
        self.bill_gates1 = Billgates1(db_manager)
        self.bill_gates2 = Billgates2(db_manager)
        self.bill_gates3 = Billgates3(db_manager)
        self.bill_gates4 = Billgates4(db_manager)
        self.bill_gates5 = Billgates5(db_manager)
        self.invitation_broadcaster = InvitationBroadcaster(db_manager)
        self.running = True
        self.video_sent = False 
        
        
    # Ajoutez ces fonctions ici
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envoie un message lorsque la commande /start est émise."""
        await update.message.reply_text("Bienvenue ! Ce bot est activé.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Envoie un message lorsque la commande /help est émise."""
        await update.message.reply_text("Utilisez /start pour démarrer le bot.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Répond à tous les messages directs avec le message spécifié."""
        response_message = "❌ Désolé, ce bot ne peut pas répondre à votre message.\n\n" \
                          "💬 Écrivez-moi ici @BILLGATESHACK pour obtenir le hack gratuitement!"
        
        # Vérifier si le message vient de l'admin
        if update.effective_user.id == ADMIN_ID:
            await update.message.reply_text("Message reçu, Admin.")
        else:
            await update.message.reply_text(response_message)
    async def send_video_once(self, context):
        """Envoie la vidéo une seule fois à tous les utilisateurs après 20 secondes"""
        # Vérifier si la vidéo a déjà été envoyée
        if self.video_sent:
            return
        
        # Marquer comme envoyée avant même le délai pour éviter les doubles exécutions
        self.video_sent = True
        
        # Attendre 20 secondes
        await asyncio.sleep(30)
        
        video_url = "https://drive.google.com/uc?export=download&id=1kCZ3ORyImQ1tmyaiwWYh48zkMWt3HdTm"
        
        try:
            logger.info("Envoi unique de la vidéo après délai de 20 secondes")
            users = await self.db_manager.get_all_users()
            
            for user_id in users:
                try:
                    await context.bot.send_video(
                        chat_id=user_id,
                        video=video_url,
                        caption="🔥 REGARDE CETTE VIDEO! 🔥\n\n"
                                "👀 Découvre comment nos utilisateurs gagnent CHAQUE JOUR!\n\n"
                                "💰 Tu peux changer ta vie facilement!\n\n"
                                "✈️ Réalise ton rêve d'aller en Europe!\n\n"
                                "🚀 Le hack est GRATUIT pour toi aujourd'hui!\n\n"
                                "📲 Contacte-moi ici pour l'obtenir maintenant!\n\n"
                                "@BILLGATESHACK"
                    )
                    await asyncio.sleep(0.5)  # Petit délai entre chaque envoi
                except Exception as e:
                    logger.error(f"Erreur d'envoi vidéo à {user_id}: {str(e)}")
                    
            logger.info("Envoi unique de la vidéo terminé")
            
        except Exception as e:
            logger.error(f"Erreur dans send_video_once: {str(e)}")



    


    
    async def start_command(self, update, context):
        """Gestionnaire de la commande /start"""
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        
        try:
            await self.db_manager.add_user(user_id)
            
            welcome_message = (
                f"👋 Bonjour {first_name} !\n\n"
                "🎉 Bienvenue dans notre bot de signaux Aviator!\n\n"
                "💫 Vous recevrez automatiquement nos signaux exclusifs.\n\n"
                "🚀 Restez connecté pour ne manquer aucune opportunité !"
            )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=welcome_message,
                parse_mode='Markdown'
            )
            
            await self.start(context)
            
        except Exception as e:
            logger.error(f"Erreur dans start_command pour {user_id}: {str(e)}")

    async def start(self, context: ContextTypes.DEFAULT_TYPE):
        """Démarre toutes les tâches de diffusion"""
        self.running = True
        asyncio.create_task(self.signal_broadcaster.broadcast(context))
        asyncio.create_task(self.marathon_broadcaster.broadcast(context))
        asyncio.create_task(self.bill_gates1.broadcast(context))
        asyncio.create_task(self.bill_gates2.broadcast(context))
        asyncio.create_task(self.bill_gates3.broadcast(context))
        asyncio.create_task(self.bill_gates4.broadcast(context))
        asyncio.create_task(self.bill_gates5.broadcast(context))
        asyncio.create_task(self.promo_broadcaster.broadcast(context))
        asyncio.create_task(self.invitation_broadcaster.broadcast(context))

    def stop(self):
        """Arrête toutes les tâches de diffusion"""
        self.running = False
        self.signal_broadcaster.running = False
        self.bill_gates1.running = False
        self.bill_gates2.running = False
        self.bill_gates3.running = False
        self.bill_gates4.running = False
        self.bill_gates5.running = False
        self.marathon_broadcaster.running = False
        self.promo_broadcaster.running = False
        self.invitation_broadcaster.running = False

    # Méthodes de compatibilité
    async def auto_broadcast_signal(self, context: ContextTypes.DEFAULT_TYPE):
        await self.start(context)
        asyncio.create_task(self.send_video_once(context))
        
    async def auto_broadcast_marathon(self, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def auto_broadcast_bill_gates(self, context: ContextTypes.DEFAULT_TYPE):
        pass







class TelegramBackupManager:
    def __init__(self, bot, storage_chat_id):
        """
        Initialise le gestionnaire de sauvegarde Telegram
        
        bot: L'instance du bot Telegram
        storage_chat_id: ID d'un canal ou groupe privé pour stocker les sauvegardes
        """
        self.bot = bot
        self.storage_chat_id = storage_chat_id
        
    async def backup_users_to_telegram(self, db_manager):
        """Sauvegarde la liste des utilisateurs dans un chat Telegram"""
        try:
            # Récupérer tous les utilisateurs
            users = await db_manager.get_all_users()
            
            # Créer le message avec horodatage
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            backup_data = {
                "timestamp": timestamp,
                "users": users,
                "count": len(users)
            }
            
            # Convertir en JSON formaté
            backup_json = json.dumps(backup_data, indent=2)
            
            # Option 1: Envoyer comme message texte si la liste n'est pas trop longue
            if len(users) < 100:  # Limite arbitraire pour éviter les messages trop longs
                message = f"📂 SAUVEGARDE UTILISATEURS BOT 📂\n\n"
                message += f"📅 Date: {timestamp}\n"
                message += f"👥 Nombre d'utilisateurs: {len(users)}\n\n"
                message += f"```json\n{backup_json}\n```"
                
                await self.bot.send_message(
                    chat_id=self.storage_chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
            # Option 2: Envoyer comme fichier pour les listes plus longues
            else:
                # Créer un fichier temporaire
                filename = f"users_backup_{timestamp.replace(' ', '_').replace(':', '-')}.json"
                with open(filename, 'w') as f:
                    f.write(backup_json)
                
                # Envoyer le fichier
                with open(filename, 'rb') as f:
                    await self.bot.send_document(
                        chat_id=self.storage_chat_id,
                        document=f,
                        caption=f"📂 Sauvegarde de {len(users)} utilisateurs - {timestamp}"
                    )
                
                # Supprimer le fichier temporaire
                os.remove(filename)
                
            logger.info(f"Sauvegarde Telegram effectuée: {len(users)} utilisateurs")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde Telegram: {str(e)}")
            return False

















    










    
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
        first_name = update.effective_user.first_name if update.effective_user else "utilisateur"
        
        await self.db_manager.add_user(chat_id)
        try:
            await context.bot.send_video(
                chat_id=chat_id,
                video=MEDIA_RESOURCES["intro_video"],
                caption="🎮 Découvrez notre méthode révolutionnaire ! 🎰"
            )
            
            message = f"""🎯 BONJOUR {first_name} ❗️

Je suis le hacker Bill Gates et je travaille avec des Russes, je connais la combine pour retirer l'argent des jeux casinos.

✅ 58.000 personnes ont déjà gagné avec moi. Et je peux vous garantir en toute confiance que vous gagnerez.

💫 Vous pouvez gagner de l'argent sans rien faire, car j'ai déjà fait tout le programme pour vous.

"@BILLGATESHACK"
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
✨ Nos utilisateurs gagnent en moyenne 50.000 FCFA par jour
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
            text="""🤖 COMMENT LE HACK FONCTIONNE 🤖

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
        
        # Handler pour la commande start (vous avez déjà ceci)
        application.add_handler(CommandHandler("start", bot_handler.start_command))
        
        # Ajoutez ces handlers
        application.add_handler(CommandHandler("help", bot_handler.help_command))
        
        # Handler pour les messages texte (non-administrateurs)
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~filters.Chat(ADMIN_ID),
            bot_handler.handle_message
        ))
        
        # Handler pour les boutons (vous avez déjà ceci)
        application.add_handler(CallbackQueryHandler(bot_handler.handle_button))
        
        # Handler pour tous les messages de l'admin (vous avez déjà ceci)
        application.add_handler(MessageHandler(
            filters.ALL & filters.Chat(ADMIN_ID),
            bot_handler.handle_admin_message
        ))
        
        # Utilisez votre propre ID comme storage_chat_id ou créez un canal privé dédié
        telegram_backup = TelegramBackupManager(application.bot, ADMIN_ID)  # ou un autre ID de chat privé
        
        # Fonction pour planifier les sauvegardes Telegram
        async def schedule_telegram_backups(interval_hours=24):
            while True:
                await asyncio.sleep(interval_hours * 3600)
                await telegram_backup.backup_users_to_telegram(db_manager)
        
        # Planifier des sauvegardes quotidiennes
        asyncio.create_task(schedule_telegram_backups())
        
        # Effectuer une sauvegarde initiale au démarrage
        asyncio.create_task(telegram_backup.backup_users_to_telegram(db_manager))
        
        
        
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
