import time
import schedule

from config import get_settings
from database import get_db_session
from tasks import GuncelkesintilerTask, UedasTask, NewsSearchTask
from tasks.ai_notifier_task import AiNotifierTask
from logging_config import get_logger

from selenium_health_check import selenium_health_check


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
        ok = run_task_once(task_cls)

        if not ok:
            time.sleep(10)
            run_task_once(task_cls)

    with get_db_session() as session:
        AiNotifierTask(session).do()


schedule.every().day.at("09:00").do(task_manager)
schedule.every().day.at("21:00").do(task_manager)


def main():
    logger.info('__main__ started')
    logger.info('enb dump')

    import json
    logger.info(
        json.dumps(
            settings.model_dump(exclude={"OPENROUTER_API_KEY", "SMTP_PASSWORD", "BASE_DIR"}),
            indent=2
        )
    )
    logger.info(f'env dump end {"="*25}')

    logger.info(f'selenium test {"="*25}')
    selenium_health_check_status = selenium_health_check(settings.SELENIUM_REMOTE_SERVER_ADDR)
    logger.info(f'env dump test end result{selenium_health_check_status} {"="*25}')

    logger.info('init_db - start')
    from utils.db_init import init_db
    init_db()
    logger.info('init_db - end')

    logger.info('test task start task_manager')
    task_manager()
    logger.info('test task  end  task_manager')

    logger.info('__main__ task mid schedule loop started')

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":

    main()
