import asyncio
import random
import sys
from threading import Thread
import time
from evomeai_utils import LogTimer, EConfig
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test')

async def test(name=None):
    random.seed()
    if name is None:
        name = random.choice('XYZ')
    log.debug("name is %s", name)
    with LogTimer('stop1'+name):
        time.sleep(random.randint(1, 5) / 10)
    with LogTimer('stop2'+name):
        time.sleep(random.randint(5, 10) / 10)
    with LogTimer('stop3'+name):
        time.sleep(random.randint(1, 4) / 10)

    log.debug(LogTimer.output())


if __name__ == '__main__':
    with LogTimer('test'):
        print('hello, world')

    with LogTimer('before test1'):
        asyncio.run(test())
    with LogTimer('before thread'):
        Thread(target=test, args=('D',)).start()
    with LogTimer('before test2'):
        Thread(target=asyncio.run, args=(test("A"),)).start()
    with LogTimer('before test3'):
        Thread(target=asyncio.run, args=(test("B"),)).start()

    with LogTimer('main sleep'):
        time.sleep(random.randint(1, 5))
        with LogTimer('inner sleep'):
            time.sleep(random.randint(1, 5))

    log.debug(LogTimer.output())

    app_config = EConfig.getConfig()
    log.info(app_config.sections())

    my_config = EConfig.getConfig('my.ini')
    log.info(my_config.sections())

    db_config = EConfig.getConfig('folder/db.ini')
    log.info(db_config.get('conn', 'host'))
