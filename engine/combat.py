from engine.dice import roll
import random

class Combat:

    def basic_attack(self, attacker, defender):
        d20 = roll(20)
        total = d20 + attacker.attack_bonus

        print(f"{attacker.name} rolls a {d20}!")

        if total >= 10:
            damage = roll(6)
            defender.hp -= damage
            defender.hp = max(0, defender.hp)
            return f"{attacker.name} hits for {damage} damage!"
        else:
            return f"{attacker.name} misses!"

    def use_ability(self, attacker, defender, ability_id, ability_data):
        print(f"\n✨ {ability_data['description']}")

        if ability_data["type"] == "damage":
            damage = roll(ability_data["damage_die"])
            defender.hp -= damage
            defender.hp = max(0, defender.hp)
            result = f"It deals {damage} damage!"

        elif ability_data["type"] == "heal":
            heal = roll(ability_data["heal_die"])
            attacker.hp = min(attacker.max_hp, attacker.hp + heal)
            result = f"You heal for {heal} HP!"

        # Start recharge AFTER ability is used
        if "recharge_roll" in ability_data:
            attacker.start_recharge(ability_id)

        return result

    def enemy_turn(self, monster, player, abilities_db):
        monster.attempt_recharge(abilities_db)

        if monster.abilities and random.random() < 0.4:
            ability_id = random.choice(monster.abilities)

            if monster.is_recharging(ability_id):
                print(self.basic_attack(monster, player))
                return

            ability_data = abilities_db[ability_id]
            print(self.use_ability(monster, player, ability_id, ability_data))
        else:
            print(self.basic_attack(monster, player))

    def battle(self, player, monster, abilities_db):
        print(f"\n⚔ A wild {monster.name} appears!\n")

        while player.is_alive() and monster.is_alive():

            # Attempt recharge at start of player turn
            player.attempt_recharge(abilities_db)

            print("\nChoose your action:")
            print("1. Basic Attack")

            for i, ability_id in enumerate(player.abilities, start=2):
                ability = abilities_db[ability_id]

                if player.is_recharging(ability_id):
                    print(f"{i}. {ability['name']} (Recharging...)")
                else:
                    print(f"{i}. {ability['name']}")

            # Input validation
            while True:
                try:
                    choice = int(input("> "))
                    if 1 <= choice <= 1 + len(player.abilities):
                        break
                    else:
                        print("Choose a valid option!")
                except ValueError:
                    print("Please enter a number!")

            if choice == 1:
                print(self.basic_attack(player, monster))
            else:
                ability_id = player.abilities[choice - 2]

                if player.is_recharging(ability_id):
                    print("⚡ That ability is still recharging!")
                    continue

                ability_data = abilities_db[ability_id]
                print(self.use_ability(player, monster, ability_id, ability_data))

            if monster.is_alive():
                self.enemy_turn(monster, player, abilities_db)

            print(f"\n{player.name}: {player.hp} HP")
            print(f"{monster.name}: {monster.hp} HP\n")

        if player.is_alive():
            print("🎉 You won the battle!")

            if hasattr(monster, "xp_reward"):
                player.gain_xp(monster.xp_reward)

            print(f"{player.name}: Level {player.level}, HP {player.hp}, XP {player.xp}/{player.next_level_xp}")
            return True
        else:
            print("💤 You fainted... but wake up safely at camp.")
            player.heal_full()
            return False