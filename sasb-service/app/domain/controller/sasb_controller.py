from app.domain.service.sasb_service import SasbService

class SasbController:
    def __init__(self):
        self.sasb_service = SasbService()

    def get_sasb(self,company_name:str):
        return self.sasb_service.get_sasb(company_name)
