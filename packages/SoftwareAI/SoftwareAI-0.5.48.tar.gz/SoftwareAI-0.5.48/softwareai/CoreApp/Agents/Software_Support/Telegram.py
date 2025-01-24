
# IMPORT SoftwareAI Libs 
from softwareai.CoreApp._init_libs_ import *
#########################################
from telegram import Bot

class Telegram:
    def __init__(self):
        self.support_telegram_init = Bot(token=self.TelegramTOKEN)
        self.support_telegram = Application.builder().token(self.TelegramTOKEN).build()

        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Olá! Como posso ajudar você hoje?')

    async def reply_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        user_id = update.message.from_user.id

        Alfred_response, Deletemessage, Infractions, BanUser, total_tokens, prompt_tokens, completion_tokens = self.Alfred(user_message, user_id)
        if Deletemessage:
            try:
                chat_id = update.effective_chat.id
                message_id = update.effective_message.message_id
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"Erro ao tentar deletar a mensagem: {e}")


        await context.bot.send_message(chat_id=update.effective_chat.id, text=Alfred_response)

    async def handle_channel_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lida com mensagens enviadas para um canal específico."""
        if update.message.chat_id == self.CHANNEL_ID:
            user_message = update.message.text
            user_id = update.message.from_user.id  # Opcional, para rastrear o usuário
            chat_id = update.effective_chat.id
            message_id = update.effective_message.message_id

            Alfred_response, Deletemessage, Infractions, BanUser, total_tokens, prompt_tokens, completion_tokens = self.Alfred(user_message, user_id)
            # Deletar mensagem do usuário
            if Deletemessage:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    print(f"Erro ao tentar deletar a mensagem: {e}")

            # Banir usuário
            if BanUser:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=Alfred_response)
                
                try:
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                    print(f"Usuário {user_id} foi banido do canal {chat_id}.")
                except Exception as e:
                    print(f"Erro ao tentar banir o usuário {user_id}: {e}")

    async def send_image_to_channel(self, image_path, caption=None):
        """
        Envia uma imagem para o canal.
        :param image_path: Caminho ou URL da imagem a ser enviada.
        :param caption: Texto opcional para incluir como legenda.
        """
        try:
            await self.support_telegram_init.send_photo(
                chat_id=self.CHANNEL_ID,
                photo=image_path,
                caption=caption
            )
            print(f"Imagem enviada para o canal {self.CHANNEL_ID}.")
        except Exception as e:
            print(f"Erro ao enviar imagem para o canal: {e}")

    async def handle_task(self, image_path, caption):
        """
        Exemplo de função chamadora que envia a imagem.
        """
        await self.send_image_to_channel(image_path, caption)




    def main_telegram(self):
        asyncio.set_event_loop(asyncio.new_event_loop())  # Cria um novo loop para a thread atual

        # Handler para o comando /start
        self.support_telegram.add_handler(CommandHandler("start", self.start))

        # Handler para mensagens diretas
        self.support_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.reply_message))

        # Handler para mensagens de canais
        self.support_telegram.add_handler(MessageHandler(filters.TEXT & filters.Chat(self.CHANNEL_ID), self.handle_channel_message))

        self.support_telegram.run_polling()  # Telegram

