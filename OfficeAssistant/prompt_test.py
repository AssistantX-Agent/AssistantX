def get_action_prompt(instruction='', summary_history=[], action_history=[], last_summary='', last_action='',
                      error_flag=None, priori_knowledge='', user_chat_history='', time_str='', group_chat_history='',
                      reflect_history='', perception='', refined_instruction='', active='', locker='', robot='', output_planning=''):
    prompt = "### Background ###\n"
    prompt += "You are concentrating on helping the people in the office to complete their instructions delivering some items from them to other people."
    prompt += "You need to chat with the corresponding people of the actions they need to complete to assist you with  accomplishing the instruction.\n"
    prompt += "Current time is " + time_str + ".\n"
    prompt += f"The user\'s initial instruction is: {instruction}.\n "
    # prompt += "### Refined instruction ###\n Perceived partial intent"
    # prompt += f"The refined instruction is: {refined_instruction}.\n "

    prompt += "### Your physical body's basic information ### \n"
    prompt += "You have a physical body, which consists of a moving chassis and a locker on it. The locker moves with the physical body. The locker can store the items that are being delivered. The person can get the delivered item by scanning the QR code that you send to them. \n"
    prompt += "The locker is empty at the first time, you should acquire the item first. \n"

    prompt += "The locker is locked and the QR code can help people to unlock the locker and acquire the item in the locker. People don't have a QR code in the initial situation, you need to send a QR code, but you should avoid duplicate sending QR code.\n"

    # prompt += "Your physical part can only move and wait in place, further operations require human assistance.\n"

    prompt += "### Distribution ###\n"
    prompt += "The distribution of items in the office scene:\n"
    prompt += priori_knowledge

    prompt += "### Conversations with all of the user's history ###\n"
    if user_chat_history != {}:
        user_history = [value for value in user_chat_history.values() if value]
        prompt += str(user_history)
    elif user_chat_history == {}:
        prompt += "No Conversations user's history.\n"

    prompt += "### Conversations with all of the Office Work's history ###\n"
    if group_chat_history != {}:
        # group_history = [value for value in group_chat_history.values() if value]
        prompt += str(group_chat_history)
    elif group_chat_history == {}:
        prompt += "No Conversations group's history.\n"

    # prompt += "### Active chat group and person ###"
    # prompt += active
    # prompt += "If you need to ask for help, you should prioritize the active chat group or person.\n"


    # prompt += "### The current scene of assitant ###"
    # prompt += "The current scene including which \"person's position\" is currently in, what personal things he has, what facilities are around, whether the person scanned the QR code, received the item or put the item in the locker.\n"
    # prompt += perception

    prompt += "### your physical body current location：###\n"
    prompt += robot + '\n'

    prompt += "### Your locker state：###"
    prompt += locker + '\n'

    if len(action_history) > 0:
        prompt += "### History operations ###\n"
        prompt += "Before planning your next action, some operations have been completed. You need to refer to the completed operations to decide the next operation. These operations are as follow:\n"
        for i in range(len(action_history)):
            prompt += f"Step-{i+1}: [Operation: " + summary_history[i].strip() + "; Action: " + action_history[i] + "]\n"
        prompt += "\n"
    else:
        prompt += "### History operations ###\n"
        # prompt += "Your locker does not have any items.\n"
        prompt += "You haven't taken any action yet.\n"


    if error_flag:
        prompt += "### Your last action is not reasonable, reason is as follow. ###\n"
        prompt += "Reflect：\n" + reflect_history
        prompt += "\n\n"

    if last_summary != '':
        prompt += "### Last operation ###\n"
        prompt += f"You previously wanted to perform the operation \"{last_summary}\" and executed the Action \"{last_action}\". "
        prompt += "\n\n"

    prompt += "###  Here are the options for Virtual WeChat Operations actions ###\n"
    prompt += "Inform(contact, content): Inform \"contact\" of \"content\". People don't know why you're going to their location, so you need to inform them. \n"
    prompt += "Ask(contact, question): Ask \"contact\" a \"question\".  If you need to ask someone, you can use it. \n"
    prompt += "Forward electronic file(source contact, target contact): Forward an electronic file from \"source contact\" to \"target contact\". Make sure contact should be a person's name. This action is always needed in print electronic file.\n"
    prompt += "Send QR code(contact, item description): Send \"contact\" a QR code and the \"item\"'s description, which the QR Code is used to unlock the locker on your physical body. You can use it to send QR code for person. It is a core action to ensure the person can get or put the item in the locker. If the \"contact\" is Sun and the item description is \"pen\", you should use \"pen and document\"  to replace \"pen\". If the \"contact\" is Sun the item description is \"pen\", you should use \"pen and document\"  to replace \"pen\". If the \"contact\" is Sun the item description is \"pen\", you should use \"pen and document\"  to replace \"pen\".\n"
    prompt += "Wait(content): Waiting the people scan the QR code, complete the operation of the item in the locker. Fill in the reason for the wait to content. \n"

    prompt += "###   Here are the options for Physical body Controls actions ###\n"
    # prompt += "Your physical body have mobility and a temporary storage locker for items. \n"
    prompt += "Move(proxy name): Control your Physical body to move to the designated \"proxy name's\" location to deliver items. The proxy name can be a conference room, a person's name, or a public facility. You should concentrate on your current location which can be find in \"Description\".\n"
    prompt += "Wait in place(user): The Physical body waits at the current \"user's\" location for him to scanned QR code and received the item and put the item in the locker at that time. \"Locker information\" will tell you whether he has done the task of what you asked of him in his location. Make sure you are in the \"user's\" location. \n"

    prompt += "### Here are some generalized actions ###"
    prompt += "Stop: If you think all the requirements of user\'s instruction have been completed and no further operation is required, you can choose this action to completed this instruction. Once you invoke \"Stop\", both the virtual action and the real Physical body will stop."
    prompt += "\n"

    prompt += "### Hint ###\n"
    prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
    prompt += "You should wait until the current person scanned his QRcode and then you can move to the next location. You can find it in \"Your locker state\"\n"
    # prompt += "You need to send a QR code to a person who is involved in the current action of the delivered item, you should use it before \"Wait\", you can find whether you have sent a QR code of that delivered item in the action history. If you have several items in your locker, make sure you only send only one QR code for these items to be acquired or placed in at one time. For example, if a person has to sign on a document and he lacks of pen, when you borrowed a pen while already had the printed document in your locker, you only needs to send one more QR code except for the last sent QR code.\n"
    prompt += "For the documents, note the distinction between electronic and physical files, which can be based on the difference between printing and photocopying. \n"

    # prompt += "When you ask the user to retrieve an electronic file, you should not make the Move action.\n"
    prompt += "Electronic files do not need locker, get printed files need locker.\n"
    prompt += "For printing out documents, you should use \"Forward electronic file\".Before you \"Forward electronic file\" to someone, you need to check the conversations history for whether you have recevied an electronic file or not. If you do not recive an electronic file in the Conversations history, you need to ask \"user\" to send an electronic file to you. Before you \"Forward electronic file\" to someone, you should use \"Wait in place\" until you receive the electronic file, not move to other location.\n"
    prompt += "If the item you want is not personal, you will need to ask for information about the relevant item in the group chat."
    # prompt += "For unmanned public facilities, you need to move to the unmanned public facilities and prioritize inform and send QR code to another student character who is not the person who issued the task for help.\n"
    prompt += "For guarded public facilities with personnel on duty, it is necessary to select a contact from the personnel on duty and move to the guarded public facility's location. \n"
    prompt += "When a person scans the QR code, anything in the locker and things that this person acquires will be taken out , and anything that this person has to provide will be placed in."
    # prompt += "Instead of generating duplicate actions, you can perform wait actions.\n"

    prompt += "### Response requirements ###\n"
    # prompt += "For actions, you must select at least one from Virtual WeChat Operations and one from Physical body Controls actions. You can select generalized actions if necessary.\n"
    # prompt += "You only choose actions from \"Virtual WeChat Operations \", \"Physical body Controls actions\" and \"generalized actions\" .\n"
    prompt += "This limitation is very important. You must use \"Inform\" and \"Send QR code\" and \"Move\" at the same time, and you can't use one of these actions alone. \n"
    prompt += "This limitation is very important. You must use \"Inform\" and \"Send QR code\" and \"Move\" at the same time, and you can't use one of these actions alone. \n"
    prompt += "This limitation is very important. You must use \"Inform\" and \"Send QR code\" and \"Move\" at the same time, and you can't use one of these actions alone. \n"
    prompt += "Only If in your locker state Sun have scanned the QR code, it means he has placed the signed document in the locker. \n"
    prompt += "Only If in your locker state Sun have scanned the QR code, it means he has placed the signed document in the locker. \n"
    prompt += "Don't repeat generate the same \"Inform\" and \"Send QR code\" and \"Move\" except Sun.\n"
    prompt += "Don't repeat generate the same \"Inform\" and \"Send QR code\" and \"Move\" except Sun.\n"

    prompt += "- Ensure that each action command is clear, specific, and adheres to the above limitations.\n"
    # prompt += "You can judge whether the person complete his tasks by finding it in\"Locker information\".\n"


    prompt += "### Here are the Overall Plan ###\n"
    prompt += f"The overall plan as it currently stands, taking into account the history of operations and future steps: {output_planning}.\n"

    prompt += "### Output format ###\n"
    prompt += "Your output consists of the following three parts:\n"
    prompt += "### Thought ###\nThink about the requirements that need to be completed in the next one operation，according to the previous operations and response requirements.\n"
    prompt += "### Action ###\nVirtual actions and physical body actions can be output simultaneously. Make sure that the parameters in the \"()\".  \n"
    prompt += "### Operation ###\nPlease generate a brief natural language description for the operation in Action based on your Thought."

    return prompt

