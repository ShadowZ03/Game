import yaml
from engine.character import Character

def load_monsters(file_path):
    with open(file_path) as f:
        data = yaml.safe_load(f)

    monsters = {}

    for m in data:
      monsters[m["id"]] = Character(
          name=m["name"],
          hp=m["hp"],
          attack_bonus=m["attack_bonus"],
          abilities=m.get("abilities", [])
      )
      monsters[m["id"]].xp_reward = m.get("xp_reward", 5)
              

    return monsters