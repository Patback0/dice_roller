import re
import requests

def process_motion_tasks(app):
    """Process tasks from the Motion API."""
    headers = {
        "X-API-Key": app.api_key,
    }
    params = {
        "status": ["Completed"],
        "label": app.remove_points_label,
    }

    response = requests.get(app.motion_api_url, headers=headers, params=params)
    if response.status_code == 200:
        tasks = response.json().get("tasks", [])
        print(f"Found {len(tasks)} tasks.")
        # Process up to 5 tasks
        upper_bound = min(5, len(tasks))
        for task in tasks[:upper_bound]:
            description = task.get("description", "")
            match = re.search(r'\{(-?\d+)\}', description)
            if match:
                points = int(match.group(1))
                print(f"Found {points} points.")
                app.dr.add_del_success(points)

                # Send PATCH request to remove the label
                update_task(app, task)
    else:
        print(f"Failed to retrieve tasks: {response.status_code} - {response.text}")


def update_task(app, task):
    task_id = task["id"]
    url = f"{app.motion_api_url}/{task_id}"
    
    updated_labels = [label for label in task.get("labels", []) if label["name"] != app.remove_points_label]
    
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
        "X-API-Key": app.api_key,
    }

    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Successfully updated task {task_id}")
    else:
        print(f"Failed to update task {task_id}: {response.status_code} - {response.text}")