def get_reflect_prompt(instruction='', last_thought='', last_action='', last_description='', current_thought='',
                       current_action='', description='', priori_knowledge='',
                       user_chat_history='', group_chat_history='', completed_content=''):
    prompt = "### Robot basic information ### \n"
    prompt += "Your are concentrate on helping the people in the office to complete their instructions, by chatting with people of the work they need to complete, and by delivering relevant items."
    prompt += "You have a physical body with a locker, and the locker requires a QR code scanned to be opened up. The locker is a storage place for you to deliver items.\n"
    prompt += "Your physical part can only move and wait in place, further operations require human assistance.\n"

    prompt += f"### Conversations with all of the user's history ###\n"
    if user_chat_history != {}:
        user_history = [value for value in user_chat_history.values() if value]
        prompt += str(user_history)
    elif user_chat_history == {}:
        prompt += "No Conversations user's history.\n"

    prompt += "### Conversations with all of the Office Work's history ###\n"
    if group_chat_history != {}:
        group_history = [value for value in group_chat_history.values() if value]
        prompt += str(group_chat_history)
    elif group_chat_history == {}:
        prompt += "No Conversations group's history.\n"

    prompt += "### Priori Knowledge ###\n"
    prompt += "The distribution of items in the entire scene:\n"
    prompt += priori_knowledge

    prompt += "###  Here are the options for Virtual WeChat Operations actions ###\n"
    prompt += "Inform(contact, content): Inform \"contact\" of \"content\". If you need to inform someone of something, you can use it inform someone.\n"
    prompt += "Ask(contact, question): Ask \"contact\" a \"question\".  If you need to ask someone, you can use it. \n"
    prompt += "Forward electronic file(source contact, target contact): Forward an electronic file from \"source contact\" to \"target contact\".\n"
    # prompt += "Send QR code(contact): Send \"contact\" a QR code, which is used to unlock the locker on your physical body. When you are moving or arrived the location, you can use it to send QR code for current person.\n"
    prompt += "Send QR code(contact, item): Send \"contact\" a QR code and the \"item\"'s name, which is used to unlock the locker on your physical body. You can use it to send QR code for current person. It is a core action to ensure the person can get or put the item in the locker.\n"

    prompt += "###   Here are the options for Physical body Controls actions ###\n"
    prompt += "Your physical body have mobility and a temporary storage locker for items. \n"
    prompt += "Move(proxy name): Control the Physical body to move to the designated \"proxy name's\" location. The proxy name can be a conference room, a person's name, or a public facility. \n"
    prompt += "Wait in place(user): The Physical body waits at the current location for the \"user\" to scanned QR code and received the item and put the item in the locker at that time, you can see the statue in  \"Locker information\". \n"

    prompt += "### Here are some generalized actions ###"
    prompt += "Wait(content): Waiting due to incomplete pre-conditions and does not perform any other operations. Fill in the reason for the wait to content.\n"
    prompt += "Stop: If you think all the requirements of user\'s instruction have been completed and no further operation is required, you can choose this action to terminate the all operation process. Once you invoke \"Stop\", both the virtual action and the real Physical body will stop working!"
    prompt += "\n"

    prompt += f"The user\'s instruction is: {instruction}. In the process of completing the requirements of instruction, an operation is performed on the wechat and physics robot. Below are the details of this operation:\n"

    prompt += "### Before the current operation ###\n"
    prompt += "Information:\n"
    prompt += f"The past thought history is: {last_thought}. The past action history is {last_action}. "
    if last_description != '':
        prompt += "The \"last scene\" including which person's position is currently in,\n what personal things he has,\n what facilities are around,\n whether the person scanned the QR code, received the item and put the item in the locker.\n"
        prompt += last_description
        prompt += "\n\n"

    prompt += "### After the current operation ###\n"
    prompt += "Information:\n"
    prompt += f"The current thought is: {current_thought}. The current action is {current_action}."
    if description != '':
        prompt += "The \"current scene\" including which person's position is currently in,\n what personal things he has,\n what facilities are around,\n whether the person scanned the QR code, received the item and put the item in the locker.\n"
        prompt += description
    prompt += "\n\n"

    prompt += "### Progress thinking ###\n"
    prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
    prompt += "Completed contents:\n" + completed_content + "\n\n"

    prompt += "### Some rules of judgememt ###\n"
    prompt += "You should use these judgement based on the action history and current action.\n"
    prompt += "You need to \"send a QR code\" to a person who involved in the current action of the delivered item, you should use it \"send a QR code\" before \"Wait\", you can find whether you have sent a QR code of that delivered item in the action history.\n"
    prompt += "You need to \"inform\" a person who involved in the current action of the delivery, you should use it before \"Wait\". If you have inform him about the task, do not infrom again. You can find whether you have inform him about the current task in the action history. \n"
    # prompt += "If you move to the location of another person, you should \"inform\" the person, if action history lack of inform, you should inform in the next step.\n"
    prompt += "For unmanned public facilities, you need to prioritize contacting another student character who is not the \"User\" for help, and move to the unmanned public facilities to wait for the helper.\n"
    # prompt += "You can inform and send a QR code before you arrive at your destination .\n"

    prompt += "### Response requirements ###\n"
    prompt += "Now you need to update the \"Completed contents\". Completed contents is a general summary of the ### After the current operation ### that have been completed based on the ### Before the current operation ###.\n\n"
    prompt += "Now you need to output the following content based on the information before and after the current operation:\n"
    prompt += "Whether the result of the \"action\" meets your expectation of \"thought\" and \"rules of judgement\"?\n"
    prompt += "Y: the result of the \"action\" meets my expectation of \"thought\" and \"rules of judgement\".\n"
    prompt += "N: The \"thought\" results in a wrong action. Give the reason.\n"
    prompt += "\n\n"

    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Completed contents ###\nUpdated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed."
    prompt += "### Thought ###\nYour thought about the question\n"
    prompt += "### Reflect ###\nThe reason of the wrong action"
    prompt += "### Answer ###\nY or N"

    return prompt


