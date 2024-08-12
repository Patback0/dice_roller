import schedule
import time
from threading import Thread
from motion import process_motion_tasks

def run_scheduler():
  while True:
    schedule.run_pending()
    time.sleep(60)

def start_scheduler(app):
  schedule.every(2).minutes.do(process_motion_tasks, app)
  schedule.every().day.at("02:00").do(app.daily_reset)
  # schedule.every().day.at("23:43").do(app.daily_reset)

  scheduler_thread = Thread(target=run_scheduler)
  scheduler_thread.daemon = True
  scheduler_thread.start()