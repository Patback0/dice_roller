from flask import Flask, request, jsonify, render_template
from roller import DiceRoller
from save import on_open, on_save, reset
import re, signal, sys
from gui import start_tkinter_thread
import requests
import schedule
import time
from threading import Thread

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
        #self.app.add_url_rule('/test', 'test', self.process_motion_tasks)

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

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    def process_motion_tasks(self):
        # Step 1: send GET request to retrieve tasks with status "Completed" and label "dr"
        headers = {
            "X-API-Key": self.api_key,
        }
        params = {
            "status": ["Completed"],
            "label": self.remove_points_label,
        }

        response = requests.get(self.motion_api_url, headers=headers, params=params)
        if response.status_code == 200:
            tasks = response.json().get("tasks", [])
            print(len(tasks))
            # Step 2: Process up to 5 tasks
            upper_bound = min(5, len(tasks))
            for task in tasks[:upper_bound]:
                description = task.get("description", "")
                match = re.search(r'\{(-?\d+)\}', description)
                if match:
                    points = int(match.group(1))
                    print(points)
                    self.dr.add_del_success(points)

                    # Step 3: Send PATCH request to remove the "dr" label from the task
                    self.update_task(task)

        else:
            print(f"Failed to retrieve tasks: {response.status_code} - {response.text}")

    def update_task(self, task):
        task_id = task["id"]
        url = f"{self.motion_api_url}/{task_id}"
        
        updated_labels = [label for label in task.get("labels", []) if label["name"] != self.remove_points_label]
        
        data = {
            "name": task["name"],
            "dueDate": task.get("dueDate"),
            "assigneeId": task["assignees"][0]["id"] if task.get("assignees") else None,
            "duration": task.get("duration"),
            "status": task["status"]["name"],
            "description": task.get("description"),
            "priority": task["priority"],
            "labels": updated_labels,
        }

        headers = {
            "X-API-Key": self.api_key,
        }

        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Successfully updated task {task_id}")
        else:
            print(f"Failed to update task {task_id}: {response.status_code} - {response.text}")

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
    
    def start_scheduler(self):
        # POST request to Motion every 30 minutes
        schedule.every(2).minutes.do(self.process_motion_tasks)

        # schedule reset method at 2:00 AM every day
        schedule.every().day.at("02:00").do(self.daily_reset)

        scheduler_thread = Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()

    def run(self):
        start_tkinter_thread(self.dr)
        self.start_scheduler()
        self.app.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    file_path = './test_pts.txt'
    app = DiceRollerApp(file_path, DiceRoller())
    app.run()
