import os
from helpers.base import config

def create_extension_with_proxy(user_dir, proxy):
    proxy_host = proxy['host']
    proxy_port = proxy['port']
    username = proxy['user']
    password = proxy['pass']
    
    output_dir = os.path.join(user_dir, 'Extensions')

    ext_dir = os.path.join(output_dir, proxy_host.replace(".", "_"))  # Thư mục chứa extension
    os.makedirs(ext_dir, exist_ok=True)

    # Nội dung manifest.json
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 3,
        "name": "Proxy Authentication",
        "permissions": [
            "proxy",
            "storage",
            "webRequest",
            "webRequestAuthProvider"
        ],
        "host_permissions": ["<all_urls>"],
        "background": {
            "service_worker": "background.js"
        }
    }
    """
    
    # Nội dung background.js
    background_js = f"""
    chrome.proxy.settings.set({{
        value: {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost"]
            }}
        }},
        scope: "regular"
    }}, function() {{
        console.log("Proxy configuration set.");
    }});

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }},
        {{ urls: ["<all_urls>"] }},
        ["blocking"]
    );
    """
    
    # Ghi file manifest.json
    with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
        f.write(manifest_json)
    
    # Ghi file background.js
    with open(os.path.join(ext_dir, "background.js"), "w") as f:
        f.write(background_js)

    return ext_dir 
