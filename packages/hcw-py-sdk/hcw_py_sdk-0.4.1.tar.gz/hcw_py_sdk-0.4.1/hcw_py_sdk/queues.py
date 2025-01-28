from .req import AuthRequests


class Queues:

    def __init__(self, req: AuthRequests):
        self.req = req
        self.url = f"{self.req.base_url}/queue"

    @property
    def list(self) -> list:
        return self.req.get(url=self.url)

    def create(self, queue_name):
        r = {
            "url": self.url,
            "json": {
                "name": queue_name
            }
        }
        return self.req.post(**r)

    def delete(self, queue_id):
        r = {
            "url": self.url,
            "json": {
                "id": queue_id
            }
        }
        return self.req.delete(**r)
