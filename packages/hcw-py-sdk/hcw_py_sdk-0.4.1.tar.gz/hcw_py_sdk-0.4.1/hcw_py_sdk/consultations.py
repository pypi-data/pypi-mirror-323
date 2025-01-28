

from .req import AuthRequests
from .messages import Messages


class Consultations:

    def __init__(self, req: AuthRequests):
        self.req = req
        self.url = f"{self.req.base_url}/consultation"
        self.id = None
        self._message = None

    @property
    def list(self) -> list:

        return self.req.get(url=self.url)

    def create(self, invite_token):
        r = {
            "url": self.url,
            "json": {
                "invitationToken": invite_token
            }
        }
        result = self.req.post(**r)
        self.id = result.get("id")
        return result

    def delete(self, id=None):
        if id:
            r = {
                "url": f"{self.url}/{id}",
            }
        else:
            r = {
                "url": f"{self.url}/{self.id}",
            }
        return self.req.delete(**r)

    def accept(self, id=None):
        if id:
            r = {
                "url": f"{self.url}/{id}/accept",
            }
        else:
            r = {
                "url": f"{self.url}/{self.id}/accept",
            }
        return self.req.post(**r)

    def close(self, id=None):
        if id:
            r = {
                "url": f"{self.url}/{id}/close",
            }
        else:
            r = {
                "url": f"{self.url}/{self.id}/close",
            }
        return self.req.post(**r)

    @property
    def message(self) -> Messages:
        if not self._message:
            self._message = Messages(self.req, self.id)
        return self._message

    def upload(self, file, id=None):

        r = {
            "headers": {
                "filename": file,
                "locale": 'en'
            },
            "files": {
                'attachment': (file, open(file, 'rb'))
            }
        }

        if id:
            r['url'] = f"{self.url}/{id}/upload-file"
        else:
            r['url'] = f"{self.url}/{self.id}/upload-file"
        result = self.req.post(**r)
        return result
