from engine.dice import roll

class Combat:
    def attack(self, attacker, defender):
        d20 = roll(20)
        total = d20 + attacker.attack_bonus

        if total >= 10:
            damage = roll(6)
            defender.hp -= damage
            return f"{attacker.name} hits {defender.name} for {damage} damage!"
        else:
            return f"{attacker.name} misses!"

    def battle(self, player, monster):
        print(f"\n⚔ A wild {monster.name} appears!\n")

        while player.is_alive() and monster.is_alive():
            input("Press Enter to attack...")
            print(self.attack(player, monster))

            if monster.is_alive():
                print(self.attack(monster, player))

            print(f"\n{player.name}: {player.hp} HP")
            print(f"{monster.name}: {monster.hp} HP\n")

        if player.is_alive():
            print("🎉 You won the battle!")
            return True
        else:
            print("💤 You fainted... but wake up safely at camp.")
            player.heal_full()
            return False