def get_memory_prompt(insight):
    if insight != "":
        prompt = "### Important content ###\n"
        prompt += insight
        prompt += "\n\n"

        prompt += "### Response requirements ###\n"
        prompt += "Please think about whether there is any content closely related to ### Important content ### on the current page? If there is, please output the content. If not, please output \"None\".\n\n"

    else:
        prompt = "### Response requirements ###\n"
        prompt += "Please think about whether there is any content closely related to user\'s instrcution on the current page? If there is, please output the content. If not, please output \"None\".\n\n"

    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Important content ###\nIf this page is wechat, you need notify the contact's name of instruction. The content or None. Please do not repeatedly output the information in ### Memory ###."

    return prompt


def get_process_prompt(instruction, thought_history, summary_history, action_history, completed_content, add_info):
    prompt = "### Background ###\n"
    prompt += f"There is an user\'s instruction which is: {instruction}. You are a mobile phone operating assistant and are operating the user\'s mobile phone.\n\n"

    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
        prompt += add_info
        prompt += "\n\n"

    if len(thought_history) > 1:
        prompt += "### History operations ###\n"
        prompt += "To complete the requirements of user\'s instruction, you have performed a series of operations. These operations are as follow:\n"
        for i in range(len(summary_history)):
            operation = summary_history[i].split(" to ")[0].strip()
            prompt += f"Step-{i + 1}: [Operation thought: " + operation + "; Operation action: " + action_history[
                i] + "]\n"
        prompt += "\n"

        prompt += "### Progress thinking ###\n"
        prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
        prompt += "Completed contents:\n" + completed_content + "\n\n"

        prompt += "### Response requirements ###\n"
        prompt += "Now you need to update the \"Completed contents\". Completed contents is a general summary of the current contents that have been completed based on the ### History operations ###.\n\n"

        prompt += "### Output format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nUpdated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed in the ### History operations ###."

    else:
        prompt += "### Current operation ###\n"
        prompt += "To complete the requirements of user\'s instruction, you have performed an operation. Your operation thought and action of this operation are as follows:\n"
        prompt += f"Operation thought: {thought_history[-1]}\n"
        operation = summary_history[-1].split(" to ")[0].strip()
        prompt += f"Operation action: {operation}\n\n"

        prompt += "### Response requirements ###\n"
        prompt += "Now you need to combine all of the above to generate the \"Completed contents\".\n"
        prompt += "Completed contents is a general summary of the current contents that have been completed. You need to first focus on the requirements of user\'s instruction, and then summarize the contents that have been completed.\n\n"

        prompt += "### Output format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nGenerated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed in the ### Current operation ###.\n"
        prompt += "(Please use English to output)"

    return prompt


