import nyaitter
from os import getenv
from dotenv import load_dotenv
load_dotenv()

bot = nyaitter.Client(token=getenv("BOT_TOKEN"))

@bot.event
async def on_ready():
    print(bot.me.name)
    post = await bot.post("**Nyaitter.py**\nテスト起動が成功しました。")
    print(f"ポストに成功しました。ID: {post.id}")

bot.login()