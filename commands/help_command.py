from .base_command import AbstractCommand
from divar_client import DivarClient


class HelpCommand(AbstractCommand):
    COMMAND_NAME = "/help"

    def execute(
        self,
        conversation_id: str,
        text: str,
        original_text: str,
        current_state: dict | None,
    ) -> str:
        return (
            "Available commands:\n"
            "/add <task description> - Add a new task\n"
            "/add - Add a new task (interactive)\n"
            "/view - View all tasks\n"
            "/delete - Delete a task by number\n"
            "/done - Mark a task as done by number\n"
            "/help - Show this help message"
        )

    def get_command_name(self) -> str | None:
        return self.COMMAND_NAME

    def get_handled_state(self) -> str | None:
        return None
