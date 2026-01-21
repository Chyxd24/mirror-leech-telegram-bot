import secrets
import time

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..core.config_manager import Config
from ..helper.ext_utils.bot_utils import new_task
from ..helper.ext_utils.btzpay_client import BTZPayClient, BTZPayError
from ..helper.ext_utils.subscription_utils import (
    PLANS,
    is_sub_active,
    get_sub_end,
    get_sub_plan,
    get_bound_group,
    set_pending_tx,
    get_pending_tx,
    clear_pending_tx,
    set_subscription,
    bind_group,
    unbind_group,
)
from asyncio import sleep

from pyrogram.errors import FloodWait

from ..helper.telegram_helper.message_utils import send_message


async def _send_photo(message, photo: str, caption: str, buttons=None):
    try:
        return await message.reply_photo(
            photo=photo,
            caption=caption,
            disable_notification=True,
            reply_markup=buttons,
        )
    except FloodWait as f:
        await sleep(f.value * 1.2)
        return await _send_photo(message, photo, caption, buttons)
    except Exception:
        # fallback to text
        return await send_message(message, caption, buttons)


def _fmt_time_left(end_ts: int) -> str:
    left = max(0, end_ts - int(time.time()))
    days = left // 86400
    hrs = (left % 86400) // 3600
    mins = (left % 3600) // 60
    return f"{days} hari {hrs} jam {mins} menit"


def _btz() -> BTZPayClient:
    return BTZPayClient(
        base_url=Config.BTZPAY_BASE_URL or "https://web.btzpay.my.id",
        apikey=Config.BTZPAY_APIKEY,
        timeout_s=20,
    )


def _plans_markup() -> InlineKeyboardMarkup:
    rows = []
    for pid in ("7d", "14d", "30d"):
        rows.append([InlineKeyboardButton(PLANS[pid]["label"], callback_data=f"sub buy {pid}")])
    return InlineKeyboardMarkup(rows)


async def send_subscribe_menu(message):
    caption = (
        "🔒 Untuk akses bot via *PM* dan grup kamu sendiri, kamu perlu langganan.\n\n"
        "Benefit:\n"
        "✅ Bisa pakai bot di PM (private)\n"
        "✅ Bisa pakai bot di 1 grup kamu sendiri (bind 1 grup)\n"
        "✅ Grup public mirror *gratis untuk semua*\n\n"
        "Pilih paket:"
    )
    thumb = (Config.SUBSCRIPTION_THUMBNAIL or "").strip()
    if thumb:
        # Can be URL or telegram file_id
        await _send_photo(message, thumb, caption, _plans_markup())
    else:
        await send_message(message, caption, _plans_markup())


@new_task
async def myplan(_, message):
    uid = message.from_user.id
    if not is_sub_active(uid):
        await send_message(message, "❌ Kamu belum punya langganan aktif. Ketik /start untuk berlangganan.")
        return

    end = get_sub_end(uid)
    plan = get_sub_plan(uid)
    g = get_bound_group(uid)
    text = (
        "✅ Langganan kamu *AKTIF*\n"
        f"📦 Paket: `{plan}`\n"
        f"⏳ Sisa: `{_fmt_time_left(end)}`\n"
        f"👥 Grup terikat: `{g if g else 'Belum di-bind'}`\n\n"
        "Bind grup: tambahkan bot ke grup kamu lalu ketik /bind di grup itu."
    )
    await send_message(message, text)


@new_task
async def bind_in_group(_, message):
    uid = message.from_user.id
    if not is_sub_active(uid):
        await send_message(message, "❌ Kamu belum punya langganan aktif. Beli dulu via PM: /start")
        return

    chat_id = message.chat.id

    if Config.PUBLIC_MIRROR_GROUP_ID and chat_id == int(Config.PUBLIC_MIRROR_GROUP_ID):
        await send_message(message, "Grup public mirror tidak bisa dipakai untuk bind grup pribadi.")
        return

    current = get_bound_group(uid)
    if current and current != chat_id:
        await send_message(
            message,
            f"⚠️ Kamu sudah bind ke grup lain: `{current}`.\n"
            "Kalau mau pindah, ketik /unbind di PM lalu /bind lagi di grup baru.",
        )
        return

    bind_group(uid, chat_id)
    await send_message(message, f"✅ Berhasil bind grup ini: `{chat_id}`")


