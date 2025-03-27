from .chrome import create_chrome
from selenium.webdriver.common.action_chains import ActionChains
import json
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
requests.packages.urllib3.util.connection.HAS_IPV6 = False
from sql.config import Model
class Driver:
    def __init__(self, profile=None):
        self.driver = create_chrome(profile=profile)
        self.type_find_element = {
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'css': By.CSS_SELECTOR
        }
        self.model = Model()
    
    def __getattr__(self, name):
        return getattr(self.driver, name)
    
    def action_chains(self):
        return ActionChains(self.driver)
    
    def get(self, url:str, e_wait:int = 0):
        self.driver.get(url)
        if e_wait > 0:
            sleep(e_wait)

    def wait_and_click(self, xpath, timeout=5, scope = None):
        actions = self.action_chains()
        """Hàm đợi phần tử xuất hiện rồi click"""
        if scope is None:
            scope = self.driver
        try:
            element = WebDriverWait(scope, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            actions.move_to_element(element).perform()
            sleep(0.5)
            element.click()
            return True
        except Exception as e:
            print(f"Error when click for {xpath}: {e}")
            return False

    def closeModal(self, index = 0, last = False, type = '//*[@aria-label="Close"]'):
        try:
            modals = self.find_all(type)
            if len(modals) > index:
                if last:
                    modals[-1].click()
                else:
                    modals[index].click()
        except Exception as e:
            print(f'Error click modal for: {index}')

    def randomSleep(self, min_time: int = 5, max_time: int = 10):
        sleep_time = random.uniform(min_time, max_time)
        sleep(sleep_time)


    def setCookies(self, cookies):
        if not cookies:
            print('Cookie không hợp lệ')
            return

        print("Type before json.loads:", type(cookies))
        if isinstance(cookies, str):
            cookies = json.loads(cookies)
        
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                print(f'Lỗi set cookie: {e}')

    def find(self,query:str, type_query = 'xpath', send_keys = None, wait=0, clear=False):
        result = None
        try:   
            result = WebDriverWait(self.driver, wait).until(
                EC.presence_of_element_located((self.type_find_element.get(type_query), query))
            )
            if clear:
                result.send_keys(Keys.CONTROL + "a")  # Chọn toàn bộ văn bản
                result.send_keys(Keys.DELETE)  # Xóa nội dung
            if send_keys is not None:
                self.send_keys_humman(result, send_keys)
        except NoSuchElementException as e:
            print(f'No search: {query}')
        except TimeoutException as e:
            print(f'No search: {query}')
        return result 
    
    def enter(self, search):
        search.send_keys(Keys.ENTER)  # Gõ Enter

    def find_all(self, query: str, type_query='xpath', last = False, wait=0):
        results = []
        try:
            results = WebDriverWait(self.driver, wait).until(
                EC.presence_of_all_elements_located((self.type_find_element.get(type_query), query))
            )
        except NoSuchElementException as e:
            print(f'No search: {query}')
        except TimeoutException as e:
            print(f'No search: {query}')

        if last and results:
            return results[-1] if results else None
        
        return results

    def random_delay(self, min_time=30, max_time=60):
        """Tạo độ trễ ngẫu nhiên"""
        sleep(random.uniform(min_time, max_time))


    def clickText(self, text, wait=0):
        try:
            xpath = f"//*[contains(text(), '{text}')]"
            ele = self.find(xpath,wait=wait)
            if ele is not None:
                ele.click()
        except Exception as e:
            print(f'Không click đc element: {e}')

    def clickOk(self):
        try:
            ok_button = self.find('//*[@aria-label="OK"]')
            ok_button.click()
        except Exception as e:
            pass

    def new_tab(self, domain:str = None):
        original_window = self.driver.current_window_handle
        windows_before = self.driver.window_handles
        self.driver.execute_script("window.open('about:blank', '_blank');")
        windows_after = self.driver.window_handles
        new_window = [window for window in windows_after if window not in windows_before][0]
        self.driver.switch_to.window(new_window)
        if domain is not None:
            self.get(domain, e_wait=5)

    def switch_tab(self, index: int, close=False):
        handles = self.driver.window_handles
        if index < len(handles):
            if close:
                current_handle = self.driver.current_window_handle
                self.driver.close()
                handles = self.driver.window_handles  # Cập nhật lại danh sách các cửa sổ sau khi đóng
                if index >= len(handles):
                    index = len(handles) - 1  # Đảm bảo chỉ số không vượt quá số lượng cửa sổ hiện tại
            self.driver.switch_to.window(handles[index])
        else:
            print(f'Index {index} out of range. There are only {len(handles)} tabs open.')

    
    def send_keys_humman(self, element, text, delay_range=(0.1, 0.3)):
        """Nhập văn bản vào một phần tử với hiệu ứng nhập bằng tay"""
        for char in text:
            element.send_keys(char)
            sleep(random.uniform(*delay_range))


    def send_image_error(self, content, api="upload-image-error"):
        try:
            self.model.headers.pop("Content-Type", None)  # Xóa Content-Type để requests tự đặt

            # Chụp ảnh màn hình và lưu thành file
            img_path = 'error.png'
            self.driver.save_screenshot(img_path)

            # Mở file ảnh và gửi lên API
            with open(img_path, 'rb') as img_file:
                files = {'image': ('error.png', img_file, 'image/png')}
                data = {'content': content}

                response = requests.post(
                    url=f"{self.model.base_url}/{api}",
                    headers=self.model.headers,
                    files=files,
                    data=data
                )
            # Kiểm tra phản hồi từ API
            if response.status_code == 200:
                print("Anh da duoc gui thanh cong.")
        except Exception as e:
            print(f"Loi xong qua trinh gui anh: {e}")
    
    def quit(self):
        self.driver.quit()