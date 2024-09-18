# Math_prompt
Codes to use qwen2-math api for constructing qq-bot

## Process

![Flowchart](./flow.jpg)

## PIP
```bash
pip install -r requirements.txt
```

## Others

1. You can focus solely on the prompt for this project, and you can also integrate other LLM API services or apply this project to other applications, such as qq-bot or wechat-bot.

2. For different LLM APIs, you may need to change some settings in `math_api.py`.

3. We choose qwen2-math-72b-instruct and deepseek-coder as the default models

4. For example:Could you help me solve the energy equation for the hydrogen atom in its ground state, specifically by solving its Schrödinger equation?

5. And you will get:

![Flowchart](./sch.PNG)