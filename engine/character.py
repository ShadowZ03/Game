from engine.dice import roll
from engine import media


class Character:
    def __init__(self, name, hp, attack_bonus=0, abilities=None):
        self.name         = name
        self.max_hp       = hp
        self.hp           = hp
        self.attack_bonus = attack_bonus
        self.abilities    = abilities or []
        self.recharging   = {}
        self.level        = 1
        self.xp           = 0
        self.next_level_xp = 10

    def is_alive(self):
        return self.hp > 0

    def heal_full(self):
        self.hp = self.max_hp

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.next_level_xp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= self.next_level_xp
        self.next_level_xp += 10
        self.max_hp += 5
        self.hp = self.max_hp
        self.attack_bonus += 1
        media.play_sound("level_up")

    def start_recharge(self, ability_id):
        self.recharging[ability_id] = True

    def is_recharging(self, ability_id):
        return self.recharging.get(ability_id, False)

    def attempt_recharge(self, abilities_db):
        """Try to recharge all cooling-down abilities; returns list of messages."""
        msgs = []
        for ability_id in list(self.recharging.keys()):
            if self.recharging[ability_id]:
                roll_result    = roll(6)
                ability_data   = abilities_db[ability_id]
                needed         = ability_data.get("recharge_roll")
                if roll_result >= needed:
                    self.recharging[ability_id] = False
                    msgs.append(f"✨ {ability_data['name']} is ready again!")
                else:
                    msgs.append(f"🔄 {ability_data['name']} recharging... (rolled {roll_result}, need {needed})")
        return msgs

    def rest(self):
        self.heal_full()
        self.recharging = {}
        media.play_sound("rest")