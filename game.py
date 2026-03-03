from engine.character import Character
from engine.combat import Combat
from engine.story import StoryEngine
from engine.monster_loader import load_monsters
from engine.character_loader import load_characters
from engine.ability_loader import load_abilities

def choose_character():
    characters = load_characters("content/characters.yaml")

    print("Choose your hero:\n")

    char_list = list(characters.values())

    for i, char in enumerate(char_list, 1):
        print(f"{i}. {char.name} (HP: {char.max_hp}, ATK Bonus: {char.attack_bonus})")

    selection = int(input("> ")) - 1
    return char_list[selection]
def main():
    player = choose_character()
    story = StoryEngine("content/chapter1.yaml")
    combat = Combat()
    monsters = load_monsters("content/monsters.yaml")
    abilities = load_abilities("content/abilities.yaml")
    
    current_node = "start"

    while current_node:
        node = story.get_node(current_node)

        print("\n" + node["text"] + "\n")

        # Handle combat
        if "combat" in node:
            monster_id = node["combat"]

            if monster_id not in monsters:
                raise ValueError(f"Monster '{monster_id}' not found.")

            monster_template = monsters[monster_id]

            # Clone monster so stats reset each fight
            monster = Character(
            name=monster_template.name,
            hp=monster_template.max_hp,
            attack_bonus=monster_template.attack_bonus,
            abilities=list(monster_template.abilities)
            )
            
            monster.xp_reward = getattr(monster_template, "xp_reward", 5)
            
            combat.battle(player, monster, abilities)
            current_node = node.get("next")
            rest_choice = input("Rest at campfire? (y/n): ")

            if rest_choice.lower() == "y":
                player.rest()
            continue

        # Handle choices
        choices = node.get("choices", [])
        if not choices:
            break

        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice['text']}")

        selection = int(input("> ")) - 1
        current_node = choices[selection]["next"]

    print("\n🌟 Thanks for playing!")
if __name__ == "__main__":
    main()