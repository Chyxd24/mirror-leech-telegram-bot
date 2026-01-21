from pyrogram.filters import create

from ... import user_data, auth_chats, sudo_users
from ...core.config_manager import Config
from ..ext_utils.subscription_utils import is_sub_active, get_bound_group


class CustomFilters:
    async def owner_filter(self, _, update):
        user = update.from_user or update.sender_chat
        return user.id == Config.OWNER_ID

    owner = create(owner_filter)

    async def authorized_user(self, _, update):
        # update can be Message or CallbackQuery
        msg = getattr(update, "message", update)
        user = getattr(update, "from_user", None) or getattr(update, "sender_chat", None) or getattr(msg, "from_user", None) or getattr(msg, "sender_chat", None)
        uid = user.id
        chat = getattr(update, "chat", None) or getattr(msg, "chat", None)
        chat_id = chat.id
        chat_type = getattr(chat, "type", "")
        thread_id = msg.message_thread_id if getattr(msg, "topic_message", False) else None

        # Public mirror group: free for everyone
        if Config.PUBLIC_MIRROR_GROUP_ID and int(chat_id) == int(Config.PUBLIC_MIRROR_GROUP_ID):
            return True

        # Subscribers: allow in PM and in their bound group
        if is_sub_active(uid):
            if chat_type == "private":
                return True
            if chat_type in ("group", "supergroup"):
                bg = get_bound_group(uid)
                if bg and int(chat_id) == int(bg):
                    return True
        return bool(
            uid == Config.OWNER_ID
            or (
                uid in user_data
                and (
                    user_data[uid].get("AUTH", False)
                    or user_data[uid].get("SUDO", False)
                )
            )
            or (
                chat_id in user_data
                and user_data[chat_id].get("AUTH", False)
                and (
                    thread_id is None
                    or thread_id in user_data[chat_id].get("thread_ids", [])
                )
            )
            or uid in sudo_users
            or uid in auth_chats
            or chat_id in auth_chats
            and (
                auth_chats[chat_id]
                and thread_id
                and thread_id in auth_chats[chat_id]
                or not auth_chats[chat_id]
            )
        )

    authorized = create(authorized_user)

    async def sudo_user(self, _, update):
        user = update.from_user or update.sender_chat
        uid = user.id
        return bool(
            uid == Config.OWNER_ID
            or uid in user_data
            and user_data[uid].get("SUDO")
            or uid in sudo_users
        )

    sudo = create(sudo_user)

    async def subscriber_user(self, _, update):
        msg = getattr(update, "message", update)
        user = (
            getattr(update, "from_user", None)
            or getattr(update, "sender_chat", None)
            or getattr(msg, "from_user", None)
            or getattr(msg, "sender_chat", None)
        )
        uid = user.id
        # owner/sudo always allowed
        if uid == Config.OWNER_ID or uid in sudo_users:
            return True
        # explicit SUDO flag in db
        if uid in user_data and user_data[uid].get("SUDO"):
            return True
        return is_sub_active(uid)

    subscriber = create(subscriber_user)
