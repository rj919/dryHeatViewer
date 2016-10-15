__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

import requests
from time import time
from datetime import datetime

def get_info(ip_address=''):
    if not ip_address:
        ip_address = 'localhost'
    url = 'http://%s:5001/scheduler' % ip_address
    response = requests.get(url=url)
    return response.json()

def get_jobs(ip_address=''):
    if not ip_address:
        ip_address = 'localhost'
    url = 'http://%s:5001/scheduler/jobs' % ip_address
    response = requests.get(url=url)
    return response.json()

def add_job(job_kwargs, ip_address=''):
    '''
    :param job_kwargs: dictionary with key word arguments for job (from job_model)
    :param ip_address: [optional] string with ip address for docker container
    :return: [json-valid] dictionary with response details
    '''
    if not ip_address:
        ip_address = 'localhost'
    url = 'http://%s:5001/scheduler/jobs' % ip_address
    response = requests.post(url=url, json=job_kwargs)
    return response.json()

if __name__ == '__main__':
    from importlib.util import spec_from_file_location, module_from_spec
    spec_file = spec_from_file_location("credTelegram", "../cred/credentialsTelegram.py")
    credTelegram = module_from_spec(spec_file)
    spec_file.loader.exec_module(credTelegram)
    telegramCredentials = credTelegram.telegramCredentials
    ip_address = ''
    # ip_address = '192.168.99.100'
# test scheduler is running
    assert get_info(ip_address)['running']
# test job model settings
    import json
    current_time = time()
    job_date = datetime.utcfromtimestamp(current_time + 5).isoformat()
    job_kwargs = json.loads(open('models/job_model.json').read())['schema']
    job_kwargs['run_date'] = '%s+00:00' % job_date
    first_job = add_job(job_kwargs, ip_address)
# test request to third party
#     job_func = 'launch:requests.post'
#     telegram_url = 'https://api.telegram.org/bot%s/sendMessage' % telegramCredentials['access_token']
#     telegram_json = { 'chat_id': telegramCredentials['admin_id'], 'text': 'text me again' }
#     job_kwargs['kwargs'] = { 'url': telegram_url, 'json': telegram_json }
#     job_kwargs['func'] = job_func
#     job_kwargs['id'] = '%s_%s' % (job_func, str(current_time))
#     job_kwargs['coalesce'] = True
#     new_job = add_job(job_kwargs, ip_address)
#     job_list = get_jobs(ip_address)
#     assert job_list[1]['func'] == job_func
#     print(new_job)
