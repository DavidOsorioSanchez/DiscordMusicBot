import discord
from discord.ext import commands  # Use ext.commands for commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio'}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, search):
        """Plays a song from youtube."""
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Rotom no puede encontrar el canal de voz.")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info['url']
                title = info['title']
                self.queue.append(url, title)
                await ctx.send(f"Rotom añadira a la cola: ***{title}***")
                
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegPCMAudio.from_url(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda : self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"Rotom está reproduciendo: ***{title}***")
        elif not ctx.voice_client.is_playing():
            await ctx.send("Rotom esta vacío!")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Rotom ha saltado la canción.")

client = commands.Bot(command_prefix="!", intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start(os.getenv("TOKEN"))

asyncio.run(main())