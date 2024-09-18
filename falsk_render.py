from flask import Flask, request, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import numpy as np
import re

app = Flask(__name__)

def custom_latex_parser(text):
    # Handle LaTeX mathematical formulas
    text = text.replace('$$', r'\[').replace('$$', r'\]')
    text = text.replace('$', r'\(').replace('$', r'\)')

    # Handle Markdown headings
    def replace_heading(match):
        hashes = match.group(1)
        content = match.group(2)
        return f'<h{len(hashes)}>{content}</h{len(hashes)}>'

    text = re.sub(r'^(#{1,6})\s*(.*?)$', replace_heading, text, flags=re.MULTILINE)

    return text

def trim_image(image_path):
    image = Image.open(image_path)
    image_data = np.asarray(image)
    non_empty_columns = np.where(image_data.max(axis=0).max(axis=1) < 255)[0]
    non_empty_rows = np.where(image_data.max(axis=1).max(axis=1) < 255)[0]
    cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
    image_data_new = image_data[cropBox[0]:cropBox[1] + 1, cropBox[2]:cropBox[3] + 1, :]
    new_image = Image.fromarray(image_data_new)
    new_image.save(image_path)

def capture_latex_render(latex_text, output_image_path='output.png'):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(f"http://localhost:5000/render")

        textarea = driver.find_element(By.NAME, "content")
        textarea.send_keys(latex_text)

        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()

        # Wait for MathJax to finish rendering
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "MathJax")))

        # Get actual content height
        js = "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
        height = driver.execute_script(js)

        # Set window size, add extra height to ensure full content is captured
        driver.set_window_size(1000, height + 100)

        # Wait a short time to ensure the page is fully loaded
        time.sleep(2)

        # Capture the entire page
        driver.save_screenshot(output_image_path)

        # Trim the image
        trim_image(output_image_path)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    content = ""
    if request.method == 'POST':
        raw_content = request.form['content']
        content = custom_latex_parser(raw_content)
        capture_latex_render(content)

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat UI</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>
        <script>
        MathJax = {
          tex: {
            inlineMath: [['\\\\(', '\\\\)']],
            displayMath: [['\\\\[', '\\\\]']],
            packages: ['base', 'ams', 'noerrors', 'noundefined']
          },
          svg: {
            fontCache: 'global'
          }
        };
        </script>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            .math-container {
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <div style="min-height: 1200px; padding: 20px;">
            <h1>Chat UI</h1>
            <form method="POST">
                <textarea name="content" rows="10" cols="50" placeholder="Enter LaTeX text..."></textarea><br>
                <input type="submit" value="Submit">
            </form>
            <hr>
            <div>
                <h2>Output:</h2>
                <div class="math-container">
                    {{ content | safe }}
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', content=content)

@app.route('/render', methods=['POST'])
def render_latex():
    raw_content = request.form['content']
    content = custom_latex_parser(raw_content)

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LaTeX Render</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-mml-chtml.js"></script>
        <script>
        MathJax = {
          tex: {
            inlineMath: [['\\\\(', '\\\\)']],
            displayMath: [['\\\\[', '\\\\]']],
            packages: ['base', 'ams', 'noerrors', 'noundefined']
          },
          svg: {
            fontCache: 'global'
          }
        };
        </script>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            .math-container {
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <div style="min-height: 1200px; padding: 20px;">
            <div class="math-container">
                {{ content | safe }}
            </div>
        </div>
    </body>
    </html>
    ''', content=content)

if __name__ == '__main__':
    app.run(debug=True)
