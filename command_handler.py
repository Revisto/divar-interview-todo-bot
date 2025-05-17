import logging
import todo_db
from divar_client import DivarClient

# Import command classes
from commands.add_command import AddCommand
from commands.delete_command import DeleteCommand
from commands.done_command import DoneCommand
from commands.help_command import HelpCommand
from commands.view_command import ViewCommand
from commands.base_command import AbstractCommand


logger = logging.getLogger(__name__)


class CommandHandler:
    def __init__(self, divar_client: DivarClient):
        self.divar_client = divar_client
        self.commands_by_name: dict[str, AbstractCommand] = {}
        self.commands_by_state: dict[str, AbstractCommand] = {}

        # Instantiate and register commands
        add_cmd = AddCommand(divar_client)
        delete_cmd = DeleteCommand(divar_client)
        done_cmd = DoneCommand(divar_client)
        help_cmd = HelpCommand(divar_client)
        view_cmd = ViewCommand(divar_client)
        self.default_cmd = HelpCommand(divar_client)  # Default

        all_commands = [add_cmd, delete_cmd, done_cmd, help_cmd, view_cmd]

        for cmd in all_commands:
            cmd_name = cmd.get_command_name()
            if cmd_name:
                if cmd_name in self.commands_by_name:
                    logger.warning(f"Duplicate command name registration: {cmd_name}")
                self.commands_by_name[cmd_name] = cmd

            handled_state = cmd.get_handled_state()
            if handled_state:
                if handled_state in self.commands_by_state:
                    logger.warning(
                        f"Duplicate state handler registration: {handled_state}"
                    )
                self.commands_by_state[handled_state] = cmd

        # Ensure help command is registered if it has a name
        if (
            help_cmd.get_command_name()
            and help_cmd.get_command_name() not in self.commands_by_name
        ):
            self.commands_by_name[help_cmd.get_command_name()] = help_cmd

    def handle_message(self, conversation_id: str, text: str, original_text: str):
        current_state = todo_db.get_conversation_state(conversation_id)

        # Check for commands like "/add description" first, then "/add"
        parts = text.split(" ", 1)
        command_text_key = parts[0]  # e.g. "/add"

        # Refined selection logic:
        # 1. If a state is active and a command handles that state, use it.
        # 2. Else, if the input text matches a command name, use that command.
        # 3. Else, use default_cmd. (Note: current code uses HelpCommand)

        command_to_execute = self.default_cmd  # Default

        if current_state and current_state.get("name") in self.commands_by_state:
            command_to_execute = self.commands_by_state[current_state.get("name")]
        elif command_text_key in self.commands_by_name:
            command_to_execute = self.commands_by_name[command_text_key]

        # Special case: if user types /help, it should always work, overriding current state processing
        # unless the state itself is part of a help flow (not the case here).
        if (
            command_text_key == HelpCommand.COMMAND_NAME
        ):  # Accessing COMMAND_NAME directly
            command_to_execute = self.commands_by_name[HelpCommand.COMMAND_NAME]

        response_text = command_to_execute.execute(
            conversation_id, text, original_text, current_state
        )

        if response_text:
            try:
                self.divar_client.send_message_to_conversation(
                    conversation_id, response_text
                )
                logger.info(f"Sent response to {conversation_id}: {response_text}")
            except Exception as e:
                logger.error(
                    f"Failed to send message to Divar for conversation {conversation_id}: {e}"
                )
