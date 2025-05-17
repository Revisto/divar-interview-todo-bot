import json
import os
import logging

logger = logging.getLogger(__name__)

TASKS_DB_FILE = "tasks.json"
STATES_DB_FILE = "conversation_states.json"


# Helper to load JSON data from a file
def _load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


# Helper to save JSON data to a file
def _save_json(filepath, data):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")


# --- Task Management ---


def get_tasks(conversation_id: str) -> list:
    """Retrieve all tasks for a given conversation_id."""
    all_tasks_data = _load_json(TASKS_DB_FILE)
    return all_tasks_data.get(conversation_id, [])


def save_tasks(conversation_id: str, tasks_list: list):
    """Save all tasks for a given conversation_id."""
    all_tasks_data = _load_json(TASKS_DB_FILE)
    all_tasks_data[conversation_id] = tasks_list
    _save_json(TASKS_DB_FILE, all_tasks_data)


def add_task_item(conversation_id: str, description: str):
    """Add a new task for a conversation."""
    tasks = get_tasks(conversation_id)
    tasks.append({"description": description, "done": False, "id": len(tasks) + 1})
    save_tasks(conversation_id, tasks)
    logger.info(f"Task added for {conversation_id}: {description}")


def delete_task_item(conversation_id: str, task_number: int) -> bool:
    """Delete a task by its 1-based index."""
    tasks = get_tasks(conversation_id)
    if 0 < task_number <= len(tasks):
        deleted_task = tasks.pop(task_number - 1)
        # Re-assign IDs if necessary or keep them sparse
        save_tasks(conversation_id, tasks)
        logger.info(
            f"Task {task_number} deleted for {conversation_id}: {deleted_task['description']}"
        )
        return True
    logger.warning(
        f"Invalid task number {task_number} for deletion for {conversation_id}"
    )
    return False


def mark_task_item_done(conversation_id: str, task_number: int) -> bool:
    """Mark a task as done by its 1-based index."""
    tasks = get_tasks(conversation_id)
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["done"] = True
        save_tasks(conversation_id, tasks)
        logger.info(
            f"Task {task_number} marked done for {conversation_id}: {tasks[task_number - 1]['description']}"
        )
        return True
    logger.warning(
        f"Invalid task number {task_number} for marking done for {conversation_id}"
    )
    return False


def get_tasks_string(conversation_id: str) -> str:
    """Get a formatted string of tasks for a conversation."""
    tasks = get_tasks(conversation_id)
    if not tasks:
        return "You have no tasks. Add one with /add <task description>."

    task_lines = []
    for i, task in enumerate(tasks):
        status = "[X]" if task.get("done") else "[ ]"
        task_lines.append(f"{i + 1}. {status} {task['description']}")
    return "\n".join(task_lines)


# --- Conversation State Management ---


def get_conversation_state(conversation_id: str) -> dict | None:
    """Retrieve the state for a given conversation_id."""
    states_data = _load_json(STATES_DB_FILE)
    return states_data.get(conversation_id)


def set_conversation_state(
    conversation_id: str, state_name: str | None, data: dict = None
):
    """Set the state for a given conversation_id. If state_name is None, clears the state."""
    states_data = _load_json(STATES_DB_FILE)
    if state_name is None:
        if conversation_id in states_data:
            del states_data[conversation_id]
            logger.info(f"State cleared for conversation {conversation_id}")
    else:
        states_data[conversation_id] = {"name": state_name, "data": data or {}}
        logger.info(
            f"State set for conversation {conversation_id}: {state_name} with data {data}"
        )
    _save_json(STATES_DB_FILE, states_data)


def clear_conversation_state(conversation_id: str):
    """Clear the state for a given conversation_id."""
    set_conversation_state(conversation_id, None)
