# engine/dice.py
import random

def roll(sides=20):
    return random.randint(1, sides)