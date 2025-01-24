import json
import logging
import time
import sys
import threading

log = logging.getLogger('LogTimer')

class LogTimer:
    timers_map = {}
    main_thread_id = threading.main_thread().ident

    def __init__(self, name):
        #获取当前函数调用堆栈深度
        track = sys._getframe(1)
        layer = 0
        while track.f_globals.get('__name__') != '__main__':
            log.debug(f"track.f_globals.get('__name__'): {track.f_globals.get('__name__')}")
            track = track.f_back
            if track is None:
                break
            layer += 1

        self.name = '  ' * layer + name
        self.start_time = time.time()
        self.elapsed_time = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time = time.time() - self.start_time
        thread_id = threading.get_ident()
        if thread_id not in LogTimer.timers_map:
            if thread_id != LogTimer.main_thread_id and LogTimer.main_thread_id in LogTimer.timers_map:
                LogTimer.timers_map[thread_id] = LogTimer.timers_map[LogTimer.main_thread_id].copy()
            else:
                LogTimer.timers_map[thread_id] = []
        LogTimer.timers_map[thread_id].append(self)
        log.debug(f"{self.name} time: {self.elapsed_time*1000:.3f} ms")

    @staticmethod
    def output():
        res = {}
        thread_id = threading.get_ident()
        if thread_id in LogTimer.timers_map:
            for timer in LogTimer.timers_map[thread_id]:
                res[timer.name] = timer.elapsed_time.__round__(3)
            # log.info("Total Time Cost: " + json.dumps(res, indent=2))
            LogTimer.timers_map[thread_id] = []
        return res