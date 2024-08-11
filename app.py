from flask import Flask, request, jsonify, render_template
from roller import DiceRoller
import re, signal, sys, json
import threading
import tkinter as tk

app = Flask(__name__)
dr = DiceRoller()
file_path = './test_pts.txt'

# Tkinter GUI Setup
def start_tkinter():
    root = tk.Tk()
    root.title("Dice Roller")

    # Styling options
    root.geometry("1024x600")
    root.configure(bg='#0a0000')

    frame = tk.Frame(root, bg='#0a0000')
    frame.pack(expand=True)

    label_var1 = tk.Label(frame, text=f"Task Points: {dr.task_points}", font=('Arial', 36), fg='white', bg='black')
    label_var1.pack()

    label_var2 = tk.Label(frame, text=f"Dice Points: {dr.dice_points}", font=('Arial', 36),fg='white', bg='black')
    label_var2.pack()

    def update_display():
        label_var1.config(text=f"Task Points: {dr.task_points}")
        label_var2.config(text=f"Dice Points: {dr.dice_points}")
        root.after(1000, update_display) # update every second

    update_display()
    root.mainloop()

# Start the Tkinter GUI in a separate thread
def start_tkinter_thread():
    if threading.active_count() == 1:  # Ensure no other threads are running
        tkinter_thread = threading.Thread(target=start_tkinter)
        tkinter_thread.daemon = True
        tkinter_thread.start()

def on_open():
    global dr, file_path
    with open(file_path, 'r+') as f:
        lines = f.readlines()
        dr.task_points = int(lines[0].strip())
        dr.dice_points = int(lines[1].strip())
        # if len(lines) > 2:
        #     dr.past_rolls = json.loads(lines[2].strip())

def on_save(save_past_rolls=False):
    global dr, file_path
    with open(file_path, 'w') as f:
        f.seek(0)
        f.write(str(dr.task_points) + '\n')
        f.write(str(dr.dice_points) + '\n')
        # if save_past_rolls and dr.past_rolls:
        #     f.write(json.dumps(dr.past_rolls) + '\n')

def reset():
    global dr
    dr.past_rolls.clear()
    dr.dice_points = round(dr.dice_points * 1.01)
    on_save() # save to file

def handle_shutdown(signum, frame):
    print('Shutting down gracefully...')
    on_save(True) # save past rolls in the event of an unexpected shutdown
    sys.exit(0)

# Register signal handlers for termination signals
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
on_open() # read automatically

@app.route('/')
def index():
    global dr
    return render_template('index.html', dice_points=dr.dice_points, task_points=dr.task_points, past_rolls=dr.past_rolls)

@app.route('/todoist', methods=['POST'])
def todoist():
    global dr
    data = request.json
    event_data = data.get('event_data', {})
    content = event_data.get('content')

    # here is where we can diverge into many different functions.
    pattern = r'\{(-?\d+)\}'
    match = re.search(pattern, content)
    if not match: return jsonify({'message': 'Task received', 'task':'no update'}), 200
    match = match.group(1)
    if not dr.add_del_handle_successful(int(match)): # if it's a 0, we want to reset
        reset()
        return jsonify({'message': 'Task received', 'task':'no update'}), 200

    return jsonify({'message': 'Task received', 'dice points': dr.dice_points, 'task points': dr.task_points}), 200

if __name__ == '__main__':
    start_tkinter_thread()
    app.run(debug=False, host='0.0.0.0')

    
