from flask import Flask, request, jsonify
from collections import Counter
import re
from roller import DiceRoller

app = Flask(__name__)
dr = DiceRoller()
file_path = './test_pts.txt'

def on_open():
    global dr, file_path
    with open(file_path, 'r+') as f:
        dr.task_points = int(f.readline().strip())
        dr.dice_points = int(f.readline().strip())

def on_save():
    global dr, file_path
    with open(file_path, 'w') as f:
        f.seek(0)
        f.write(str(dr.task_points) + '\n')
        f.write(str(dr.dice_points) + '\n')

def reset():
    global dr
    dr.past_rolls.clear()
    dr.dice_points = round(dr.dice_points * 1.01)
    on_save() # save to file

on_open() # read automatically

@app.route('/')
def index():
    global dr
    return f'Dice Points: {dr.dice_points} \n Task Points: {dr.task_points} \n Rolls: {dr.past_rolls}'

@app.route('/todoist', methods=['POST'])
def todoist():
    global dr
    data = request.json
    event_data = data.get('event_data', {})
    content = event_data.get('content')

    # here is where we can diverge into many different functions.
    pattern = r'\{(-?\d+)\}'
    match = re.search(pattern, content).group(1)
    if not match: return jsonify({'message': 'Task received', 'task':'no update'}), 200

    if not dr.add_del_handle_successful(int(match)): # if it's a 0, we want to reset
        reset()
        return jsonify({'message': 'Task received', 'task':'no update'}), 200

    return jsonify({'message': 'Task received', 'dice points': dr.dice_points, 'task points': dr.task_points}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

    
