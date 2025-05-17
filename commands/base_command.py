from abc import ABC, abstractmethod
from divar_client import DivarClient


class AbstractCommand(ABC):
    def __init__(self, divar_client: DivarClient):
        self.divar_client = divar_client
        # todo_db is used directly by commands for data persistence and state management.

    @abstractmethod
    def execute(
        self,
        conversation_id: str,
        text: str,
        original_text: str,
        current_state: dict | None,
    ) -> str:
        """
        Executes the command and returns the response text.
        The command is responsible for managing its own state transitions via todo_db.
        """
        pass

    @abstractmethod
    def get_command_name(self) -> str | None:
        """
        Returns the primary command string (e.g., "/add") that triggers this command.
        Returns None if this command is primarily triggered by a state or is a default handler.
        """
        pass

    @abstractmethod
    def get_handled_state(self) -> str | None:
        """
        Returns the conversation state name (e.g., "awaiting_task_description")
        that this command can process.
        Returns None if this command is not primarily triggered by a specific state.
        """
        pass
