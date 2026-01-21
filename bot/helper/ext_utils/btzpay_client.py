import requests
from typing import Any, Dict, Optional


class BTZPayError(RuntimeError):
    pass


class BTZPayClient:
    """Minimal BTZPay QRIS client.

    Uses the documented endpoints:
      - POST /api/qris/create
      - GET  /api/qris/transaction/:transactionId?key=ACCESS_KEY
      - POST /api/qris/cancel/:transactionId
    """

    def __init__(self, base_url: str, apikey: str, timeout_s: int = 20):
        self.base_url = base_url.rstrip("/")
        self.apikey = apikey
        self.timeout_s = timeout_s

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = requests.post(url, json=payload, timeout=self.timeout_s)
        except Exception as e:
            raise BTZPayError(f"BTZPay POST failed: {e}") from e

        if r.status_code >= 400:
            raise BTZPayError(f"BTZPay POST {path} HTTP {r.status_code}: {r.text[:300]}")

        try:
            data = r.json()
        except Exception as e:
            raise BTZPayError(f"BTZPay invalid JSON: {r.text[:300]}") from e

        if not data.get("success"):
            raise BTZPayError(data.get("message") or str(data))
        return data

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = requests.get(url, timeout=self.timeout_s)
        except Exception as e:
            raise BTZPayError(f"BTZPay GET failed: {e}") from e

        if r.status_code >= 400:
            raise BTZPayError(f"BTZPay GET {path} HTTP {r.status_code}: {r.text[:300]}")

        try:
            data = r.json()
        except Exception as e:
            raise BTZPayError(f"BTZPay invalid JSON: {r.text[:300]}") from e

        if not data.get("success"):
            raise BTZPayError(data.get("message") or str(data))
        return data

    def create_qris(
        self,
        *,
        amount: int,
        timeout_ms: int,
        notes: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        callback_url: str = "",
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "apikey": self.apikey,
            "amount": int(amount),
            "timeout": int(timeout_ms),
        }
        if callback_url:
            payload["callback_url"] = callback_url
        if notes:
            payload["notes"] = notes
        if metadata is not None:
            payload["metadata"] = metadata

        data = self._post("/api/qris/create", payload)
        return data["data"]

    def get_transaction(self, transaction_id: str, access_key: str) -> Dict[str, Any]:
        data = self._get(f"/api/qris/transaction/{transaction_id}?key={access_key}")
        return data["data"]

    def cancel_transaction(self, transaction_id: str, reason: str = "User cancelled") -> Dict[str, Any]:
        payload = {"apikey": self.apikey, "reason": reason}
        data = self._post(f"/api/qris/cancel/{transaction_id}", payload)
        return data.get("data") or {}