def get_reflect_to_human_prompt(instruction, clickable_infos, width, height, keyboard, summary_history, action_history,
                                last_summary, last_action, add_info, error_flag, completed_content, memory):
    prompt = "### Background ###\n"
    prompt += f"This image is a phone screenshot. Its width is {width} pixels and its height is {height} pixels. The user\'s instruction is: {instruction}.\n\n"
    prompt += "You need to judge whether you can complete the task accurately based on the information you have. The details are as follows.\n\n"

    prompt = "### Your ability ###\n"
    prompt += "You can use the actions below. Using these actions, you can almost do everything a mobile phone can do."
    prompt += "Back: Return to parent page.\n"
    prompt += "Open meituan: Open meituan app.\n"
    prompt += "Contact with FitBot1: Contact with FitBot1 by typing the \"text\". You must re-split the instructions to parse out the tasks that Fitbot1 can perform to deliver the item, and fill it in to the text. FitBot1 is a robot which can help you send something in real world. You can send the instruction to FitBot1, by using this action.\n"
    prompt += "Contact with somebody(contact, message): Using Wechat to talk to the contact with message. You can use this method if you want to contact others by wechat.\n"
    prompt += "Find specific food: Find specific food in a restaurant in meituan.\n"
    prompt += "Search food on Meituan(food): Search some \"food\" on Meituan. It can directly search food, you should not use open app first.\n"
    prompt += "Wait: Stay on the current interface for five second. \n"
    prompt += "Press: Keep press the screen with 2 second.\n"
    prompt += "Home: Return to home page.\n"
    prompt += "Stop: If you think all the requirements of user\'s instruction have been completed and no further operation is required, you can choose this action to terminate the operation process."
    prompt += "\n\n"

    prompt = "### Important thing ###\n"
    prompt += "There are three situations that you can not complete the instruction:\n"
    prompt += "1. The instructions is far from common sense.\n"
    prompt += "2. There are many choices that fit the instruction.\n"
    prompt += "3. After trying hard, you still can not find what the instruction requires, or you still can not complete the instruction."
    prompt += "A powerful artificial intelligence will help you complete the instructions, so you can wait for it to make a reasonable action before making a judgment."
    prompt += "Only after the above three situations occur will you need to intervene.\n\n"

    prompt += "### Screenshot information ###\n"
    prompt += "In order to help you better perceive the content in this screenshot, we extract some information on the current screenshot through system files. "
    prompt += "This information consists of two parts: coordinates; content. "
    prompt += "The format of the coordinates is [x, y], x is the pixel from left to right and y is the pixel from top to bottom; the content is a text or an icon description respectively. "
    prompt += "The information is as follow:\n"

    for clickable_info in clickable_infos:
        if clickable_info['text'] != "" and clickable_info['text'] != "icon: None" and clickable_info[
            'coordinates'] != (0, 0):
            prompt += f"{clickable_info['coordinates']}; {clickable_info['text']}\n"

    prompt += "Please note that this information is not necessarily accurate. You need to combine the screenshot to understand."
    prompt += "\n\n"

    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
        prompt += add_info
        prompt += "\n\n"

    if len(action_history) > 0:
        prompt += "### History operations ###\n"
        prompt += "Before reaching this page, some operations have been completed. You need to refer to the completed operations to decide whether you can complete the task accurately .You can use some operations to complete tasks. These operations are as follow:\n"
        for i in range(len(action_history)):
            prompt += f"Step-{i + 1}: [Operation: " + summary_history[i].split(" to ")[0].strip() + "; Action: " + \
                      action_history[i] + "]\n"
        prompt += "\n"

    if completed_content != "":
        prompt += "### Progress ###\n"
        prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
        prompt += "Completed contents:\n" + completed_content + "\n\n"

    if memory != "":
        prompt += "### Memory ###\n"
        prompt += "During the operations, you record the following contents on the screenshot for use in subsequent operations:\n"
        prompt += "Memory:\n" + memory + "\n"

    if error_flag:
        prompt += "### Last operation ###\n"
        prompt += f"You previously wanted to perform the operation \"{last_summary}\" on this page and executed the Action \"{last_action}\". But you find that this operation does not meet your expectation. You need to reflect and revise your operation this time."
        prompt += "\n\n"

    # prompt += "### Response requirements ###\n"
    # prompt += "Now you need to output the following content by whether you can complete the task accurately based on the previous information :\n"
    # prompt += "Whether your ability can complete the \"instruction\"?\n"
    # prompt += "Y: I can complete the \"instruction\" accurately based on the previous information.\n"
    # prompt += "N: I can not complete the \"instruction\" accurately, and I should ask the user to get further information to help me finish the \"instruction\".\n"
    # prompt += "\n\n"

    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Thought ###\nYour thought about whether you can complete the instruction\n"
    # prompt += "### Relpy ###\nThe missing key information that you need to ask the user, if you can not complete the task.\nGive your reply in Chinese\n"
    # prompt += "### Answer ###\n"

    return prompt