@new_task
async def unbind_pm(_, message):
    uid = message.from_user.id
    if not is_sub_active(uid):
        await send_message(message, "❌ Langganan kamu tidak aktif.")
        return
    unbind_group(uid)
    await send_message(message, "✅ Unbind berhasil. Kamu bisa /bind lagi di grup lain.")


@new_task
async def subscription_callback(_, query):
    uid = query.from_user.id
    parts = query.data.split()
    # sub buy 7d | sub check | sub cancel
    if len(parts) < 2:
        await query.answer()
        return

    action = parts[1]

    if action == "buy":
        if len(parts) < 3:
            await query.answer("Paket tidak valid", show_alert=True)
            return
        plan_id = parts[2]
        if plan_id not in PLANS:
            await query.answer("Paket tidak valid", show_alert=True)
            return

        plan = PLANS[plan_id]
        order_id = secrets.token_hex(8)

        try:
            data = _btz().create_qris(
                amount=int(plan["amount"]),
                timeout_ms=int(Config.BTZPAY_TIMEOUT_MS or 900000),
                notes=f"SUB user={uid} plan={plan_id} order={order_id}",
                metadata={
                    "orderId": order_id,
                    "userId": uid,
                    "plan": plan_id,
                    "productName": f"Subscription {plan_id}",
                },
                callback_url="",  # webhook optional (polling only)
            )
        except BTZPayError as e:
            await query.answer("Gagal membuat pembayaran", show_alert=True)
            await send_message(query.message, f"❌ BTZPay error: `{e}`")
            return

        set_pending_tx(
            uid,
            {
                "plan": plan_id,
                "amount": int(plan["amount"]),
                "transactionId": data.get("transactionId"),
                "accessKey": data.get("accessKey"),
                "paymentUrl": data.get("paymentUrl"),
                "createdAt": int(time.time()),
                "expiredAt": data.get("expiredAt"),
                "status": data.get("status", "pending"),
            },
        )

        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💳 Bayar (QRIS)", url=data.get("paymentUrl"))],
                [InlineKeyboardButton("🔄 Cek pembayaran", callback_data="sub check")],
                [InlineKeyboardButton("✖️ Batalkan", callback_data="sub cancel")],
            ]
        )
        await send_message(
            query.message,
            "Silakan bayar via QRIS di link berikut.\n\n"
            f"• Paket: *{plan['label']}*\n"
            f"• Status: `pending`\n\n"
            "Setelah bayar, klik *Cek pembayaran*.",
            kb,
        )
        await query.answer()
        return

    if action == "check":
        tx = get_pending_tx(uid)
        if not tx:
            await query.answer("Tidak ada transaksi pending", show_alert=True)
            return

        try:
            info = _btz().get_transaction(tx["transactionId"], tx["accessKey"])
        except BTZPayError as e:
            await query.answer("Gagal cek status", show_alert=True)
            await send_message(query.message, f"❌ BTZPay error: `{e}`")
            return

        status = str(info.get("status") or "").lower()
        if status == "sukses":
            set_subscription(uid, tx["plan"])
            clear_pending_tx(uid)
            await send_message(
                query.message,
                "✅ Pembayaran *BERHASIL* — Langganan kamu *AKTIF*.\n\n"
                "Sekarang bind grup kamu:\n"
                "1) Tambahkan bot ke grup kamu\n"
                "2) Ketik `/bind` di grup itu\n\n"
                "Catatan: 1 user hanya bisa bind 1 grup selama langganan.",
            )
            await query.answer("Sukses ✅", show_alert=True)
            return

        if status in ("expired", "gagal", "cancel"):
            clear_pending_tx(uid)
            await send_message(
                query.message,
                f"❌ Transaksi selesai dengan status: `{status}`.\nSilakan buat transaksi baru via /start.",
            )
            await query.answer("Transaksi selesai", show_alert=True)
            return

        await query.answer(f"Status masih: {status or 'pending'}", show_alert=True)
        return

    if action == "cancel":
        tx = get_pending_tx(uid)
        if not tx:
            await query.answer("Tidak ada transaksi pending", show_alert=True)
            return
        try:
            _btz().cancel_transaction(tx["transactionId"], reason="User cancelled")
        except BTZPayError:
            pass
        clear_pending_tx(uid)
        await query.answer("Transaksi dibatalkan", show_alert=True)
        await send_message(query.message, "✖️ Transaksi dibatalkan. Kalau mau langganan, pilih paket lagi dengan /start")
        return

    await query.answer()
