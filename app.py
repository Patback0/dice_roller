from flask import Flask, request, jsonify
from collections import Counter
import random, sys, re

app = Flask(__name__)

task_points = dice_points = 0
past_rolls = Counter()

file_path = './test_pts.txt'

def on_open():
    global task_points, dice_points, file_path
    with open(file_path, 'r+') as f:
        task_points = int(f.readline().strip())
        dice_points = int(f.readline().strip())

def on_save():
    global task_points, dice_points, file_path
    with open(file_path, 'w') as f:
        f.seek(0)
        f.write(str(task_points) + '\n')
        f.write(str(dice_points) + '\n')
        

def dice_roll():
    global task_points, dice_points, past_rolls
    roll_count = task_points // 20
    task_points = task_points % 20
    results = []
    for i in range(roll_count):
        curr_coin, num_coin = 1, 2
        while curr_coin == 1:
            outcome = random.randint(1, 20)
            results.append(outcome)
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
        if res in past_rolls: score += points * (1 + (2 * past_rolls.get(res, 0)))
        else: score += points

        past_rolls.update([res])
    dice_points += score
    # prior dice rolls stay in context. ie. if I get a bunch of 1's in one day, they will grow

def reset():
    global dice_points, past_rolls
    past_rolls.clear()
    dice_points = round(dice_points * 1.01)
    #  save results
    on_save()

on_open() # read automatically

@app.route('/')
def index():
    global task_points, dice_points, past_rolls
    rolls = past_rolls
    return f'Dice Points: {dice_points} \n Task Points: {task_points} \n Rolls: {rolls}'

@app.route('/todoist', methods=['POST'])
def todoist():
    global task_points, dice_points, past_rolls
    data = request.json
    event_data = data.get('event_data', {})
    content = event_data.get('content')

    # here is where we can diverge into many different functions.
    pattern = r'\{(-?\d+)\}'
    match = re.search(pattern, content).group(1)

    # for now, positive number indicates task point addition.
    # if negative, assume a del against dice points.
    if match: value = int(match)
    else: return jsonify({'message': 'Task received', 'task':'no update'}), 200

    if value > 0: task_points += value
    elif value == 0: # reset message
        reset()
        return jsonify({'message': 'Task received', 'dice points': dice_points, 'task points': task_points}), 200
    else: dice_points += value # assuming a del

    if task_points >= 20: dice_roll()

    return jsonify({'message': 'Task received', 'dice points': dice_points, 'task points': task_points}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

    
