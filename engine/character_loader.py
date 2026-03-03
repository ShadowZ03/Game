from engine.character import Character
import yaml

def load_characters(file_path):
    with open(file_path) as f:
        data = yaml.safe_load(f)

    characters = {}

    for char in data:
        characters[char["id"]] = Character(
            name=char["name"],
            hp=char["hp"],
            attack_bonus=char["attack_bonus"],
            abilities=char.get("abilities", [])
        )

    return characters