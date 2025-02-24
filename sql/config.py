import requests
import logging

class Model:
    def __init__(self):
        self.base_url = "https://spyads.asfycode.vn/api"
        self.headers = {
            'X-CSRF-Token': 'asfytecthungpvphattrien',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }

    def request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}/{endpoint}"  
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=self.headers,
                timeout=30  
            )
            response.raise_for_status()
            return response.json()  # Trả về JSON nếu hợp lệ
        except ValueError:
            return response.text  # Trả về text nếu JSON lỗi
        except requests.exceptions.HTTPError as err:
            
            try: 
                e = err.response.json()  # Trả về JSON nếu hợp lệ
            except ValueError:
                e = err.response.text  # Trả về text nếu JSON lỗi

            print(f"⛔ Request lỗi: {err}")
            return {"error": str(e)}  # Trả về lỗi thay vì chỉ in ra
        except requests.exceptions.RequestException as e:
            logging.error(f"⛔ Request lỗi: {e}")
            print(f"⛔ Request lỗi: {e}")
            return {"error": str(e)} 

    def get(self, endpoint, params=None):
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint, data=None):
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None):
        return self.request("DELETE", endpoint, params=params)
