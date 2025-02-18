# from handles import create_browse_link_spy_fb

# create_browse_link_spy_fb(1, None)

import json
from sql import accounts

cookies = []
with open('cookie.json') as cookie_file:
    cookies = cookie_file.read()  # Đọc nội dung file rồi mới parse JSON

accounts.update(1, {
    'cookies': cookies,
})

account = accounts.find(1)
print(account)