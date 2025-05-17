from .base_command import AbstractCommand
import todo_db


class DeleteCommand(AbstractCommand):
    COMMAND_NAME = "/delete"
    STATE_AWAITING_TASK_NUMBER = "awaiting_task_to_delete"

    def execute(
        self,
        conversation_id: str,
        text: str,
        original_text: str,
        current_state: dict | None,
    ) -> str:
        if (
            current_state
            and current_state.get("name") == self.STATE_AWAITING_TASK_NUMBER
        ):
            try:
                task_num = int(
                    text
                )  # Use the already lowercased 'text' for number parsing
                if todo_db.delete_task_item(conversation_id, task_num):
                    response_text = f"Task {task_num} deleted."
                else:
                    response_text = f"Invalid task number: {task_num}. Task list:\n{todo_db.get_tasks_string(conversation_id)}"
                todo_db.clear_conversation_state(conversation_id)
                return response_text
            except ValueError:
                todo_db.clear_conversation_state(
                    conversation_id
                )  # Clear state on bad input
                return "Invalid input. Please send a valid task number. Deletion cancelled."

        # Initial /delete command
        tasks_string = todo_db.get_tasks_string(conversation_id)
        if "You have no tasks" in tasks_string:
            return "No tasks to delete."
        else:
            todo_db.set_conversation_state(
                conversation_id, self.STATE_AWAITING_TASK_NUMBER
            )
            return f"Which task number to delete?\n{tasks_string}"

    def get_command_name(self) -> str | None:
        return self.COMMAND_NAME

    def get_handled_state(self) -> str | None:
        return self.STATE_AWAITING_TASK_NUMBER
