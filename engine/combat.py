from engine.dice import roll
from engine import media
import random


class Combat:

    def basic_attack(self, attacker, defender):
        d20    = roll(20)
        total  = d20 + attacker.attack_bonus
        if total >= 10:
            damage = roll(6)
            defender.hp = max(0, defender.hp - damage)
            media.play_sound("basic_attack")
            return f"🗡  {attacker.name} rolls {d20} — hits for {damage} damage!"
        else:
            media.play_sound("miss")
            return f"💨  {attacker.name} rolls {d20} — misses!"

    def use_ability(self, attacker, defender, ability_id, ability_data):
        media.play_sound(ability_data.get("sound", ability_id))
        desc = ability_data["description"]

        if ability_data["type"] == "damage":
            damage = roll(ability_data["damage_die"])
            defender.hp = max(0, defender.hp - damage)
            result = f"✨ {desc}\n   It deals {damage} damage!"

        elif ability_data["type"] == "heal":
            heal = roll(ability_data["heal_die"])
            attacker.hp = min(attacker.max_hp, attacker.hp + heal)
            result = f"✨ {desc}\n   You heal for {heal} HP!"
        else:
            result = f"✨ {desc}"

        if "recharge_roll" in ability_data:
            attacker.start_recharge(ability_id)

        return result

    def enemy_turn(self, monster, player, abilities_db):
        monster.attempt_recharge(abilities_db)

        if monster.abilities and random.random() < 0.4:
            ability_id = random.choice(monster.abilities)
            if monster.is_recharging(ability_id):
                return self.basic_attack(monster, player)
            ability_data = abilities_db[ability_id]
            return self.use_ability(monster, player, ability_id, ability_data)
        else:
            return self.basic_attack(monster, player)

    def battle(self, player, monster, abilities_db):
        # Monster image becomes the battle backdrop
        if hasattr(monster, "image") and monster.image:
            media.set_scene(monster.image)

        media.show_message([f"⚔  A wild {monster.name} appears!"])

        while player.is_alive() and monster.is_alive():
            recharge_msgs = player.attempt_recharge(abilities_db)
            if recharge_msgs:
                media.show_message(recharge_msgs)

            # Build choice labels
            options    = ["⚔  Basic Attack"]
            recharging = [False]
            for ability_id in player.abilities:
                ab  = abilities_db[ability_id]
                rec = player.is_recharging(ability_id)
                options.append(ab["name"])
                recharging.append(rec)

            status = (f"{player.name}: {player.hp}/{player.max_hp} HP  •  "
                      f"{monster.name}: {monster.hp}/{monster.max_hp} HP")

            choice = media.prompt_choices(status, options, recharging=recharging)

            # Execute player action
            if choice == 0:
                result = self.basic_attack(player, monster)
            else:
                ability_id = player.abilities[choice - 1]
                if player.is_recharging(ability_id):
                    media.show_message(["⚡ That ability is still recharging!"])
                    continue
                result = self.use_ability(player, monster, ability_id, abilities_db[ability_id])

            lines = [result]

            # Enemy turn
            if monster.is_alive():
                enemy_result = self.enemy_turn(monster, player, abilities_db)
                lines += ["", f"👹 {monster.name}'s turn:", enemy_result]

            lines += [
                "",
                f"{player.name}: {player.hp}/{player.max_hp} HP",
                f"{monster.name}: {monster.hp}/{monster.max_hp} HP",
            ]
            media.show_message(lines)

        if player.is_alive():
            media.play_sound("victory")
            xp = getattr(monster, "xp_reward", 0)
            old_level = player.level
            player.gain_xp(xp)
            lines = [f"🎉 You defeated {monster.name}!",
                     f"   +{xp} XP"]
            if player.level > old_level:
                lines += ["", f"🎊 LEVEL UP!  Now Level {player.level}",
                          f"   +5 HP, +1 ATK"]
            lines += ["", f"{player.name}: Level {player.level}  "
                         f"HP {player.hp}  XP {player.xp}/{player.next_level_xp}"]
            media.show_message(lines)
            return True
        else:
            media.play_sound("game_over")
            player.heal_full()
            media.show_message(["💤 You fainted...",
                                 "   You wake up safely at camp."])
            return False