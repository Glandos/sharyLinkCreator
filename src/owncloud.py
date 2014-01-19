# encoding: utf-8

import lxml.objectify

from services import WebDAVService

class OwncloudService(WebDAVService):
    SHARE_TYPE_USER = 0
    SHARE_TYPE_GROUP = 1
    SHARE_TYPE_PUBLIC = 3
    def __init__(self, baseURL, username = '', password = ''):
        WebDAVService.__init__(self, baseURL, baseURL + '/remote.php/webdav', username, password)
        self.shareURL = baseURL + '/ocs/v1.php/apps/files_sharing/api/v1/shares'

    def share_path(self, path, share_type = SHARE_TYPE_PUBLIC):
        r = self.session.post(self.shareURL,
                              auth = (self.username, self.password),
                              data = {'path': path, 'shareType': share_type})
        if r.ok:
            shareDetails = lxml.objectify.fromstring(r.text)
            if shareDetails.meta.statuscode == 100:
                return str(shareDetails.data.url)
            else:
                print('Unable to share {}: {} ({})'.format(path, shareDetails.meta.status, shareDetails.meta.statuscode))
        else:
            print('Share request failed: {}'.format(r.status_code))
        return None
        
