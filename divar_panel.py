from flask import (
    Flask,
    request,
    jsonify,
)
from divar_client import DivarClient
import logging
from command_handler import CommandHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.secret_key = "a_very_secret_key_for_flask_flashing"

# Global DivarClient instance for the web app
divar_client = DivarClient()

# Global CommandHandler instance
command_handler = CommandHandler(divar_client)


@app.route("/", methods=["POST"])
def chat_callback():
    webhook_data = request.json
    logger.info(
        f"Received Divar webhook: headers={request.headers}, body={webhook_data}"
    )

    if webhook_data.get("type") == "NEW_CHATBOT_MESSAGE":
        message_data = webhook_data.get("new_chatbot_message", {})
        conversation_id = message_data.get("conversation", {}).get("id")
        sender_type = message_data.get("sender", {}).get("type")
        text = message_data.get("text", "").strip().lower()
        original_text = message_data.get(
            "text", ""
        ).strip()  # Keep original for descriptions

        if not conversation_id or sender_type != "HUMAN":
            logger.warning(
                "Ignoring non-human message or message without conversation ID."
            )
            return jsonify({"status": "ignored"}), 200

        # Delegate message handling to CommandHandler
        command_handler.handle_message(conversation_id, text, original_text)

        return jsonify({"status": "processed"}), 200

    return jsonify({"status": "unsupported_type"}), 400


if __name__ == "__main__":
    app.run(port=8000, debug=True)
