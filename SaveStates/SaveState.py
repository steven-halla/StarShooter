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
            "weapons": {},
            "missiles": {},
            "shield": {},
            "stats": {},
            "upgrades": {},
        }

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_path = os.path.join(self.base_dir, self.DEFAULT_FILENAME)

    # -------------------------------------------------
    # PLAYER (CORE / REQUIRED)
    # -------------------------------------------------
    def capture_player(self, starship) -> None:
        self.data["player"] = {
            "shipHealth": starship.shipHealth,
            "shipHealthMax": starship.shipHealthMax,
            "equipped_magic": list(starship.equipped_magic),
            "magic_inventory": list(starship.magic_inventory),
            "current_level": starship.current_level,  # ✅ ADDED
        }

        self.data["stats"] = {
            "speed": starship.speed,
            "player_ki": starship.player_ki,
            "player_max_ki": starship.player_max_ki,
            "current_heat": starship.current_heat,
            "max_heat": starship.max_heat,
        }

        self.data["weapons"] = {
            "machine_gun": {
                "damage": starship.machine_gun_damage,
                "width": starship.machine_gun_width,
                "height": starship.machine_gun_height,
                "rate_of_fire": starship.machine_gun_rate_of_fire,
                "bullet_speed": starship.machine_gun_bullet_speed,
                "bullets_per_shot": starship.machine_gun_bullets_per_shot,
            }
        }

        self.data["missiles"] = {
            "damage": starship.missile_damage,
            "bullet_speed": starship.missile_bullet_speed,
            "rate_of_fire": starship.missile_rate_of_fire,
            "max": starship.missile_max,
            "current": starship.missile_current,
            "fire_interval_seconds": starship.missile_fire_interval_seconds,
            "regen_interval_seconds": starship.missile_regen_interval_seconds,
        }

        if hasattr(starship, "shield_system"):
            self.data["shield"] = {
                "current": starship.shield_system.current_shield_points,
                "max": starship.shield_system.max_shield_points,
                "recharge_rate": starship.shield_system.recharge_rate_shield,
                "time_to_start_recharge": starship.shield_system.time_to_start_shield_recharge,
            }

        self.data["upgrades"] = {
            "upgrade_chips": list(starship.upgrade_chips)
        }

    # -------------------------------------------------
    # RESTORE PLAYER
    # -------------------------------------------------
    def restore_player(self, starship) -> None:
        p = self.data.get("player", {})
        if p:
            starship.shipHealth = p.get("shipHealth", starship.shipHealth)
            starship.shipHealthMax = p.get("shipHealthMax", starship.shipHealthMax)
            starship.equipped_magic = list(
                p.get("equipped_magic", starship.equipped_magic)
            )
            starship.magic_inventory = list(
                p.get("magic_inventory", starship.magic_inventory)
            )
            starship.current_level = p.get(  # ✅ RESTORED
                "current_level", starship.current_level
            )

        s = self.data.get("stats", {})
        if s:
            starship.speed = s.get("speed", starship.speed)
            starship.player_ki = s.get("player_ki", starship.player_ki)
            starship.player_max_ki = s.get("player_max_ki", starship.player_max_ki)
            starship.current_heat = s.get("current_heat", starship.current_heat)
            starship.max_heat = s.get("max_heat", starship.max_heat)

        w = self.data.get("weapons", {}).get("machine_gun", {})
        if w:
            starship.machine_gun_damage = w.get("damage", starship.machine_gun_damage)
            starship.machine_gun_width = w.get("width", starship.machine_gun_width)
            starship.machine_gun_height = w.get("height", starship.machine_gun_height)
            starship.machine_gun_rate_of_fire = w.get(
                "rate_of_fire", starship.machine_gun_rate_of_fire
            )
            starship.machine_gun_bullet_speed = w.get(
                "bullet_speed", starship.machine_gun_bullet_speed
            )
            starship.machine_gun_bullets_per_shot = w.get(
                "bullets_per_shot", starship.machine_gun_bullets_per_shot
            )

        m = self.data.get("missiles", {})
        if m:
            starship.missile_damage = m.get("damage", starship.missile_damage)
            starship.missile_bullet_speed = m.get(
                "bullet_speed", starship.missile_bullet_speed
            )
            starship.missile_rate_of_fire = m.get(
                "rate_of_fire", starship.missile_rate_of_fire
            )
            starship.missile_max = m.get("max", starship.missile_max)
            starship.missile_current = m.get("current", starship.missile_current)
            starship.missile_fire_interval_seconds = m.get(
                "fire_interval_seconds", starship.missile_fire_interval_seconds
            )
            starship.missile_regen_interval_seconds = m.get(
                "regen_interval_seconds", starship.missile_regen_interval_seconds
            )

        sh = self.data.get("shield", {})
        if sh and hasattr(starship, "shield_system"):
            starship.shield_system.current_shield_points = sh.get(
                "current", starship.shield_system.current_shield_points
            )
            starship.shield_system.max_shield_points = sh.get(
                "max", starship.shield_system.max_shield_points
            )
            starship.shield_system.recharge_rate_shield = sh.get(
                "recharge_rate", starship.shield_system.recharge_rate_shield
            )
            starship.shield_system.time_to_start_shield_recharge = sh.get(
                "time_to_start_recharge",
                starship.shield_system.time_to_start_shield_recharge,
            )

        u = self.data.get("upgrades", {})
        if u:
            starship.upgrade_chips = list(
                u.get("upgrade_chips", starship.upgrade_chips)
            )

        # reset transient combat state
        starship.invincible = False
        starship.last_health = starship.shipHealth

    # -------------------------------------------------
    # FILE IO
    # -------------------------------------------------
    def save_to_file(self, filename: str | None = None) -> None:
        if filename is None:
            filename = self.DEFAULT_FILENAME

        os.makedirs(self.base_dir, exist_ok=True)
        path = os.path.join(self.base_dir, filename)

        with open(path, "w") as f:
            json.dump(self.data, f, indent=2)

    def load_from_file(self, filename: str | None = None) -> bool:
        if filename is None:
            filename = self.DEFAULT_FILENAME

        path = os.path.join(self.base_dir, filename)

        if not os.path.exists(path):
            print(f"[SaveState] No save file found at {path}")
            return False

        with open(path, "r") as f:
            self.data = json.load(f)

        return True
