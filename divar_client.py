import requests
from config import Config
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DivarClient:
    def __init__(self):
        self.client_id = Config.DIVAR_APP_SLUG
        self.client_secret = Config.DIVAR_OAUTH_SECRET
        self.redirect_uri = Config.DIVAR_REDIRECT_URI
        self.api_key = Config.DIVAR_API_KEY
        self.base_url = "https://api.divar.ir"
        self.open_api_base_url = "https://open-api.divar.ir"
        self.scopes = [
            "USER_POSTS_ADDON_CREATE",
            "USER_ADDON_CREATE",
            "USER_POSTS_GET",
            "USER_PHONE",
            "offline_access",
            "CHAT_BOT_USER_MESSAGE_SEND",
            "CHAT_SUPPLIER_ALL_CONVERSATIONS_MESSAGE_SEND",
            "CHAT_SUPPLIER_ALL_CONVERSATIONS_READ",
            "NOTIFICATION_ACCESS_REVOCATION",
        ]

        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

    def get_oauth_redirect_url(self, state: str) -> str:
        endpoint = f"/oauth2/auth"
        url = f"{self.base_url}{endpoint}"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "+".join(self.scopes),
            "state": state,
        }
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{url}?{query_string}"

    def get_access_token(self) -> str:
        if (
            self.access_token
            and self.token_expires_at
            and datetime.now() < self.token_expires_at
        ):
            logger.info("Access token is valid and not expired.")
            return self.access_token

        if self.refresh_token:
            logger.info("Access token expired, attempting to refresh.")
            return self.refresh_access_token()

        raise Exception("No valid access token available. Please authenticate.")

    def refresh_access_token(self) -> str:
        endpoint = f"/oauth2/token"
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "code": self.access_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "redirect_uri": self.redirect_uri,
            "refresh_token": self.refresh_token,
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()

        token_data = response.json()
        print(token_data)  ## FIXME
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        if expires_in:
            self.token_expires_at = datetime.now() + timedelta(seconds=int(expires_in))

        logger.info("Successfully refreshed access token.")
        return self.access_token

    def exchange_code_for_token(self, code: str) -> dict:
        endpoint = f"/oauth2/token"
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()

        token_data = response.json()

        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        if expires_in:
            self.token_expires_at = datetime.now() + timedelta(seconds=int(expires_in))

        logger.info("Successfully obtained and stored access token.")
        return token_data

    def _get_authenticated_headers_v2(self) -> dict:
        if not self.access_token or not self.api_key:
            raise Exception("Access token or Api Key not available.")
        headers = dict()
        headers["x-api-key"] = self.api_key
        headers["x-access-token"] = self.get_access_token()
        return headers

    def _get_authenticated_headers_v1(self) -> dict:
        if not self.access_token or not self.api_key:
            raise Exception("Access token or Api Key not available.")
        headers = dict()
        headers["x-api-key"] = self.api_key
        headers["Authorization"] = f"Bearer {self.get_access_token()}"
        return headers

    def subscribe_to_event(
        self, event_type: str, event_resource_id: str = None, metadata: dict = None
    ) -> dict:
        endpoint = f"/v1/open-platform/events/subscriptions"
        url = f"{self.open_api_base_url}{endpoint}"

        payload = {"event_type": event_type}
        if event_resource_id:
            payload["event_resource_id"] = event_resource_id
        if metadata:
            payload["metadata"] = metadata

        # Prepare headers
        headers = self._get_authenticated_headers_v1()

        logger.info(
            f"Subscribing to event: {event_type}, resource: {event_resource_id or 'all'} at {url}"
        )

        response = requests.post(url, json=payload, headers=headers)
        print(response.content)
        response.raise_for_status()

        if response.status_code == 204 or not response.content:
            logger.info(
                f"Subscription to {event_type} successful with no content in response."
            )
            return None

        return response.json()

    def get_conversation_by_id(self, conversation_id: str) -> dict:
        endpoint = f"/v1/open-platform/chat/conversations/{conversation_id}"
        url = f"{self.base_url}{endpoint}"

        headers = self._get_authenticated_headers_v2()

        logger.info(f"Getting conversation by ID: {conversation_id} from {url}")

        response = requests.get(url, headers=headers)
        print(response.content)
        response.raise_for_status()

        if response.status_code == 204 or not response.content:
            logger.info(
                f"Successfully fetched conversation {conversation_id} with no content."
            )
            return None

        return response.json()

    def send_message_to_conversation(
        self,
        conversation_id: str,
        text_message: str,
        buttons: dict = None,
    ) -> dict:
        """
        Send a text message to a conversation using the experimental bot API.
        Requires CHAT_BOT_SEND_MESSAGE permission.
        """
        endpoint = f"/experimental/open-platform/chat/bot/conversations/{conversation_id}/messages"
        url = f"{self.open_api_base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

        payload = {
            "type": "TEXT",
            "text_message": text_message,
        }
        if buttons:
            payload["buttons"] = buttons

        logger.info(
            f"Sending bot message to conversation {conversation_id} at {url} with payload: {payload}"
        )

        response = requests.post(url, json=payload, headers=headers)
        print(response.content)
        response.raise_for_status()

        if response.status_code == 200 and response.content:
            return response.json()
        elif response.status_code == 200:
            logger.info(
                f"Message sent to {conversation_id} successfully with no JSON response body."
            )
            return {
                "status": "success",
                "message": "Message sent, no content returned.",
            }

        logger.warning(
            f"Message to {conversation_id} resulted in status {response.status_code} with no JSON content."
        )
        return {"status": response.status_code, "content": response.text}
