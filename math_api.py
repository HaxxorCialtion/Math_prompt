# ----------------------------数学模型，返回Latex--------------------
# -------------------------------------2024.09.01----------------------------
import time
import json
import requests
from openai import OpenAI


def qwen2_math(content):
    import re
    from openai import OpenAI

    # 使用OpenAI的API
    client = OpenAI(
        api_key=f"{qwen2_math_api}",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    try:
        completion = client.chat.completions.create(
            model="qwen2-math-72b-instruct",
            messages=[
                {'role': 'system',
                 'content': '''You are an advanced mathematical assistant with expertise in various fields of mathematics, physics, and related sciences. Always use LaTeX formatting for mathematical expressions, equations, and symbols.'''},
                {'role': 'user', 'content': f"{content}"}
            ],
            temperature=0.2,
            top_p=0.2
        )

        response_dict = json.loads(completion.model_dump_json())
        response = response_dict['choices'][0]['message']['content']

        return response
    except Exception as e:
        return f"请求失败，qwen2-math出错。错误信息：{str(e)}"


def dp_convert_latex(fake_latex):
    # 使用Deepseek API转换Latex
    client = OpenAI(api_key=f"{deepseek_api}", base_url="https://api.deepseek.com")
    system_define = '''You are an expert LaTeX formatter and mathematical content reviewer. Your task is to review and correct the LaTeX formatting of mathematical content.'''

    try:
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=[
                {"role": "system", "content": system_define},
                {"role": "user", "content": fake_latex},
            ],
            stream=False
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        return f"请求失败，DeepSeek出错。错误信息：{str(e)}"


def math_convert_img(true_latex):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import os
    from datetime import datetime

    # 创建backup文件夹
    backup_folder = "backup"
    os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(backup_folder, f'output_{timestamp}.png')
    html_path = os.path.join(backup_folder, f'temp_{timestamp}.html')

    def capture_latex_render(latex_text, output_image_path=image_path):
        # 请求本地渲染服务
        response = requests.post('http://127.0.0.1:5000/render', data={'content': latex_text})

        if response.status_code != 200:
            print(f"Error: Unable to render LaTeX. Status code: {response.status_code}")
            return

        # Selenium操作截图
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        driver = webdriver.Edge(options=options)

        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            driver.get('file://' + os.path.abspath(html_path))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "MathJax")))

            js = """
            return {
                width: Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth),
                height: Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight)
            };
            """
            dimensions = driver.execute_script(js)
            driver.set_window_size(dimensions['width'] + 200, dimensions['height'] + 100)

            time.sleep(5)
            driver.save_screenshot(output_image_path)

            print(f"Screenshot saved as {output_image_path}")

        finally:
            driver.quit()

    capture_latex_render(true_latex)
    return image_path


if __name__ == "__main__":
    qwen2_math_api = "<your_api>"
    deepseek_api = "<your_api>"
    user_input = input("Enter your math problem: ").strip()
    if user_input:
        # 获取假latex
        fake_latex = qwen2_math(user_input)
        # 转换为真实latex
        true_latex = dp_convert_latex(fake_latex)
        # 生成图片
        image_path = math_convert_img(true_latex)
        print(f"LaTeX rendered image saved at {image_path}")
