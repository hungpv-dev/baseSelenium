from .chrome import create_chrome
from selenium.webdriver.common.action_chains import ActionChains
import json
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
class Driver:
    def __init__(self, profile=None, undetected = True):
        self.driver = create_chrome(profile=profile,undetected=undetected)
        self.type_find_element = {
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'css': By.CSS_SELECTOR
        }
    
    def __getattr__(self, name):
        return getattr(self.driver, name)
    
    def action_chains(self):
        return ActionChains(self.driver)
    
    def get(self, url:str, e_wait:int = 0):
        self.driver.get(url)
        if e_wait > 0:
            sleep(e_wait)

    def closeModal(self, index, last = False, type = '//*[@aria-label="Close"]'):
        try:
            modals = self.find_all(type)
            if len(modals) > index:
                if last:
                    modals[-1].click()
                else:
                    modals[index].click()
        except Exception as e:
            print(f'Lỗi click modal: {index} - {e}')

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

    def find(self,query:str, type_query = 'xpath', send_keys = None, wait=0):
        result = None
        try:   
            result = WebDriverWait(self.driver, wait).until(
                EC.presence_of_element_located((self.type_find_element.get(type_query), query))
            )
            if send_keys is not None:
                result.send_keys(send_keys)
        except NoSuchElementException as e:
            print(f'No search: {query}')
        except TimeoutException as e:
            print(f'No search: {query}')
        return result 

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

    def quit(self):
        self.driver.quit()