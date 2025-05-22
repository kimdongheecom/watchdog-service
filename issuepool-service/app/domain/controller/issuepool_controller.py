from gateway.app.domain import service


class IssuepoolController:
    def __init__(self):
        pass

    def get_issuepool(self, company_name: str):
        return service.get_issuepool(company_name)


