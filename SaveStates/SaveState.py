import json
import os
from typing import Any


class SaveState:
    VERSION = 1
    DEFAULT_FILENAME = "player_save.json"

    def __init__(self):
        self.data: dict[str, Any] = {
            "version": self.VERSION,
            "player": {},
        }
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_path = os.path.join(self.base_dir, self.DEFAULT_FILENAME)

    # -------------------------------------------------
    # PLAYER
    # -------------------------------------------------
    def capture_player(self, starship, level_name: str) -> None:
        self.data["player"] = {
            "shipHealth": starship.shipHealth,
            "shipHealthMax": starship.shipHealthMax,
            "equipped_magic": list(starship.equipped_magic),
            "level": level_name,
        }

    def restore_player(self, starship) -> None:
        p = self.data.get("player", {})
        if not p:
            return

        starship.shipHealth = p["shipHealth"]
        starship.shipHealthMax = p["shipHealthMax"]
        starship.equipped_magic = list(p["equipped_magic"])

        # reset transient combat state
        starship.invincible = False
        starship.last_health = starship.shipHealth
    # -------------------------------------------------
    # FILE IO
    # -------------------------------------------------
    def save_to_file(self, filename: str) -> None:
        print("SAVE PATH:")
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # ensure SaveStates directory exists
        os.makedirs(base_dir, exist_ok=True)

        path = os.path.join(base_dir, filename)

        with open(path, "w") as f:
            json.dump(self.data, f, indent=2)

    def load_from_file(self, filename: str) -> bool:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, filename)

        if not os.path.exists(path):
            print(f"[SaveState] No save file found at {path}")
            return False

        with open(path, "r") as f:
            self.data = json.load(f)

        return True
