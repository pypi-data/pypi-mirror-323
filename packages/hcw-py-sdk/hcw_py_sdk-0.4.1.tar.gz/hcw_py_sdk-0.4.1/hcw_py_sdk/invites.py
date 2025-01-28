from .req import AuthRequests


class Invites:

    def __init__(self, req: AuthRequests):
        self.req = req
        self.id = None
        self.url = f"{self.req.base_url}/invite"

    @property
    def list(self) -> list:

        return self.req.get(url=self.url)

    def create(self, **info):
        r = {
            "url": self.url,
            # TODO: embedded the structure
            # "json": {
            #     "emailAddress": info.get("emailAddress"),
            #     "doctorLanguage": info.get("doctorLanguage"),
            #     "firstName": info.get("firstName"),
            #     "lastName": info.get("lastName"),
            #     "gender": info.get("gender"),
            #     "patientTZ": info.get("patientTZ"),
            #     "sendInvite": info.get("sendInvite"),
            #     "isPatientInvite": info.get("isPatientInvite"),
            # }
            "json": info
        }
        return self.req.post(**r)

    def close(self, id=None):
        if id:
            r = {
                "url": f"{self.url}/{id}/consultation/close",
            }
        else:
            r = {
                "url": f"{self.url}/{self.id}/consultation/close",
            }
        return self.req.post(**r)

    def get(self, id=None):
        if id:
            r = {
                "url": f"{self.url}/{id}",
            }
        else:
            r = {
                "url": f"{self.url}/{self.id}",
            }
        return self.req.get(**r)

    def delete(self, id):
        r = {
            "url": f"{self.url}/{id}",
        }
        return self.req.delete(**r)

    def consultation(self, id):
        '''Returns the consultation linked to invite'''
        if id:
            r = {
                "url": f"{self.url}/{id}/consultation",
            }
        else:
            r = {
                "url": f"{self.url}/{self.id}/consultation",
            }
        return self.req.get(**r)
