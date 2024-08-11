from collections import Counter
import random

# DiceRoller class that manages rolls
class DiceRoller:
  def __init__(self):
    self.task_points = self.dice_points = 0
    self.past_rolls = Counter()

  def dice_roll(self):
    if self.task_points < 20: return
    
    roll_count = self.task_points // 20
    self.task_points %= 20
    results = []
    for _ in range(roll_count):
        curr_coin, num_coin = 1, 2
        while curr_coin == 1:
            results.append(random.randint(1, 20))
            curr_coin = random.randint(1, num_coin)
            num_coin *= 2

    # score computation
    score = 0
    for res in results:
        points = 0
        if res > 10: points = 2
        if res <= 10 and res > 4: points = 5
        if res <= 4 and res > 1: points = 10
        if res == 1: points = 20
        if res in self.past_rolls: score += points * (1 + (2 * self.past_rolls.get(res, 0)))
        else: score += points

        self.past_rolls.update([res])
    self.dice_points += score
    # prior dice rolls stay in context. ie. if I get a bunch of 1's in one day, they will grow

  # for now, positive number indicates task point addition.
  # if negative, assume a del against dice points.
  def add_del_success(self, value):
    if value == 0: return False
    if value > 0: self.task_points += value
    elif value < 0: self.dice_points += value
    self.dice_roll()
    return True