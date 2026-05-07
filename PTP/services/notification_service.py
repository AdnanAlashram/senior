import logging
 
import requests
from django.db import transaction
 
from PTP.models.expo_push_token import ExpoPushToken
from PTP.models.notification import Notification
 
logger = logging.getLogger(__name__)
 
EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
EXPO_PUSH_TIMEOUT = 5  # seconds
 
 
class NotificationService:
 
    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
 
    @classmethod
    def send_driver_notification(cls, *, driver_id: int, title: str, body: str) -> Notification:
        """
        Persist + push a notification to a driver.
        Raises ValueError if driver_id is None.
        """
        if driver_id is None:
            raise ValueError("driver_id must not be None.")
 
        return cls._send(
            user_type='driver',
            driver_id=driver_id,
            passenger_id=None,
            title=title,
            body=body,
        )
 
    @classmethod
    def send_passenger_notification(cls, *, passenger_id: int, title: str, body: str) -> Notification:
        """
        Persist + push a notification to a passenger.
        Raises ValueError if passenger_id is None.
        """
        if passenger_id is None:
            raise ValueError("passenger_id must not be None.")
 
        return cls._send(
            user_type='passenger',
            driver_id=None,
            passenger_id=passenger_id,
            title=title,
            body=body,
        )
 
    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
 
    @classmethod
    @transaction.atomic
    def _send(
        cls,
        *,
        user_type: str,
        driver_id,
        passenger_id,
        title: str,
        body: str,
    ) -> Notification:
        # 1. Persist to DB first — always
        notification = Notification.objects.create(
            user_type=user_type,
            driver_id=driver_id,
            passenger_id=passenger_id,
            title=title,
            body=body,
            status='unread',
            push_sent=False,
        )
 
        # 2. Fetch token from DB — never from request
        token = cls._get_token(user_type=user_type, driver_id=driver_id, passenger_id=passenger_id)
 
        if token is None:
            logger.warning(
                "No Expo token found for %s id=%s — notification id=%s saved but not pushed.",
                user_type,
                driver_id or passenger_id,
                notification.pk,
            )
            return notification
 
        # 3. Fire Expo push
        push_sent, push_error = cls._push(token=token, title=title, body=body)
 
        # 4. Write result back (outside the atomic block would lose it on outer rollback,
        #    but we want the notification record to survive even if the view rolls back,
        #    so we use update() on the already-flushed pk)
        Notification.objects.filter(pk=notification.pk).update(
            push_sent=push_sent,
            push_error=push_error,
        )
        notification.push_sent = push_sent
        notification.push_error = push_error
 
        return notification
 
    @staticmethod
    def _get_token(*, user_type: str, driver_id, passenger_id) -> str | None:
        """Return the raw token string or None."""
        try:
            if user_type == 'driver':
                obj = ExpoPushToken.objects.get(driver_id=driver_id, user_type='driver')
            else:
                obj = ExpoPushToken.objects.get(user_id=passenger_id, user_type='passenger')
            return obj.token
        except ExpoPushToken.DoesNotExist:
            return None
 
    @staticmethod
    def _push(*, token: str, title: str, body: str) -> tuple[bool, str | None]:
        """
        Send to Expo push API.
        Returns (push_sent: bool, push_error: str | None).
        Never raises — all failures are logged and returned as error strings.
        """
        payload = {
            "to": token,
            "title": title,
            "body": body,
            "sound": "default",
        }
        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=payload,
                timeout=EXPO_PUSH_TIMEOUT,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            data = response.json()
 
            # Expo wraps results in {"data": [{"status": "ok"|"error", ...}]}
            result = data.get("data", [{}])[0]
            if result.get("status") == "error":
                error_msg = result.get("message", "Unknown Expo error")
                logger.error("Expo push error for token %s: %s", token, error_msg)
                return False, error_msg
 
            return True, None
 
        except requests.Timeout:
            msg = "Expo push timed out."
            logger.error(msg)
            return False, msg
        except Exception as exc:
            msg = str(exc)
            logger.exception("Unexpected error sending Expo push: %s", msg)
            return False, msg