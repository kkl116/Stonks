import cryptocompare
import csv 
from flask_app import scheduler 
from ..config import Config

@scheduler.task("cron",
id="fetch_coins", 
day='1st mon')
def fetch_coin_list():
    path = Config.COINS_LIST_PATH
    coins_list = cryptocompare.get_coin_list(format=True)
    coins_list = [[c] for c in coins_list]
    with open(path, 'w') as f:
        write = csv.writer(f)
        write.writerow(['coins'])
        write.writerows(coins_list)

