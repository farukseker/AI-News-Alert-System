from database import SessionLocal, get_db_session
from config import get_settings

settings = get_settings()

session = SessionLocal()

from tasks.guncelkesintiler_task import GuncelkesintilerTask
from tasks.uedas_task import UedasTask


for task in [
    GuncelkesintilerTask,
    UedasTask
    # web arama sonuçlarının analizi
]:
    with get_db_session() as session:
        task = task(session)
        task.do()


# mail gönderen ai
