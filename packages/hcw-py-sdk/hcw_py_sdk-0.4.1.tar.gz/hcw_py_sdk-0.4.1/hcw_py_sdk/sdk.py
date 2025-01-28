import requests
from .users import Users
from .queues import Queues
from .invites import Invites
from .phone import Phone
from .fhir import Fhir
from .consultations import Consultations
from .req import AuthRequests


class HCW:

    def __init__(self, base_url, username=None, password=None, auth_token=None) -> None:
        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth_token = auth_token
        self._token = None
        self._req = None
        self._consultation = None

    def _login(self) -> None:
        if self.username and self.password:
            params = {
                "url": f"{self.base_url}/login-local",
                "json": {
                    "email": self.username,
                    "password": self.password
                }
            }
        elif self.auth_token:
            params = {
                "url": f"{self.base_url}/login-invite",
                "json": {
                    "inviteToken": self.auth_token
                }
            }

        req = requests.post(**params)
        if req.status_code == 200:
            if req.json().get("user"):
                self._token = req.json().get("user").get("token")
        else:
            raise Exception(f"Unable to get token: {req.text}")

    @property
    def req(self):
        if not self._req:
            self._req = AuthRequests(self.token, self.base_url)
        return self._req

    @property
    def token(self):
        if not self._token:
            self._login()
        return self._token

    @property
    def user(self) -> Users:
        return Users(self.req)

    @property
    def queue(self) -> Queues:
        return Queues(self.req)

    @property
    def invite(self) -> Invites:
        return Invites(self.req)

    @property
    def phone(self) -> Phone:
        return Phone(self.req)

    @property
    def consultation(self) -> Consultations:
        if not self._consultation:
            self._consultation = Consultations(self.req)
        return self._consultation

    @property
    def fhir(self):
        return Fhir(self.req)
