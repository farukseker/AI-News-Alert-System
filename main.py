import time
import schedule

from database import get_db_session
from tasks import GuncelkesintilerTask, UedasTask, NewsSearchTask
from tasks.ai_notifier_task import AiNotifierTask


def task_manager():
    for task_cls in [
        GuncelkesintilerTask,
        UedasTask,
        NewsSearchTask,
    ]:
        with get_db_session() as session:
            task = task_cls(session)
            task.do()

            if task.has_error:
                time.sleep(10)
                task.do()

    with get_db_session() as session:
        AiNotifierTask(session).do()


schedule.every().day.at("09:00").do(task_manager)
schedule.every().day.at("21:00").do(task_manager)


def main():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
