from pyrogram import Client, filters
import requests
import os
import subprocess
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "txt-bulk-bot",
    api_id=35181357
    api_hash=249b30d940f4b4becf452da0c7101320
    bot_token=8519507737:AAE4b-3Gk8YBMQkR_p8jra1-XGaG9skXhl4
)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def is_m3u8(link):
    return ".m3u8" in link

@app.on_message(filters.document & filters.private)
async def handle_txt(client, message):
    if not message.document.file_name.endswith(".txt"):
        await message.reply("❌ Please send only .txt file")
        return

    file_path = await message.download()
    await message.reply("✅ TXT file received, processing...")

    with open(file_path, "r") as f:
        links = f.read().splitlines()

    for link in links:
        if link.strip() == "":
            continue

        try:
            if is_m3u8(link):
                await message.reply(f"🎬 Converting M3U8: {link}")

                output_file = os.path.join(DOWNLOAD_FOLDER, "video.mp4")
                cmd = [
                    "ffmpeg",
                    "-i", link,
                    "-c", "copy",
                    "-bsf:a", "aac_adtstoasc",
                    output_file
                ]

                subprocess.run(cmd)

                await client.send_document(message.chat.id, output_file)
                os.remove(output_file)

            else:
                await message.reply(f"⬇️ Downloading: {link}")
                r = requests.get(link)
                filename = link.split("/")[-1]
                save_path = os.path.join(DOWNLOAD_FOLDER, filename)

                with open(save_path, "wb") as out:
                    out.write(r.content)

                await client.send_document(message.chat.id, save_path)
                os.remove(save_path)

        except Exception:
            await message.reply(f"❌ Failed: {link}")


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🤖 Send me a .txt file with links")

app.run()
