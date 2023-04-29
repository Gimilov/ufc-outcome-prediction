import time

class Timer:
    def __init__(self):
        self.start_time = time.time()
        self.time_checkpoint = self.start_time
        
    def total_time_elapsed(self):
        return time.time() - self.start_time
    
    def checkpoint(self):
        result = time.time() - self.time_checkpoint
        self.time_checkpoint = time.time()
        
        return result
    
    def format_time(self, time: time.time()) -> str:
        formatted_time = '{:.0f}'.format(time)
        return formatted_time.ljust(7)
        
    