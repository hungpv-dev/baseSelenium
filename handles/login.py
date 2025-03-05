from helpers.omo_captcha import get_code_from_img
from time import sleep
from sql import accounts

def login(tab, driver, account):
    tab['status'] = 'Kiểm tra đăng nhập!'
    check = False
    print('Start check login...')
    status_login = check_login(driver)
    print(f'Check login: {status_login}')
    check = status_login
    if status_login == False:
        tab['status'] = 'Đang thử login với cookies...'
        print(f'Login with cookie')
        driver.setCookies(account.get('cookies'))
        driver.get('https://facebook.com', e_wait=3)
        accept_all_cookies = driver.find_all('//*[@aria-label="Allow all cookies"]', last=True)
        if accept_all_cookies:
            accept_all_cookies.click()
        tab['status'] = 'Đang kiểm tra login...'
        status_login = check_login(driver)
        print('Check login with cookies:', status_login)
        check = status_login
        if status_login == False:
            print('Login with username and password')
            tab['status'] = 'Đăng nhập cookie thất bại, thử lại với user và pass...'
            login_with_user_pass(driver, account)
            check = check_login(driver)
            print(f'Login: {check}')
            status = 1
            if status_login:
                status = 2
            accounts.update(account.get('id'), {'status': status})
            print(f'Update account')
    if check:
        tab['status'] = 'Đăng nhập thành công!'
        print(f'Save cookie')
        cookies = driver.get_cookies()
        accounts.update(account.get('id'), {
            'cookies' : cookies,
        })
    return check

def check_login(driver):
    sleep(2)
    driver.clickOk()
    print('Check blocked')
    checkBlock = False
    checkLogin = False

    messages = [
        "your account has been locked",
        "We suspended your account",
        "Account locked",
        "You’re Temporarily Blocked"
    ]

    for mess in messages:
        print(f"Block: {mess}")
        eleCheck = driver.find(f"//*[contains(text(), '{mess}')]")
        if eleCheck:
            if mess == "You’re Temporarily Blocked":
                profile = driver.find('//*[@aria-label="Your profile"]')
                if profile:
                    driver.get('https://facebook.com/home.php', e_wait=2)
                    driver.clickOk()
                    sleep(1)
                eleCheck = driver.find(f"//*[contains(text(), '{mess}')]")
                if eleCheck:
                    checkBlock = True
            else:
                checkBlock = True

    profile = driver.find('//*[@aria-label="Your profile"]')
    if profile:
        checkLogin = True

    if checkBlock:
        return False
    
    return checkLogin
    
def login_with_user_pass(driver, account):
    driver.find('email', 'id', account.get('user'))
    driver.find('pass', 'id', account.get('pwd'))
    btnSubmit = driver.find('loginbutton', 'id') or driver.find('login', 'name')
    btnSubmit.click()
    sleep(5)
    accept_all_cookies = driver.find_all('//*[@aria-label="Allow all cookies"]', last=True)
    if accept_all_cookies:
        accept_all_cookies.click()
    get_code_from_captcha(driver)
    sleep(5)
    authenapp = driver.find("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'authentication app')]")
    if authenapp is not None:
        code = get_code_from_2fa(driver, account.get('two_fa'))
        sleep(2)
        push_code(driver, code)
    
    print('Trust this device')
    nexts = driver.find_all(f"//*[contains(text(), 'Trust this device')]")
    for next in nexts:
        try:
            next.click()
        except: 
            pass
    sleep(5)
    driver.clickText('Dismiss',wait=5)
    sleep(5)
    

def get_code_from_2fa(driver, two_fa):
    driver.new_tab('https://2fa.live')
    sleep(5)
    driver.find('listToken','id').send_keys(two_fa)
    sleep(1)
    driver.find('submit','id').click()
    sleep(5)
    print('Submit code')
    value = driver.find('output','id').get_attribute('value')
    print(f"Value code: {value}")
    parst = value.split('|')
    code = parst[-1]
    print(f"Code là: {code}")
    driver.switch_tab(0,close=True)
    return code

def get_code_from_captcha(driver):
    img_captchas = driver.find_all('//img[@referrerpolicy="origin-when-cross-origin"]', wait=5)
    src = ''
    for img in img_captchas:
        captcha_url = img.get_attribute("src")
        if 'captcha' in captcha_url:
            src = captcha_url
            break

    if src == '':
        return
    
    print(f'Captcha cần xử lý: {src}')
    code = get_code_from_img(src)
    push_code(driver, code)

def push_code(driver, code):
    if code:
        print('Nhập code')
        driver.find('email', 'name', code)
        driver.find('input[type="text"]', 'css', code)
        sleep(2)
        print('Continue')
        driver.clickText('Continue',wait=5)
        sleep(5)