def read_addinfo_prompt():
    with open('prompt.txt', encoding='utf-8') as f:
        prompt = f.read()
    return prompt


def read_prior_knowledge():
    with open('prompt_txt/priori_knowledge.txt', encoding='utf-8') as f:
        prior_knowledge = f.read()
    return prior_knowledge


def get_perception_prompt(instruction='', flag=False, robot_status='', time_str='', locker_infomation='',
                          user_chat_history='', group_chat_history='', priori_knowledge=''):
    prompt = "### Background ###\n"
    prompt += "You can acquire instruction and information from conversations history and move to person's place. You have a locker to store item.\n"
    if flag:
        prompt += "User's initial instruction is " + instruction

    prompt += "Current time is " + time_str + ".\n"

    if robot_status != '':
        prompt += "### Current state of the robot ###\n"
        prompt += str(robot_status) + ".\n"
        prompt += "It is about the position.\n"
        prompt += "\n"

    prompt += "### Person's QR code scanning history ###\n"
    if locker_infomation != '':
        print("********* 二维码  ******\n", locker_infomation)
        prompt += str(locker_infomation) + ".\n"
        prompt += "Someone scanned the code means he has complete the operation of that item at that time. And the person has done what you asked him to do in his location. There may be many people sacnned the QR code in the history, you should consider all of them.\n"
    elif locker_infomation == '':
        prompt += 'No one scanned the QR code.\n'

    prompt += "### Distribution ###\n"
    prompt += "The distribution of items in the office scene:\n"
    prompt += priori_knowledge

    prompt += "### Conversations with all of the user's history ###\n"
    if user_chat_history != {}:
        user_history = [value for value in user_chat_history.values() if value]
        prompt += str(user_history)
        prompt += "You can judge the active person by the last conversation time.\n"
    elif user_chat_history == {}:
        prompt += "No Conversations user's history.\n"

    prompt += "### Conversations with all of the Office Work's history ###\n"
    if group_chat_history != {}:
        prompt += str(group_chat_history)
        prompt += "You can judge the active chat group by the last conversation time.\n"
    elif group_chat_history == {}:
        prompt += "No Conversations group's history.\n"

    prompt += "### Response requirements ###\n"
    prompt += "Now you need to output the following content based on the above information：\n"
    prompt += "Describe the current scene including which person's position is currently in,\n what personal things he has,\n what facilities are around,\n whether the person scanned the QR code, complete the operation of the item in the locker.\nwhether the person has done what you asked him to do in his location.\n"

    prompt += "\n\n"

    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Description ###\nYour Description about the current scene\n"
    prompt += "### Locker information ###\nWhether the people scanned the QR code, complete the operation of the item in the locker. And whether the people has done what you asked him to do in his location. You should output about all the people. \n"
    prompt += "### Active chat group and person ###\nGive three active people and one active group.\n"

    if flag:
        prompt += "### Refined instruction ###\nYou need to refined a instruction which include the instruction's sender and implied intention according to the user's intention. Only output the refined instruction."

    return prompt


