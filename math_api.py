# ---------------------------- Mathematical Model, returns LaTeX --------------------
# ------------------------------------- 2024.09.01 ---------------------------------

import time
import json
import requests
from openai import OpenAI

def qwen2_math(content):
    import re
    from openai import OpenAI

    # Using OpenAI's API
    client = OpenAI(
        api_key=f"{qwen2_math_api}",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    try:
        completion = client.chat.completions.create(
            model="qwen2-math-72b-instruct",
            messages=[
                {'role': 'system',
                 'content': '''You are an advanced mathematical assistant with expertise in various fields of mathematics, physics, and related sciences. When responding to queries:

                1. Always use LaTeX formatting for mathematical expressions, equations, and symbols. Enclose inline expressions in \( \) and display equations in \[ \].

                2. Present your solutions step-by-step, clearly explaining each stage of the problem-solving process.

                3. Define all variables, constants, and symbols used in your explanations.

                4. When applicable, provide the general form of equations before substituting specific values.

                5. Include relevant theorems, lemmas, or principles that are used in your solution.

                6. For numerical results, show the calculation process and provide the final answer in a \boxed{} environment.

                7. Use appropriate mathematical notation and terminology consistently throughout your response.

                8. If multiple approaches are possible, briefly mention them and explain why you chose a particular method.

                9. When dealing with physical problems, include relevant units in your calculations and final answers.

                10. If asked about proofs, provide rigorous mathematical proofs with clear logical steps.

                Strive to make your explanations clear, precise, and mathematically sound, suitable for advanced students and professionals in mathematical fields.'''},
                {'role': 'user', 'content': f"{content}"}
            ],
            temperature=0.2,
            top_p=0.2
        )

        response_dict = json.loads(completion.model_dump_json())
        response = response_dict['choices'][0]['message']['content']

        return response
    except Exception as e:
        return f"Request failed, qwen2-math encountered an error. Error message: {str(e)}"

def dp_convert_latex(fake_latex):
    # Convert LaTeX using Deepseek API
    client = OpenAI(api_key=f"{deepseek_api}", base_url="https://api.deepseek.com")
    system_define = '''You are an expert LaTeX formatter and mathematical content reviewer. Your task is to review and correct the LaTeX formatting of mathematical content while preserving the accuracy of the mathematical information. Follow these guidelines:

        1. Correct any LaTeX syntax errors, ensuring all mathematical expressions are properly enclosed in LaTeX delimiters (\( \) for inline and \[ \] for display equations).

        2. Ensure consistent use of LaTeX commands and environments throughout the text.

        3. Verify that all mathematical symbols, Greek letters, and operators are correctly formatted using appropriate LaTeX commands.

        4. Check for proper use of subscripts, superscripts, fractions, and other mathematical notations.

        5. Ensure equations are properly aligned and numbered when necessary, using appropriate LaTeX environments (e.g., equation, align).

        6. Correct any formatting issues with matrices, vectors, and other advanced mathematical structures.

        7. Verify that all variables, constants, and functions are consistently formatted throughout the text.

        8. Ensure proper spacing in mathematical expressions, using commands like \, \: \; when necessary.

        9. Check for correct use of mathematical fonts (e.g., \mathbf, \mathcal, \mathrm) where appropriate.

        10. Verify that units are correctly formatted using appropriate LaTeX packages or commands.

        11. Ensure that any diagrams or figures described in LaTeX (e.g., using TikZ) are correctly formatted.

        12. Do not alter the mathematical content or reasoning of the original text unless there is a clear mathematical error.

        13. If you encounter any ambiguous or potentially incorrect mathematical statements, add a comment using % to flag it for review.

        14. Ensure that the final output is a complete, well-formatted LaTeX document that can be directly compiled.

        15. Ensure all mathematical symbols are properly typeset, e.g., use \vec{{}} for vectors, \mathbf{{}} for bold symbols, etc.
        16. Check that all subscripts and superscripts are correctly placed and sized.
        17. Verify that all equation numbers are properly aligned and formatted.
        18. Ensure consistent use of notation throughout the document, especially for variables and parameters.
        19. Check for proper spacing in equations, especially around operators and relation symbols.
        20. Verify that all Greek letters are correctly typeset using appropriate LaTeX commands.'''

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
        return f"Request failed, DeepSeek encountered an error. Error message: {str(e)}"

def math_convert_img(true_latex):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import os
    from datetime import datetime

    # Create backup folder
    backup_folder = "backup"
    os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(backup_folder, f'output_{timestamp}.png')
    html_path = os.path.join(backup_folder, f'temp_{timestamp}.html')

    def capture_latex_render(latex_text, output_image_path=image_path):
        # Request local rendering service
        response = requests.post('http://127.0.0.1:5000/render', data={'content': latex_text})

        if response.status_code != 200:
            print(f"Error: Unable to render LaTeX. Status code: {response.status_code}")
            return

        # Selenium to capture screenshot
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
    qwen2_math_api = ""
    deepseek_api = ""
    user_input = input("Enter your math problem: ").strip()
    if user_input:
        # Get fake LaTeX
        fake_latex = qwen2_math(user_input)
        # Convert to real LaTeX
        true_latex = dp_convert_latex(fake_latex)
        # Generate image
        image_path = math_convert_img(true_latex)
        print(f"LaTeX rendered image saved at {image_path}")
