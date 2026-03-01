# engine/character.py
class Character:
    def __init__(self, name, hp, attack_bonus=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_bonus = attack_bonus

    def is_alive(self):
        return self.hp > 0
      
    def heal_full(self):
      self.hp = self.max_hp    