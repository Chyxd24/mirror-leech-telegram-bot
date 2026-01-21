import time
from typing import Any, Dict, Optional

from ... import user_data
from .db_handler import DbManager


PLANS: Dict[str, Dict[str, Any]] = {
    "7d": {"days": 7, "amount": 12000, "label": "7 hari — Rp12.000"},
    "14d": {"days": 14, "amount": 20000, "label": "14 hari — Rp20.000"},
    "30d": {"days": 30, "amount": 25000, "label": "30 hari — Rp25.000"},
}


def now_ts() -> int:
    return int(time.time())


def is_sub_active(uid: int) -> bool:
    end = int(user_data.get(uid, {}).get("SUB_END", 0) or 0)
    return end > now_ts()


def get_sub_end(uid: int) -> int:
    return int(user_data.get(uid, {}).get("SUB_END", 0) or 0)


def get_sub_plan(uid: int) -> str:
    return str(user_data.get(uid, {}).get("SUB_PLAN", "") or "")


def get_bound_group(uid: int) -> Optional[int]:
    g = user_data.get(uid, {}).get("SUB_GROUP")
    return int(g) if g else None


def set_subscription(uid: int, plan_id: str) -> None:
    plan = PLANS[plan_id]
    end = now_ts() + int(plan["days"]) * 86400
    user_data.setdefault(uid, {})
    user_data[uid]["SUB_PLAN"] = plan_id
    user_data[uid]["SUB_END"] = end
    DbManager().update_user_data(uid)


def set_pending_tx(uid: int, tx: Dict[str, Any]) -> None:
    user_data.setdefault(uid, {})
    user_data[uid]["SUB_TX"] = tx
    DbManager().update_user_data(uid)


def get_pending_tx(uid: int) -> Optional[Dict[str, Any]]:
    return user_data.get(uid, {}).get("SUB_TX")


def clear_pending_tx(uid: int) -> None:
    if uid in user_data and "SUB_TX" in user_data[uid]:
        del user_data[uid]["SUB_TX"]
    DbManager().update_user_data(uid)


def bind_group(uid: int, chat_id: int) -> None:
    user_data.setdefault(uid, {})
    user_data[uid]["SUB_GROUP"] = int(chat_id)
    DbManager().update_user_data(uid)


def unbind_group(uid: int) -> None:
    user_data.setdefault(uid, {})
    user_data[uid]["SUB_GROUP"] = None
    DbManager().update_user_data(uid)
