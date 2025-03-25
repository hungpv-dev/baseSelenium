import google.generativeai as genai
API_TOKEN_GEMINI = 'AIzaSyAOVpv0d5_KEkF4xXi1jhA0DTh2-CWQ1Iw'

genai.configure(api_key=API_TOKEN_GEMINI)

# Chọn model phù hợp
model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Hoặc thử các model khác

# Nội dung cần phân tích
html_content = "<div>Example post with 100 likes and 20 shares</div>"

# Gửi request tới AI để phân tích nội dung
response = model.generate_content(html_content)

# In kết quả
print(response.text)
