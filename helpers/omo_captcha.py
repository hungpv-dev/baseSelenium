import requests
import base64
from helpers.base import config

def get_code_from_img(src):
    try:
        token = config('omocaptcha_token','')
        if token == '':
            raise ValueError('Không có token của Omo Captcha')
        base64Image = decodeBase64Img(src)
        if base64Image is None:
            raise ValueError('Không thể decode hình ảnh')
        print(f'Call api tạo job: {job_id}')
        job_id = createJob(token, base64Image)
        if job_id is None:
            raise ValueError('Không thể lấy job id')
        print(f'Lấy code: {code}')
        code = getResult(token, job_id)
        if code is None:
            raise ValueError('Không thể lấy code')
        return code
    except ValueError as e:
        print(e)
        return ''

def decodeBase64Img(url):
    res = requests.get(url)
    content = None
    if res.status_code == 200:
        content = base64.b64encode(res.content).decode('utf-8')
    return content

def createJob(token, base64Image):
        api = 'https://omocaptcha.com/api/createJob'
        data = {
            'api_token': token,
            'data': {
                'type_job_id': 30,
                'image_base64': base64Image
            }
        }
        res = requests.post(api, json=data)
        res = res.json()
        job_id = None
        if res.get("success"):
            job_id = res.get("job_id")
        return job_id
    
def getResult(token, job_id):
    code = ''
    while True:
        result = requests.post('https://omocaptcha.com/api/getJobResult', json={
            "api_token": token,
            "job_id": job_id
        })
        result = result.json()
        status = result.get('status')
        print(f'Lấy code status: {status}')
        if 'success' in status or 'fail' in status:
            if 'fail' in status:
                print(result)
            code = result.get('result')
            break
    return code