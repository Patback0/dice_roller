from flask import Flask, request, jsonify, render_template
from roller import DiceRoller
from save import on_open, on_save, reset
import re, signal, sys
from gui import start_tkinter_thread

class DiceRollerApp:
    def __init__(self, file_path, dice_roller):
        self.app = Flask(__name__)
        self.dr = dice_roller
        self.file_path = file_path

        # registering routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/todoist', 'todoist', self.todoist, methods=['POST'])

        # registering signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

        # initialize data
        on_open(self.dr, self.file_path)

    def handle_shutdown(self, signum, frame):
        print('Shutting down gracefully...')
        on_save(self.dr, self.file_path, True)  # save past rolls in the event of an unexpected shutdown
        sys.exit(0)

    def index(self):
        return render_template('index.html', dice_points=self.dr.dice_points, task_points=self.dr.task_points, past_rolls=self.dr.past_rolls)

    def todoist(self):
        content = request.json.get('event_data', {}).get('content', '')
        match = re.search(r'\{(-?\d+)\}', content)
        
        if match and self.dr.add_del_success(int(match.group(1))):
            response = {'dice points': self.dr.dice_points, 'task points': self.dr.task_points}
        else:
            reset(self.dr, self.file_path)
            response = {'task': 'no update'}

        return jsonify({'message': 'Task received', **response}), 200

    def run(self):
        start_tkinter_thread(self.dr)
        self.app.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    file_path = './test_pts.txt'
    app = DiceRollerApp(file_path, DiceRoller())
    app.run()
