from .req import AuthRequests


class Users:

    def __init__(self, req: AuthRequests):
        self.req = req
        self.url = f"{self.req.base_url}/user"

    @property
    def list(self) -> list:

        return self.req.get(url=self.url)

    def create(self, **user):
        r = {
            "url": self.url,
            "json": {
                "username": user.get('username'),
                "firstName": user.get('firstName'),
                "lastName": user.get('lastName'),
                "role": user.get('role'),
                "email": user.get('email'),
                "password": user.get('password'),
                "authPhoneNumber": user.get('authPhoneNumber'),
            }
        }
        return self.req.post(**r)

    def delete(self, id):
        r = {
            "url": f"{self.url}/{id}",
        }
        return self.req.delete(**r)
