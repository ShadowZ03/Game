from engine.dice import roll
import engine.ability_loader

class Character:
    def __init__(self, name, hp, attack_bonus=0, abilities=None):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_bonus = attack_bonus
        self.abilities = abilities or []
        self.recharging = {}
        
        # Leveling
        self.level = 1
        self.xp = 0
        self.next_level_xp = 10  # XP needed for next level

    def is_alive(self):
        return self.hp > 0

    def heal_full(self):
        self.hp = self.max_hp

    def gain_xp(self, amount):
        print(f"✨ {self.name} gains {amount} XP!")
        self.xp += amount

        while self.xp >= self.next_level_xp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= self.next_level_xp
        self.next_level_xp += 10  # Increase threshold each level

        # Level-up rewards
        hp_increase = 5
        atk_increase = 1
        self.max_hp += hp_increase
        self.hp = self.max_hp
        self.attack_bonus += atk_increase

        print(f"🎉 {self.name} leveled up to Level {self.level}!")
        print(f"   +{hp_increase} HP, +{atk_increase} ATK\n")
        
    def start_recharge(self, ability_id):
      self.recharging[ability_id] = True

    def is_recharging(self, ability_id):
        return self.recharging.get(ability_id, False)

    def attempt_recharge(self, abilities_db):
      for ability_id in list(self.recharging.keys()):
          if self.recharging[ability_id]:

              roll_result = roll(6)
              ability_data = abilities_db[ability_id]
              needed = ability_data.get("recharge_roll")

              print(f"🔄 Trying to recharge {ability_data['name']}... rolled {roll_result}")

              if roll_result >= needed:
                  print(f"✨ {ability_data['name']} is ready again!")
                  self.recharging[ability_id] = False
                    
    def rest(self):
      print("🏕 You rest at the campfire...")
      self.heal_full()
      self.recharging = {}
      print("✨ All abilities restored!")