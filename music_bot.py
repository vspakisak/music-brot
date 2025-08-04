import discord
from discord.ext import commands
import yt_dlp
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_audio_stream_url(query):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # ytsearch automatically fetches the first result
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]  # take first video from search results
            return info['url']
        except Exception as e:
            print(f"yt_dlp error: {e}")
            return None

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined {channel.name}")
    else:
        await ctx.send("You're not in a voice channel.")

@bot.command()
async def play(ctx, *, query):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command('join'))

    stream_url = get_audio_stream_url(query)

    if not stream_url:
        await ctx.send("Could not retrieve audio. The video may be restricted or invalid.")
        return

    vc = ctx.voice_client

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    if vc.is_playing():
        vc.stop()

    source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
    vc.play(source, after=lambda e: print(f"Playback finished: {e}"))
    await ctx.send("Now streaming audio!")

@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("Paused playback.")
    else:
        await ctx.send("Nothing is playing.")

@bot.command(name="continue")
async def continue_(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("Resumed playback.")
    else:
        await ctx.send("Nothing is paused.")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("Stopped playback.")
    else:
        await ctx.send("Nothing is playing.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("I'm not in a voice channel.")

# Start the web server
keep_alive()

# Use token from environment variable

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

