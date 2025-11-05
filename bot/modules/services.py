from time import time

from ..helper.ext_utils.bot_utils import new_task
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.telegram_helper.message_utils import send_message, edit_message, send_file
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands


@new_task
async def start(_, message):
    buttons = ButtonMaker()
    # tombol default
    buttons.url_button("Repo", "https://www.github.com/Chyxd24/")
    buttons.url_button("Code Owner", "https://t.me/S3LVNVMMASA")
    # tombol tambahan (custom kamu)
    buttons.url_button("💬 Join Mirror Group", "https://t.me/mirrorleechg")
    buttons.url_button("📜 Rules", "https://t.me/mirrorleechg")

    reply_markup = buttons.build_menu(2)

    if await CustomFilters.authorized(_, message):
        start_string = f"""✅ Anda sudah diberi akses oleh admin.
✅ You have been granted access by the admin.

Gunakan bot ini untuk melakukan mirror, leech, dan upload ke berbagai cloud.
Use this bot to mirror, leech, and upload to your connected cloud services.

💡 Tips:
Ketik /{BotCommands.HelpCommand} untuk melihat semua perintah yang tersedia.
Type /{BotCommands.HelpCommand} to see the list of available commands.

Terima kasih telah menjadi bagian dari komunitas ini 💫
Thank you for being part of our mirror community!
"""
        await send_message(message, start_string, reply_markup)

    else:
        start_string = f"""🌸 Halo! / Hi there!

Bot ini di-host oleh tim kami 💫
This mirror bot is hosted by our team.

🔹 Ingin akses dan bisa menggunakan bot?
Want to get access to use this bot?

• Kirim pesan pribadi ke admin 👉 @S3LVNVMMASA
  (Send a private message to the admin)
• Atau bergabung ke grup publik kami 👉 https://t.me/mirrorleechg
  (Or join our public mirror group)

Pastikan membaca peraturan sebelum menggunakan bot.
Please make sure to read the rules before using the bot.

Ketik /{BotCommands.HelpCommand} untuk daftar perintah yang tersedia.
Type /{BotCommands.HelpCommand} to see available commands.
"""
        await send_message(message, start_string, reply_markup)


@new_task
async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await send_message(message, "Starting Ping")
    end_time = int(round(time() * 1000))
    await edit_message(reply, f"{end_time - start_time} ms")


@new_task
async def log(_, message):
    await send_file(message, "log.txt")
    
