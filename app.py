from flask import Flask, request, jsonify, render_template
from roller import DiceRoller
from save import on_open, on_save, reset
from gui import start_tkinter_thread
from scheduled import start_scheduler
import re, signal, sys

class DiceRollerApp:
    def __init__(self, file_path, dice_roller):
        self.app = Flask(__name__)
        self.dr = dice_roller
        self.file_path = file_path
        self.api_key = "sXUJ+YZbSBL05h0Ufo1V69BkFQH4F806q0fnMAmNkJc="
        self.motion_api_url = "https://api.usemotion.com/v1/tasks"
        self.remove_points_label = "dr"

        # registering routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/todoist', 'todoist', self.todoist, methods=['POST'])

        # registering signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

        # initialize data
        on_open(self.dr, self.file_path)

    def daily_reset(self):
        # Reset the state at 2:00 AM every day
        print("Running daily reset...")
        reset(self.dr, self.file_path)
        print("Reset completed.")

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
        start_scheduler(self)
        self.app.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    file_path = './test_pts.txt'
    app = DiceRollerApp(file_path, DiceRoller())
    app.run()
