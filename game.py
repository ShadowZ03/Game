from engine.character import Character
from engine.combat import Combat
from engine.story import StoryEngine

from engine.character_loader import load_characters

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

    current_node = "start"

    while current_node:
        node = story.get_node(current_node)

        print("\n" + node["text"] + "\n")

        # Handle combat
        if "combat" in node:
            monster = Character("Goblin", hp=10, attack_bonus=1)
            combat.battle(player, monster)

            current_node = node.get("next")
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