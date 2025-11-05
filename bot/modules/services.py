from time import time

from ..helper.ext_utils.bot_utils import new_task
from ..helper.telegram_helper.button_build import ButtonMaker
from ..helper.telegram_helper.message_utils import send_message, edit_message, send_file
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands


# === RULES TEXT (HTML READY) ===
RULES_TEXT = """<b>📜 RULES – MIRROR BOT</b>

<b>🇮🇩 Bahasa Indonesia:</b>

<b>1. Umum</b><br>
Bot ini disediakan untuk membantu proses <i>mirror</i>, <i>upload</i>, dan <i>leeching</i> dari berbagai sumber ke cloud atau Telegram.<br>
Gunakan bot ini dengan bijak dan sesuai dengan ketentuan yang berlaku.<br>
Segala bentuk penyalahgunaan akan mengakibatkan <b>pemblokiran permanen</b> dari sistem.

<b>2. Batasan Penggunaan</b><br>
• Jangan melakukan <i>spam command</i> atau menjalankan beberapa tugas bersamaan tanpa izin.<br>
• Jangan unggah atau <i>mirror</i> konten ilegal, pornografi, atau materi berhak cipta tanpa izin pemilik.<br>
• Hindari file berukuran sangat besar yang dapat mengganggu server (ikuti batas ukuran yang berlaku).

<b>3. Privasi & Keamanan</b><br>
Data pengguna (seperti username, ID Telegram, link yang dikirim) hanya digunakan untuk kebutuhan log dan pelacakan internal bot.<br>
Kami tidak menyimpan atau menyebarkan data pribadi pengguna kepada pihak ketiga.

<b>4. Kebijakan Pemakaian Wajar (Fair Use Policy)</b><br>
Bot ini bersifat <i>shared service</i>, jadi mohon untuk tidak memonopoli resource.<br>
Jika ditemukan penyalahgunaan, admin berhak menangguhkan akses tanpa pemberitahuan.

<b>5. Bantuan & Komunitas</b><br>
Jika kamu mengalami kendala, hubungi admin melalui PM atau grup komunitas mirror.<br>
Pastikan membaca <i>pinned message</i> atau panduan terbaru sebelum bertanya.

<b>6. Tanggung Jawab</b><br>
Admin & pengelola bot tidak bertanggung jawab atas segala konten yang di-<i>mirror</i> oleh pengguna.<br>
Semua pengguna bertanggung jawab penuh atas file yang mereka unggah atau sebarkan melalui bot.

Terima kasih telah menggunakan layanan mirror kami 💫<br>
Gunakan dengan sopan, aman, dan bertanggung jawab 🙏

<hr>

<b>🇬🇧 English Version:</b>

<b>1. General</b><br>
This bot is provided to help with mirroring, uploading, and leeching files from various sources to clouds or Telegram.<br>
Please use the bot responsibly and in accordance with these terms.<br>
Any misuse may result in a <b>permanent ban</b> from the system.

<b>2. Usage Limitations</b><br>
• Do not spam commands or run multiple tasks simultaneously without permission.<br>
• Do not mirror or upload illegal, pornographic, or copyrighted materials without proper authorization.<br>
• Avoid extremely large files that could overload the server (follow the current size limits).

<b>3. Privacy & Security</b><br>
User data (such as Telegram ID, username, or links sent) is used only for internal logging and tracking purposes.<br>
We do not store or share your private data with any third parties.

<b>4. Fair Use Policy</b><br>
This bot is a <i>shared service</i>, so please be considerate and avoid hogging the resources.<br>
Admins reserve the right to suspend any user who abuses the system without prior notice.

<b>5. Support & Community</b><br>
If you face issues, feel free to contact the admin via PM or join the mirror group community.<br>
Please read the pinned messages or latest guides before asking questions.

<b>6. Responsibility</b><br>
The admin and bot operators are not responsible for any content mirrored by users.<br>
Each user is fully responsible for the files they upload or share via the bot.

Thank you for using our mirror service 💫<br>
Please use it politely, safely, and responsibly 🙏
"""


@new_task
async def start(_, message):
    buttons = ButtonMaker()
    # tombol default
    buttons.url_button("Repo", "https://www.github.com/Chyxd24/")
    buttons.url_button("Code Owner", "https://t.me/S3LVNVMMASA")
    # tombol tambahan
    buttons.url_button("💬 Join Mirror Group", "https://t.me/mirrorleechg")
    buttons.button("📜 Rules", f"/rules")

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
async def rules(_, message):
    await send_message(message, RULES_TEXT, parse_mode="HTML")


@new_task
async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await send_message(message, "Starting Ping")
    end_time = int(round(time() * 1000))
    await edit_message(reply, f"{end_time - start_time} ms")


@new_task
async def log(_, message):
    await send_file(message, "log.txt")
    
