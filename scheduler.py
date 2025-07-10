# scheduler.py

from datetime import datetime
import time
import schedule
from app import check_reminders  # re-use the same check function

def run_scheduler():
    schedule.every(15).seconds.do(check_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()
