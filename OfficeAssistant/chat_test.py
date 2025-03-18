import copy
from MobileAgent.api import encode_image

def init_action_chat():
    operation_history = []
    # system_prompt = "You are an helpful AI office assistant. You can complete user's instructions by interacting with the user and controlling the physical robot. This physical robot can move based on a person's name or the name of an unattended facilities. And the robot is equipped with a smart lock temporary locker that can only be opened by a person scanning a QR code, so the robot's movements require human cooperation."
    system_prompt = "You are a helpful AI assistant. You need to combine all the historical and known information to make independent thinking and judgment, and take appropriate actions to gradually complete the user instructions. You should think about the next move, not all of them."
    operation_history.append(["system", [{"type": "text", "text": system_prompt}]])
    return operation_history
def init_planning_chat():
    operation_history = []
    system_prompt = "You are a helpful AI assistant."
    operation_history.append(["system", [{"type": "text", "text": system_prompt}]])
    return operation_history
def init_reflect_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI office assistant."
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history
def init_perception_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI office assistant."
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history


def init_memory_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI office assistant."
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history

def init_reflect_to_human_chat():
    operation_history = []
    sysetm_prompt = "You are a helpful AI mobile phone operating assistant. You need to judge whether you can complete the task accurately based on the information you have. "
    operation_history.append(["system", [{"type": "text", "text": sysetm_prompt}]])
    return operation_history

def add_response(role, prompt, chat_history, image=None):
    new_chat_history = copy.deepcopy(chat_history)
    if image:
        base64_image = encode_image(image)
        content = [
            {
                "type": "text", 
                "text": prompt
            },
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
        ]
    else:
        content = [
            {
            "type": "text", 
            "text": prompt
            },
        ]
    new_chat_history.append([role, content])
    return new_chat_history


def add_response_two_image(role, prompt, chat_history):
    new_chat_history = copy.deepcopy(chat_history)

    content = [
        {
            "type": "text", 
            "text": prompt
        }
    ]

    new_chat_history.append([role, content])
    return new_chat_history


def print_status(chat_history):
    print("*"*100)
    for chat in chat_history:
        print("role:", chat[0])
        print(chat[1][0]["text"] + "<image>"*(len(chat[1])-1) + "\n")
    print("*"*100)