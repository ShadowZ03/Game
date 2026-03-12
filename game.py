from engine.character import Character
from engine.combat import Combat
from engine.story import StoryEngine
from engine.monster_loader import load_monsters
from engine.character_loader import load_characters
from engine.ability_loader import load_abilities
from engine import media


def calc_max_buttons(characters, story, abilities):
    """
    Walk all screens to find the largest number of buttons ever shown at once.
      Character select = one button per character
      Combat screen    = 1 (Basic Attack) + player's ability count
      Story screen     = number of choices in the node
    """
    max_char_select = len(characters)

    max_combat = max(
        1 + len(c.abilities) for c in characters.values()
    )

    max_story = max(
        (len(node.get("choices", [])) for node in story.nodes.values()),
        default=0,
    )

    # 2 = minimum for Yes/No prompts
    return max(max_char_select, max_combat, max_story, 2)


def choose_character(characters):
    char_list = list(characters.values())
    labels = [
        f"{c.name}  (HP: {c.max_hp}  ATK: +{c.attack_bonus})"
        for c in char_list
    ]
    idx = media.prompt_choices("Choose your hero:", labels)
    return char_list[idx]


def main():
    # Load content
    characters = load_characters("content/characters.yaml")
    story      = StoryEngine("content/chapter1.yaml")
    monsters   = load_monsters("content/monsters.yaml")
    abilities  = load_abilities("content/abilities.yaml")

    # Size and open the window before anything is displayed
    max_btns = calc_max_buttons(characters, story, abilities)
    media.init_window(max_btns)

    media.set_scene("title_screen")
    player  = choose_character(characters)
    combat  = Combat()
    current_node = "start"

    while current_node:
        node = story.get_node(current_node)

        if node.get("image"):
            media.set_scene(node["image"])
        if node.get("sound"):
            media.play_sound(node["sound"])

        media.show_message([node["text"]])

        # ── combat ──────────────────────────────────────────────────────────
        if "combat" in node:
            monster_id = node["combat"]
            if monster_id not in monsters:
                raise ValueError(f"Monster '{monster_id}' not found.")

            tmpl = monsters[monster_id]
            monster = Character(
                name=tmpl.name,
                hp=tmpl.max_hp,
                attack_bonus=tmpl.attack_bonus,
                abilities=list(tmpl.abilities),
            )
            monster.xp_reward = getattr(tmpl, "xp_reward", 5)
            monster.image     = getattr(tmpl, "image", None)

            combat.battle(player, monster, abilities)
            current_node = node.get("next")

            if media.prompt_yn("Rest at the campfire?"):
                player.rest()
                media.show_message(["You rest at the campfire.",
                                    "All abilities restored!"])
            continue

        # ── story choices ────────────────────────────────────────────────────
        choices = node.get("choices", [])
        if not choices:
            break

        idx = media.prompt_choices("What do you do?", [c["text"] for c in choices])
        current_node = choices[idx]["next"]

    media.show_message(["Thanks for playing!"], wait_label="Quit")
    media.quit_media()


if __name__ == "__main__":
    main()