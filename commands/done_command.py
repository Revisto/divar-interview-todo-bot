from .base_command import AbstractCommand
import todo_db


class DoneCommand(AbstractCommand):
    COMMAND_NAME = "/done"
    STATE_AWAITING_TASK_NUMBER = "awaiting_task_to_mark_done"

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
                task_num = int(text)
                if todo_db.mark_task_item_done(conversation_id, task_num):
                    response_text = f"Task {task_num} marked as done."
                else:
                    response_text = f"Invalid task number: {task_num}. Task list:\n{todo_db.get_tasks_string(conversation_id)}"
                todo_db.clear_conversation_state(conversation_id)
                return response_text
            except ValueError:
                todo_db.clear_conversation_state(conversation_id)
                return "Invalid input. Please send a valid task number. Marking as done cancelled."

        # Initial /done command
        tasks_string = todo_db.get_tasks_string(conversation_id)
        if (
            "You have no tasks" in tasks_string
        ):  # Assuming this is the "no tasks" message from get_tasks_string
            return "No tasks to mark as done."
        else:
            todo_db.set_conversation_state(
                conversation_id, self.STATE_AWAITING_TASK_NUMBER
            )
            return f"Which task number to mark as done?\n{tasks_string}"

    def get_command_name(self) -> str | None:
        return self.COMMAND_NAME

    def get_handled_state(self) -> str | None:
        return self.STATE_AWAITING_TASK_NUMBER
