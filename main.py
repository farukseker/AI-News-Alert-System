# from requests import api
# from ddgs import DDGS
# from hashlib import sha256
# from browser import sync_scraper
#
#
# print(sha256('Bursa Orhangazi ilçesi yapılacak kesintiler'.encode('utf-8')).hexdigest())
#
# r = sync_scraper('https://farukseker.com.tr')
# #
# print(r)
#
# results = DDGS().text("Bursa Orhangazi ilçesi yapılacak kesintiler", region='tr-tr', max_results=15)
# # print(results)
# print('#', '*' * 15)
# for result in results:
#     target = result.get('href')
#     if r := sync_scraper(target):
#         print('context on', target)
#     else:
#         print('context off', target)
#     print('*'*15)


from database import SessionLocal

session = SessionLocal()

from tasks.guncelkesintiler_task import GuncelkesintilerTask


task = GuncelkesintilerTask(session)
print('task start')
task.do()
print('task end')
print(task.has_error)