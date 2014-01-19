# encoding: utf-8

import html

from sh import zenity

from utils import ProgressMonitor

def ask_credentials(title, username = None):
    zenityCredentials = zenity.bake(title = 'Credentials for {}'.format(title), password = True)
    if not username:
        zenityCredentials = zenityCredentials.bake(username = True)
    result = zenityCredentials().strip()
    return (username, result) if username else (element for element in result.split('|'))
    
def show_error(message):
    zenity(error = True, text = message)
    
def show_shared_url(url, failed_upload = []):
    failed_files_message = 'Some files were not uploaded:\n- {}'.format('\n- '.join(failed_upload)) if failed_upload else ''
    
    zenity(title = 'Shared URL', info = True,
           text = 'Your files are <a href="{}">now shared</a>.\n{}'.format(html.escape(url), failed_files_message),
           _ok_code = [0, 1])

def show_progress_dialog(title, pulsate = False):
    progress = ProgressMonitor()
    zenity(progress = True, title = title, auto_close = True, pulsate = pulsate,
           _in = progress.get_queue(), _bg = True)
    # Give some time for window to appear
    return progress
    
