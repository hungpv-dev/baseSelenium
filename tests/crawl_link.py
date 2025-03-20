# Danh sách link ban đầu
links = [
    "https://metastatus.com/ads-transparency",
    "https://www.facebook.com/ads/about/?entry_product=ad_library",
    "https://www.facebook.com/privacy/center/?entry_point=privacy_basics_redirect",
    "https://www.facebook.com/policies/",
    "https://www.facebook.com/policies/cookies/",
    "https://www.facebook.com/HomeBuysToledo/",
    "https://www.facebook.com/HomeBuysJeffersonville/",
    "https://www.facebook.com/61556975611752/",
    "https://l.facebook.com/l.php?u=https%3A%2F%2Fnudel.shop%2Fpages%2Fvip-club%3Ffbclid%3DIwZXh0bgNhZW0CMTAAAR3GhKDgC78YfiE702D1Zf5LjASHHGN7bFmh6vfYeRkvfD0AOz7Iigzs0bQ_aem_sEzVGxYf0ombJSkmhXkz7A&h=AT0pEmpeLpVfsgXs-7rF1Z6Xs6cQKjVt_E05ry_Np_juREpapDplUm67lXgVq33HlmtSFb08D8um8at7MY4uZ_QIg07SXjYcQrq4ddPACLVwq1dyRYeI6HGuMS7JVKtmQJg37g",
]

# Từ khóa cần loại bỏ
keywords_to_remove = ["ads-transparency", "privacy", "policies", "ads"]

# Lọc danh sách link
filtered_links = [
    link for link in links
    if link.startswith("https://www.facebook.com") and not any(keyword in link for keyword in keywords_to_remove)
]

print(filtered_links)
