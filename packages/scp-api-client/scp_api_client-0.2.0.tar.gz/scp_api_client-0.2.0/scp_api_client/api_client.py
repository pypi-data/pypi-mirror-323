import requests
import logging
import os
from datetime import datetime
import json


logger = logging.getLogger(__name__)


ENV_URLS = {
    'dev': 'http://localhost:8088',
    'prod': 'https://mytimber-api-prod-appservice.azurewebsites.net'
}


class ScpApiClient:
    def __init__(self, api_key: str):
        self.environment = os.getenv('ENVIRONMENT', 'dev')
        self.base_url = ENV_URLS[self.environment]
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        print(f"Using {self.environment} environment")
        
    def _headers(self):
        return {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    def get_waybill(self,waybill_number: str) -> dict:
        logger.info(f"Fetching waybill with number: {waybill_number}")
        url = f'{self.base_url}/waybill/number/{waybill_number}'
        try:
            response = requests.get(url, headers=self._headers(), timeout=20)
            response.raise_for_status()
            logger.debug(f"Successfully retrieved waybill {waybill_number}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch waybill {waybill_number}: {str(e)}")
            raise
        
    def list_waybills(self,start_time:datetime, end_time:datetime) -> dict:
        logger.info(f"Fetching waybills from {start_time} to {end_time}")
        url = (
            f'{self.base_url}/waybill/list'
            f'?pageIndex=0&pageSize=100000&filters=%5B%5D'
            f'&startDate={start_time.isoformat()}'
            f'&endDate={end_time.isoformat()}'
        )
        try:
            response = requests.get(url, headers=self._headers(), timeout=20)
            response.raise_for_status()
            data = response.json()['data']
            logger.info(f"Successfully retrieved {len(data)} waybills")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch waybills list: {str(e)}")
            raise
        
    def create_waybill(self, payload: dict):
        endpoint = f"{self.base_url}/waybill"
        response = requests.post(endpoint, data = json.dumps(payload), headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def list_all_sources(self):
        url = f'{self.base_url}/source/list'
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def list_all_destinations(self):
        url = f'{self.base_url}/destination/list'
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def upload_to_api(self, waybill):
        try:
            self.create_waybill(waybill.serialize())
        except Exception as e:
            self.logger.error("Failed to upload data to API: %s", str(e))
            raise