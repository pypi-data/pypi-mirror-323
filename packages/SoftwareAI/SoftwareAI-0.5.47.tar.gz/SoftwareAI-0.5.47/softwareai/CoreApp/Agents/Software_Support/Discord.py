import discord
import sys
from discord.ext import commands
from softwareai.CoreApp.Agents.Software_Support.Alfred import Alfred

class Discord:
    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.messages = True  
        self.client_Discord = commands.Bot(command_prefix="!", intents=self.intents)
        self.Discord_token = sys.argv[4]
        Alfredclass = Alfred()
        Alfred_NordVPN_Auto_Rotate = Alfredclass.NordVPN_Auto_Rotate(
                    sys.argv[0],
                    sys.argv[1],
                    sys.argv[2],
                    sys.argv[3],
                    sys.argv[4]
                    )
        self.Alfred = Alfred_NordVPN_Auto_Rotate.Alfred


    async def send_image_to_discord(self, image_path, caption=None):
        """
        Envia uma imagem para o canal do Discord.
        :param image_path: Caminho ou URL da imagem a ser enviada.
        :param caption: Texto opcional para incluir como legenda.
        """
        try:
            channel = self.client.get_channel(self.CHANNEL_ID)
            await channel.send(content=caption, file=discord.File(image_path))
            print(f"Imagem enviada para o canal {self.CHANNEL_ID}.")
        except Exception as e:
            print(f"Erro ao enviar imagem para o canal: {e}")


    def setup_discord_handlers(self):

        @self.client_Discord.event
        async def on_ready():
            print(f'Bot conectado como {self.client_Discord.user}')

        @self.client_Discord.event
        async def on_message(message):
            if message.author == self.client_Discord.user:
                return

            Alfred_response, Deletemessage, Infractions, BanUser, total_tokens, prompt_tokens, completion_tokens = self.Alfred(message, message.author)

            # Deletar mensagem
            if Deletemessage:
                try:
                    await message.delete()
                except Exception as e:
                    print(f"Erro ao tentar deletar a mensagem: {e}")

            # Banir usuário
            if BanUser:
                await message.channel.send(Alfred_response)
                try:
                    await message.guild.ban(member=message.author)
                    print(f"Usuário {message.author} foi banido do servidor {message.guild.id}.")
                except Exception as e:
                    print(f"Erro ao tentar banir o usuário {message.author}: {e}")


            await message.channel.send(Alfred_response)

        @self.client_Discord.command()
        async def ping(ctx):
            await ctx.send("Pong!")


    def main_discord(self):
        self.setup_discord_handlers()
        self.client_Discord.run(self.Discord_token)  # Discord






Discordclass = Discord()
Discordclass.main_discord()