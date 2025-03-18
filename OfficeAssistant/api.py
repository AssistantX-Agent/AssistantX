import base64
import time

import requests

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def inference_chat(chat, model, api_url, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "model": model,
        "messages": [],
        "max_tokens": 2048,
        "temperature": 0.01,
        "seed": 1234
    }

    for role, content in chat:
        data["messages"].append({"role": role, "content": content})

    while True:
        try:
            res = requests.post(api_url, headers=headers, json=data)
            res_json = res.json()
            res_content = res_json['choices'][0]['message']['content']
        except Exception as e:
            print("Network Error:")
            try:
                print(res.json())
            except:
                print("Request Failed")
        else:
            break
    
    return res_content


def inference_chat_claude(chat, model, api_url='', token=''):

    url = "https://4.0.wokaai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-qOd5gOIvXNNyvZ1G29Cc649b7216431e80A9Ef2f0398D3De",
        "Content-Type": "application/json"
    }

    data = {
        # "model": "claude-3-5-sonnet-20240620", # 'claude-3-sonnet-20240229'
        "model": "claude-3-opus-20240229", # 'claude-3-sonnet-20240229'
        # "model": "claude-3-sonnet-20240229", # 'claude-3-sonnet-20240229'
        "messages": [],
        "max_tokens": 4098,
        "temperature": 0.01
    }

    for role, content in chat:
        data["messages"].append({"role": role, "content": content})

    while True:
        try:
            res = requests.post(url, headers=headers, json=data)
            res_json = res.json()
            res_content = res_json['choices'][0]['message']['content']
            # print(res_json)
        except:
            print("Network Error:")
            try:
                print(res.json())
            except:
                print("Request Failed")
        else:
            break

    return res_content


from  zhipuai import ZhipuAI

def inference_chat_glm(chat, token):

    retry_count = 0
    messages = []

    client = ZhipuAI(api_key=token)
    for role, content in chat:
        messages.append({"role": role, "content": content})
    # print(messages)
    while True:
        try:
            response = client.chat.completions.create(
                    model='glm-4-plus',
                    messages=messages,
                    max_tokens=4098,
                    temperature=0.1
                )
            content = response.choices[0].message.content
            return content
        except Exception as e:
            time.sleep(1)
            retry_count += 1
            print(e)

from openai import OpenAI
def inference_chat_qwen(chat,qwen_api):
    client = OpenAI(
        api_key=qwen_api, # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
    messages = []

    for role, content in chat:
        messages.append({"role": role, "content": content})
    completion = client.chat.completions.create(
        model="qwen-turbo",
        messages=messages,
        temperature=0.001
        )
    content = completion.choices[0].message.content
    return content

