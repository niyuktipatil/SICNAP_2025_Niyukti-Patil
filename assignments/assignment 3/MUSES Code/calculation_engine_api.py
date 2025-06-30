import requests
import random
from requests.auth import HTTPBasicAuth
import os
import sys
import json
import logging
from time import sleep

from io import StringIO
import pandas as pd

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv('LOG_LEVEL', logging.WARNING))


class CalculationEngineApi():
    def __init__(self, conf={}):
        # Import credentials and config from environment variables
        self.conf = {
            'username': os.environ.get('CE_USERNAME', 'admin'),
            'password': os.environ.get('CE_PASSWORD', 'password'),
            'token': os.environ.get('CE_API_TOKEN', ''),
            'api_url_protocol': os.environ.get('CE_API_URL_PROTOCOL', 'http'),
            'api_url_authority': os.environ.get('CE_API_URL_AUTHORITY', 'localhost:4000'),
            'api_url_basepath': os.environ.get('CE_API_URL_BASEPATH', 'api/v0'),
            # Max number of requests per second
            'api_rate_limit': int(os.environ.get('API_RATE_LIMIT_USER', '2')),
        }
        for param in self.conf:
            if param in conf:
                self.conf[param] = conf[param]
        self.conf['url_base'] = f'''{self.conf['api_url_protocol']}://{self.conf['api_url_authority']}'''
        self.conf['api_url_base'] = f'''{self.conf['url_base']}/{self.conf['api_url_basepath']}'''
        if self.conf['token']:
            self.api_token = self.conf['token']
        else:
            self.api_token = self.get_api_token()
        self.auth_header = {
            'Authorization': f'''Token {self.api_token}''',
        }
        self.json_headers = self.auth_header
        self.json_headers['Content-Type'] = 'application/json'

    def get_api_token(self):
        url = f'''{self.conf['api_url_base']}/token/'''
        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/json',
            },
            json={
                'username': self.conf['username'],
                'password': self.conf['password'],
            }
        )
        data = self.display_response(response)
        return data['token']

    def display_response(self, response, parse_json=True):
        try:
            assert isinstance(response, requests.Response)
        except Exception as err:
            logger.error(f'''Invalid response object: {err}''')
            return response
        logger.debug(f'''Response code: {response.status_code}''')
        try:
            assert response.status_code in range(200, 300)
            if parse_json:
                data = response.json()
                logger.debug(json.dumps(data, indent=2))
                return data
            else:
                return response
        except Exception:
            try:
                logger.debug(f'''ERROR: {json.dumps(response.text, indent=2)}''')
            except Exception:
                logger.debug(f'''ERROR: {response.text}''')
            return response

    def login(self):
        response = requests.post(
            f'''{self.conf['url_base']}/admin/login/''',
            auth=HTTPBasicAuth(self.conf['username'], self.conf['password']),
        )
        data = self.display_response(response)
        return data

    def rate_limiter(self, response):
        rate_limit_status_code = 429
        if response.status_code == rate_limit_status_code:
            logger.debug(f'Response code {rate_limit_status_code} received. Rate limiter engaged.')
            sleep(1.0 / self.conf['api_rate_limit'])
        return response.status_code == rate_limit_status_code

    def job_create(self, name='', description="", config={}):
        if not name:
            name = f'''test-{random.randrange(10000, 99999)}'''
        while True:
            response = requests.post(
                f'''{self.conf['api_url_base']}/ce/job/''',
                json={
                    'name': name,
                    'config': config,
                    'description': description,
                },
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def job_delete(self, uuid=None):
        while True:
            response = requests.delete(
                f'''{self.conf['api_url_base']}/ce/job/{uuid}/''',
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response, parse_json=False)

    def job_delete_all(self):
        all_jobs = self.job_list()
        for job in all_jobs:
            logger.debug(job)
            while True:
                response = requests.delete(
                    f'''{self.conf['api_url_base']}/ce/job/{job['uuid']}/''',
                    headers=self.json_headers,
                )
                if not self.rate_limiter(response):
                    break
            self.display_response(response, parse_json=False)

    def job_list(self, uuid=''):
        jobs = []
        url = f'''{self.conf['api_url_base']}/ce/job/'''
        if uuid:
            url = f'''{url}{uuid}/'''
        while True:
            response = requests.get(
                url,
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        if response.status_code not in range(200, 300):
            return response
        response_data = response.json()
        # If a single job is being requested, return the data
        if uuid:
            return response_data
        # If all job info is being requested, append the result list and then fetch the next page of results
        jobs = response_data['results']
        url = response_data['next']
        # If the URL to the next page of results was included in the response, fetch it
        logger.debug(f'''Next page of results: "{url}"''')
        while url:
            while True:
                response = requests.get(
                    url,
                    headers=self.json_headers,
                )
                if not self.rate_limiter(response):
                    break
            response_data = response.json()
            jobs += response_data['results']
            url = response_data['next']
        return jobs

    def upload_list(self, uuid=''):
        uploads = []
        url = f'''{self.conf['api_url_base']}/ce/upload/'''
        if uuid:
            url = f'''{url}{uuid}/'''
        while True:
            response = requests.get(
                url,
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        if response.status_code not in range(200, 300):
            return response
        response_data = response.json()
        # If a single upload is being requested, return the data
        if uuid:
            return response_data
        # If all upload info is being requested, append the result list and then fetch the next page of results
        uploads = response_data['results']
        url = response_data['next']
        # If the URL to the next page of results was included in the response, fetch it
        logger.debug(f'''Next page of results: "{url}"''')
        while url:
            while True:
                response = requests.get(
                    url,
                    headers=self.json_headers,
                )
                if not self.rate_limiter(response):
                    break
            response_data = response.json()
            uploads += response_data['results']
            url = response_data['next']
        return uploads

    def upload_file(self, file_path='', upload_path='', description='', public=False):
        url = f'''{self.conf['api_url_base']}/ce/upload/'''
        while True:
            with open(file_path, 'rb') as fp:
                response = requests.put(
                    url,
                    headers={
                        'Authorization': f'''Token {self.api_token}''',
                    },
                    files={'file': fp},
                    data={
                        'path': upload_path,
                        'description': description,
                        'public': public,
                    },
                )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def upload_file_update(self, uuid, public=None, description=None, parse_json=True):
        url = f'''{self.conf['api_url_base']}/ce/upload/{uuid}/'''
        data = {}
        if public is not None:
            assert isinstance(public, bool)
            data['public'] = public
        if description is not None:
            assert isinstance(description, str)
            data['description'] = description
        while True:
            response = requests.patch(
                url,
                headers={
                    'Authorization': f'''Token {self.api_token}''',
                },
                data=data,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response, parse_json=parse_json)

    def download_job_file(self, uuid, path, root_dir='/tmp/ce/jobs'):
        url = f'''{self.conf['url_base']}/ce/download/{uuid}/{path.strip('/')}'''
        file_path = os.path.join(root_dir, uuid, path.strip('/'))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with requests.get(url, headers=self.json_headers, stream=True) as response:
            if self.rate_limiter(response):
                return self.download_job_file(uuid, path, root_dir)
            response.raise_for_status()
            with open(file_path, 'wb') as fp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        fp.write(chunk)

    def download_uploaded_file(self, uuid, root_dir='/tmp/ce/uploads'):
        url = f'''{self.conf['url_base']}/ce/download/{uuid}'''
        upload = self.upload_list(uuid=uuid)
        if 'path' not in upload:
            logger.error('Upload not found.')
            return
        path = upload['path'].strip('/')
        file_path = os.path.join(root_dir, uuid, path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with requests.get(url, headers=self.json_headers, stream=True) as response:
            if self.rate_limiter(response):
                return self.download_uploaded_file(uuid, root_dir)
            response.raise_for_status()
            with open(file_path, 'wb') as fp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        fp.write(chunk)

    def delete_uploaded_file(self, uuid, parse_json=False):
        url = f'''{self.conf['api_url_base']}/ce/upload/{uuid}/'''
        while True:
            response = requests.delete(
                url,
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response, parse_json=parse_json)

    def update_job(self, job_id, saved=None, public=None):
        url = f'''{self.conf['api_url_base']}/ce/job/{job_id}/'''
        data = {}
        if saved is not None:
            assert isinstance(saved, bool)
            data['saved'] = saved
        if public is not None:
            assert isinstance(public, bool)
            data['public'] = public
        while True:
            response = requests.patch(
                url,
                headers=self.json_headers,
                json=data,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def list_modules(self):
        url = f'''{self.conf['api_url_base']}/ce/module/'''
        while True:
            response = requests.get(
                url,
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def list_users(self):
        url = f'''{self.conf['api_url_base']}/user/'''
        while True:
            response = requests.get(
                url,
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def delete_user(self, username):
        url = f'''{self.conf['api_url_base']}/user/{username}/'''
        while True:
            response = requests.delete(
                url,
                headers=self.json_headers,
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def create_user(self, username, password, first_name='', last_name='', is_staff=True):
        url = f'''{self.conf['api_url_base']}/user/'''
        while True:
            response = requests.post(
                url,
                headers=self.json_headers,
                json={
                    'username': username,
                    'email': f'{username}@example.com',
                    'is_staff': is_staff,
                    'first_name': first_name if first_name else username,
                    'last_name': last_name if last_name else username,
                    'password': password,
                },
            )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)

    def get_metrics(self):
        metrics = []
        url = f'''{self.conf['api_url_base']}/ce/metrics/'''
        while url:
            while True:
                response = requests.get(
                    url,
                    headers=self.json_headers,
                )
                if not self.rate_limiter(response):
                    break
            metrics_data = response.json()
            metrics.extend(metrics_data['results'])
            url = metrics_data['next']
        return metrics


    def read_job_file_to_dataframe(self, uuid, path,**kwargs):
        url = f'''{self.conf['url_base']}/ce/download/{uuid}/{path.strip('/')}'''


        try: 
            response = requests.get(url, headers=self.json_headers)

            response.raise_for_status()

            # Convert the content of the response to a DataFrame
            file_content = StringIO(response.text)
            df = pd.read_csv(file_content, **kwargs)

            return df
        
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None
            
    def upload_dataframe(self, df, upload_path, description='', public=False):
        url = f"{self.conf['api_url_base']}/ce/upload/"
        while True:
            with StringIO() as fp:
                df.to_csv(fp, index=False)
                # Move file pointer back to start
                fp.seek(0)
                
                response = requests.put(
                    url,
                    headers={'Authorization': f"Token {self.api_token}"},
                    files={'file': fp},
                    data={
                        'path': upload_path,
                        'description': description,
                        'public': public,
                    },
                )
            if not self.rate_limiter(response):
                break
        return self.display_response(response)