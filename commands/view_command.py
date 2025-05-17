from .base_command import AbstractCommand
import todo_db


class ViewCommand(AbstractCommand):
    COMMAND_NAME = "/view"

    def execute(
        self,
        conversation_id: str,
        text: str,
        original_text: str,
        current_state: dict | None,
    ) -> str:
        return todo_db.get_tasks_string(conversation_id)

    def get_command_name(self) -> str | None:
        return self.COMMAND_NAME

    def get_handled_state(self) -> str | None:
        return None
