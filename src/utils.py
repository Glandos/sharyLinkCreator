# encoding: utf-8

import functools
import os
import os.path

from queue import Queue

class UploadPaths(dict):
    @property
    def total_paths(self):
        return sum([len(paths) for paths in self.values()])
    
    def full_paths(self):
        return [os.path.join(base, path)
                for (base, paths) in self.items()
                for path in paths]
    
    @property
    def total_size(self):
        # One-liner party!
        return sum([os.path.getsize(os.path.join(base, path))
                    for (base, paths) in self.items()
                    for path in paths if os.path.isfile(os.path.join(base, path))])

class ProgressMonitor():
    def __init__(self, mini = 0, maxi = 100):
        self._queue = Queue()
        self._min = mini
        self._max = maxi
        
    def get_queue(self):
        return self._queue
    
    def write_progress(self, percentage, message = None):
        self._queue.put('{}\n'.format(percentage))
        print('Message is {} at {}%'.format(message, percentage))
        if message:
            self._queue.put('# {}\n'.format(message))
            
    def restrict_progress_interval(self, mini = 0, maxi = 100):
        self._min = mini
        self._max = maxi
    
    def get_progress_interval(self):
        return (self._min, self._max)
    
    def close(self):
        self.write_progress(self._max)
        
    def read_and_report(self, file, filesize, n):
        real_read = file.__read(n)
        if not real_read:
            # Unregister
            file.read = file.__read
        self.write_progress((self._max - self._min) * (file.tell() / filesize) + self._min)
        return real_read
        
    def follow_file_read(self, file):
        file.__read = file.read
        size = os.fstat(file.fileno()).st_size
        file.read = functools.partial(self.read_and_report, file, size)
        
    
class EmptyProgressMonitor(ProgressMonitor):
    
    def __init__(self):
        ProgressMonitor.__init__(self, 0, 0)
        
    def restrict_progress_interval(self, mini = 0, maxi = 0):
        ProgressMonitor.restrict_progress_interval(self, 0, 0)
    
    def write_progress(self, percentage, message = None):
        pass