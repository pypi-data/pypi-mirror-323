

from .req import AuthRequests


class Messages:

    def __init__(self, req: AuthRequests, consultation_id):
        self.req = req
        self.url = f"{self.req.base_url}/message"
        self.consultation_id = consultation_id

    @property
    def list(self) -> list:

        return self.req.get(url=self.url)

    def create(self, text, type="text"):
        r = {
            "url": self.url,
            "json": {
                "consultation": self.consultation_id,
                "text":	text,
                "type": type
            }
        }
        result = self.req.post(**r)
        self.consultation_id = result.get("id")
        return result
