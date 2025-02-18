from sql import accounts, posts
from managers import Driver
from .login import check_login, login_with_user_pass
from time import sleep
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
from helpers import clean_url_keep_params
import json
import pyperclip
import re

def extract_post_id(url):
    match = re.search(r'/p/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else ''

def create_browse_link_spy_fb(account_id, stop_event):
    print(f'Lấy thông tin account: {account_id}')
    account = accounts.find(account_id)
    print(f"Account: {account.get('name')}")
    print('Khởi tạo trình duyệt')
    driver = Driver()
    print('Login với cookie')
    driver.get('https://facebook.com', e_wait=2)
    status_login = check_login(driver)
    if status_login is False:
        driver.setCookies(account.get('cookies'))
        driver.get('https://facebook.com', e_wait=3)
        accept_all_cookies = driver.find_all('//*[@aria-label="Allow all cookies"]', last=True)
        if accept_all_cookies:
            accept_all_cookies.click()
        print('Kiểm tra trạng thái login')
        status_login = check_login(driver)
        if status_login is False:
            print('Login không thành công, bắt đầu login...')
            login_with_user_pass(driver, account)
            status_login = check_login(driver)
            print(f'Login: {status_login}')
            if status_login:
                cookies = driver.get_cookies()
                print(cookies)
                accounts.update(account_id,{
                    'cookies': cookies,
                })

    print('Login thành công')
    # pageLinkPost = f"/posts/"
    # pageLinkStory = "https://www.facebook.com/permalink.php"
    listId = set()
    while not stop_event.is_set():
        print('Room nhỏ màn hình')
        driver.execute_script("document.body.style.zoom='0.2';")
        actions = driver.action_chains()
        sleep(3)
        listPosts = driver.find_all('//*[@aria-posinset]') 
        print(f'Số bài viết lấy được: {len(listPosts)}')
        for p in listPosts:
            try:
                stt = p.get_attribute('aria-posinset')
                if stt not in listId:
                    print(f'Bài số: {stt}')
                    listId.add(stt)
                    links = p.find_elements(By.XPATH, ".//a")
                    for link in links:
                        if link.is_displayed() and link.size['width'] > 0 and link.size['height'] > 0:
                            actions.move_to_element(link).perform()
                            href = link.get_attribute('href')
                            if '/ads/' in href:
                                try:
                                    share = p.find_element(By.XPATH, '//*[@aria-label="Send this to friends or post it on your profile."]')
                                    actions.move_to_element(share).perform()
                                    share.click()
                                    sleep(3)
                                    parent_element = driver.find_element(By.XPATH, ".//*[@aria-label='List of available \"share to\" options in the unified share sheet.']")
                                    list = parent_element.find_elements(By.XPATH, "./div/div/div")
                                    for item in list:
                                        item_text = item.text.lower()
                                        if "copy link" in item_text:
                                            item.click()
                                            sleep(2)
                                            break
                                    
                                    fb_link = pyperclip.paste()
                                    fb_id = extract_post_id(fb_link)
                                    data = [account_id, fb_link, fb_id]
                                    posts.create(data)
                                    print(json.dumps(data, indent=4))
                                except Exception as e:
                                    print(f'Lỗi click share: {e}')
                                break
            except Exception as e:
                print(e)
        if len(listId) >= 20:
            print('Đã được 20 bài viết, refresh trang!')
            driver.refresh() 
            listId.clear() 
            driver.execute_script("document.body.style.zoom='0.2';")
            sleep(3)
        else:
            driver.execute_script("window.scrollBy(0, 500);")
        sleep(5)
    driver.quit()