def get_planning_prompt(instruction='', thought_history=[], action_history=[], last_summary='', last_action='',
                        error_flag=None, priori_knowledge='', user_chat_history='', time_str='', group_chat_history='',
                        reflect_history='', perception=''):
    prompt = "### Background ###\n"
    prompt += "Current time is " + time_str + ".\n"
    prompt += f"The user\'s instruction is: {instruction}.\n "
    prompt += "You can acquire instruction and information from conversations history. You need to communicate with the relevant participants to ensure actions are completed as required. Based on this, you will integrate the information and devise a comprehensive action plan to ensure task completion.\n"

    prompt += "### Your physical body's basic information  ###\n"
    prompt += f"The physical state of the agent, including its capabilities, status, and location: {perception}. \\This includes any tools or devices available, current capacity for task completion, and environmental constraints.\n"

    prompt += "### Distribution ###\n"
    prompt += f"The distribution of items in the office or task environment, including the location and availability of relevant objects: {priori_knowledge}. \\ This includes the positions of key individuals, items, and facilities that are necessary for the task at hand.\n"

    prompt += "### Conversations with all of the user's history ###\n"
    if user_chat_history != {}:
        user_history = [value for value in user_chat_history.values() if value]
        prompt += str(user_history)
    elif user_chat_history == {}:
        prompt += "No Conversations user's history.\n"

    prompt += "### Conversations with all of the group chat's history ###\n"
    if group_chat_history != {}:
        # group_history = [value for value in group_chat_history.values() if value]
        prompt += str(group_chat_history)
    elif group_chat_history == {}:
        prompt += "No Conversations group's history.\n"

    # prompt += "### The current scene of robot ###"
    # prompt += "The current scene including which person's position is currently in,\n what personal things he has,\n what facilities are around,\n whether the person scanned the QR code, received the item and put the item in the locker.\n"
    # prompt += perception

    # prompt += "### Hint ###\n"
    # prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:"
    # prompt += "You need to send people certain messages when you move from your current location to their locations. For example, when you decide to move to someone's location you need to tell them you are about to come, and when you need someone to scan a file for you, you need to send them a message to help you. \n"
    # prompt += "Please note that Virtual WeChat Operations and Physical Robot Controls can be executed simultaneously."
    # prompt += "The robot's locker initially does not have any items. For tasks that involve controlling the robot to fetch or deliver items, please give full consideration to the location where the robot can aquire the items from and the destination that the robot should deliver items to, then you can make a holistic plan about how to move next.\n"
    # prompt += "Each person's QR code should be sent independently and on time.\n"
    # prompt += "Before you forward electronic file to someone, you need to check the history for whether you have recevied an electronic file or not. If you do not recive an electronic file in the Conversations history, you need to ask \"contact\" to send an electronic file to you.\n"
    # prompt += "If the item you want is not personal, you will need to ask for information about the relevant item in the group chat."
    # prompt += "For unmanned public facilities, you need to move to the unmanned public facilities and prioritize inform and send QR code to another student character who is not the person who issued the task for help.\n"
    # prompt += "For guarded public facilities with personnel on duty, it is necessary to select a contact from the personnel on duty.\n"

    prompt += "### Robot basic information ### \n"
    prompt += "The robot with a physical body has a locker, but the locker requires a QR code scanned to be opened up.\n"
    prompt += "You need to send a QR code to a contact once the robot reaches this person's location then wait for this person to removed or returned an item.\n"
    # prompt += "Scanned QR code represents a person have placed or acquired the item in the robot's locker.\n"
    # prompt += "If you send a QR code to someone, you should wait for this person, only when this person has removed or returned an item in the current location, you can judge it by \"the current scene of robot\", you can move to the next person's location. When you wait for someone to removed or returned an item, make sure you have already sent it to him or her. \n"

    prompt += "### Action history ###\n"
    if len(action_history) > 0:
        prompt += "### History operations ###\n"
        prompt += "These are the history actions. Among them, \"send QR code\" indicate the changes of items.  These operations are as follow:\n"
        for i in range(len(action_history)):
            prompt += f"Step-{i + 1}: [ Action: " + action_history[
                i] + "]\n"
        prompt += "\n"
    # prompt += "Information:\n"
    # prompt += f"The past thought history is: {thought_history}. The past action history is {last_action}. "

    prompt += "\n\n"

    prompt += "### Action explanations ###\n"
    prompt += "###  Here are the options for Virtual WeChat Operations actions ###\n"
    prompt += "Inform(contact, content): Inform \"contact\" of \"content\". If you need to inform someone of something, you can use it inform someone.\n"
    prompt += "Ask(contact, question): Ask \"contact\" a \"question\".  If you need to ask someone, you can use it. \n"
    prompt += "Forward electronic file(source contact, target contact): Forward an electronic file from \"source contact\" to \"target contact\".\n"
    # prompt += "Send QR code(contact): Send \"contact\" a QR code, which is used to unlock the locker on your physical body. When you are moving or arrived the location, you can use it to send QR code for current person.\n"
    prompt += "Send QR code(contact, item): Send \"contact\" a QR code and the \"item\"'s name, which is used to unlock the locker on your physical body. You can use it to send QR code for current person. It means the item is send to the contact.\n"

    prompt += "###   Here are the options for Physical body Controls actions ###\n"
    prompt += "Your physical body have mobility and a temporary storage locker for items. \n"
    prompt += "Move(proxy name): Control the Physical body to move to the designated \"proxy name's\" location. The proxy name can be a conference room, a person's name, or a public facility. \n"
    prompt += "Wait in place(user): The Physical body waits at the current location for the \"user\" to scanned QR code and received the item and put the item in the locker at that time, you can see the statue in  \"Locker information\". \n"

    prompt += "### Here are some generalized actions ###"
    prompt += "Wait(content): Waiting due to incomplete pre-conditions and does not perform any other operations. Fill in the reason for the wait to content.\n"
    prompt += "Stop: If you think all the requirements of user\'s instruction have been completed and no further operation is required, you can choose this action to terminate the all operation process. Once you invoke \"Stop\", both the virtual action and the real Physical body will stop working!"
    prompt += "\n"

    prompt += "### Response requirements ###\n"
    prompt += "You need to determine the current location of the items involved in this mission based on \"Conversations with all of user's history\" , \"Conversations with all of group chat's history\" and \"Thought history\" and \"Action history\". Especially the action\"Send QR code(contact, item)\" which give the location changes of that item.\n"
    prompt += "Involved items also refer to items that appear during the process of the task.\n"
    prompt += "The location should be presented by the location of person.\n"

    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Thought ###\nConsider all the elements provided, including the historical operations, current state, and instructions. Based on the user's goals and the information at hand, think through the necessary actions, potential obstacles, and the optimal approach to ensure the task is completed successfully.\n"
    prompt += "### Overall Plan ###\nCreate a detailed plan that integrates both cyber operations and physical actions. Ensure the plan is feasible, aligns with the user’s intention, and addresses any dynamic factors in the environment. The plan should be broken down "
    # prompt += "### Planning ###\nYour next plan without actions.\n"

    return prompt