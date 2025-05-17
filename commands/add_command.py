from .base_command import AbstractCommand
import todo_db


class AddCommand(AbstractCommand):
    COMMAND_NAME = "/add"
    STATE_AWAITING_DESCRIPTION = "awaiting_task_description"

    def execute(
        self,
        conversation_id: str,
        text: str,
        original_text: str,
        current_state: dict | None,
    ) -> str:
        if (
            current_state
            and current_state.get("name") == self.STATE_AWAITING_DESCRIPTION
        ):
            if not original_text:  # User sent an empty message for task description
                todo_db.clear_conversation_state(conversation_id)
                return "Task addition cancelled as no description was provided. Type /add again to start over."
            todo_db.add_task_item(conversation_id, original_text)
            todo_db.clear_conversation_state(conversation_id)
            return f'Task added: "{original_text}"'

        if text.startswith(f"{self.COMMAND_NAME} "):
            task_description = original_text[len(self.COMMAND_NAME) + 1 :].strip()
            if task_description:
                todo_db.add_task_item(conversation_id, task_description)
                return f'Task added: "{task_description}"'
            else:  # Command was like "/add " with nothing after
                todo_db.set_conversation_state(
                    conversation_id, self.STATE_AWAITING_DESCRIPTION
                )
                return "Okay, what is the task?"
        elif text == self.COMMAND_NAME:  # Just "/add"
            todo_db.set_conversation_state(
                conversation_id, self.STATE_AWAITING_DESCRIPTION
            )
            return "Okay, what is the task?"

        # Fallback, should ideally not be reached if CommandHandler routes correctly
        return "Error: AddCommand was called inappropriately."

    def get_command_name(self) -> str | None:
        return self.COMMAND_NAME

    def get_handled_state(self) -> str | None:
        return self.STATE_AWAITING_DESCRIPTION
