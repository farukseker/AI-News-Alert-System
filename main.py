import schedule
import sentry_sdk

import time

from config import get_settings
from database import get_db_session

from tasks import GuncelkesintilerTask, UedasTask, NewsSearchTask
from tasks.ai_notifier_task import AiNotifierTask

from logging_config import get_logger, configure_logging

from utils.db_init import init_db
from utils.selenium_health_check import selenium_health_check

configure_logging()

logger = get_logger(__name__)
settings = get_settings()


def run_task_once(task_cls):
    with get_db_session() as session:
        task = task_cls(session)
        try:
            task.do()
            return not task.has_error
        except Exception:
            logger.exception(f"{task_cls.__name__} failed")
            return False


def task_manager():
    for task_cls in [
        GuncelkesintilerTask,
        UedasTask,
        NewsSearchTask,
    ]:
        if run_task_once(task_cls):
            logger.info(f"Task {task_cls.__name__} succeeded")
        else:
            logger.info(f"Task {task_cls.__name__} failed")

        # if not ok:
        #     time.sleep()
        #     run_task_once(task_cls)

    with get_db_session() as session:
        AiNotifierTask(session).do()




def main():
    logger.info('__main__ started')
    # import json
    # logger.info(
    #     json.dumps(
    #         settings.model_dump(exclude={"OPENROUTER_API_KEY", "SMTP_PASSWORD", "BASE_DIR"}),
    #         indent=2
    #     )
    # )
    # logger.info(f'env dump end {"="*25}')

    logger.info(f'selenium test {"="*25}')
    selenium_health_check_status = selenium_health_check(settings.SELENIUM_REMOTE_SERVER_ADDR)
    logger.info(f'env dump test end result: {"OK" if selenium_health_check_status else "BAD"} {"="*25}')

    logger.info('init_db - start')
    init_db()
    logger.info('init_db - end')

    logger.info('tasks start scheduling')
    schedule.every().day.at("06:00").do(task_manager)
    schedule.every().day.at("18:00").do(task_manager)
    logger.info('tasks has scheduled')

    logger.info('task scheduler started.')
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("Application crashed", exc_info=True)
        raise
