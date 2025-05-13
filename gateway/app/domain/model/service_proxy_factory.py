from typing import Optional
from fastapi import HTTPException
import httpx
from app.domain.model.service_type import SERVICE_URLS, ServiceType


class ServiceProxyFactory:
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.base_url = SERVICE_URLS[service_type]
        print(f"👩🏻 Service URL: {self.base_url}")

    async def request(
        self,
        method: str,
        path: str,
        headers: Optional[list[tuple[bytes, bytes]]] = None,
        body: Optional[bytes] = None
    ) -> httpx.Response:
        url = f"{self.base_url}/{self.service_type.value}/{path}"
        print(f"🎯🎯🎯 Requesting URL: {url}")
        
        # ✅ 헤더 설정 (필요 시 외부 헤더 병합 가능)
        headers_dict = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers_dict,
                    content=body
                )
                print(f"Response status: {response.status_code}")
                print(f"Request URL: {url}")
                print(f"Request body: {body}")
                return response
            except Exception as e:
                print(f"Request failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))