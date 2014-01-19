# encoding: utf-8

import os.path
import urllib.parse

from abc import ABCMeta, abstractmethod

import requests

from requests.exceptions import HTTPError
from utils import EmptyProgressMonitor

class Service(metaclass=ABCMeta):
    def __init__(self, baseURL, username = '', password = ''):
        self.baseURL = baseURL
        self.username = username
        self.password = password
        
    def upload_files(self, file_paths, destination, progress_monitor = EmptyProgressMonitor()):
        not_uploaded_files = []
        (progress_min, progress_max) = progress_monitor.get_progress_interval()
        progress_current = progress_min
        progress_step = (progress_max - progress_min) / file_paths.total_paths
        
        for (base, relative_paths) in file_paths.items():
            for relative_path in relative_paths:
                fullpath = os.path.join(base, relative_path)
                if os.path.isdir(fullpath):
                    progress_monitor.write_progress(progress_current, 'Creating directory {}'.format(relative_path))
                    
                    if not self.create_directory(relative_path, destination):
                        # Show some errors
                        print('Fail to create directory {}'.format(relative_path, destination))
                        not_uploaded_files.append(fullpath)
                else:
                    file_destination = os.path.join(destination, os.path.dirname(relative_path))
                    progress_monitor.write_progress(progress_current, 'Uploading {}'.format(relative_path))
                    progress_monitor.restrict_progress_interval(progress_current, progress_current + progress_step)
                    if not self.upload_file(fullpath, file_destination, progress_monitor):
                        # Show some errors
                        print('Fail to upload {} to {}'.format(relative_path, file_destination))
                        not_uploaded_files.append(fullpath)
                        
                    progress_monitor.restrict_progress_interval(progress_min, progress_max)
                        
                progress_current += progress_step
                
        # This method used to be recursive, but it's not the case right now
        # So we force progress to be at its maximum at the end
        progress_monitor.write_progress(progress_max)          
        return not_uploaded_files
    
    @abstractmethod
    def upload_file(self, file, destination, monitor = None):
        return False
    
    @abstractmethod
    def create_directory(self, name, base):
        return False
    
    @abstractmethod
    def is_directory(self, path):
        return False
    
    @abstractmethod
    def share_path(self, path, share_type):
        return False
    
class WebDAVService(Service):
    def __init__(self, baseURL, webdavURL, username = '', password = ''):
        Service.__init__(self, baseURL, username, password)
        self.webdavURL = webdavURL
        self.session = requests.Session()
        if not self.check_credentials():
            raise HTTPError('Invalid credentials')
        
    def check_credentials(self):
        r = self.session.get(self.webdavURL, auth = (self.username, self.password), verify = False)
        return r.ok
    
    def upload_file(self, file, destination, monitor = None):
        with open(file, 'rb') as f:
            if monitor:
                monitor.follow_file_read(f)
            filename = os.path.basename(file)
            r = self.session.put(self.webdavURL + urllib.parse.quote(destination + '/' + filename), data = f)
            return r.ok
        return False
    
    def create_directory(self, name, base):
        r = self.session.request('MKCOL', self.webdavURL + urllib.parse.quote(base + '/' + name))
        print('Directory creation', r)
        return r.ok
    
    def is_directory(self, path):
        # TODO really test this is a directory
        r = self.session.get(self.webdavURL + urllib.parse.quote(path))
        return r.ok