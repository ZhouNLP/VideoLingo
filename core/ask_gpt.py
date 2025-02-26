import os, sys, json, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from threading import Lock
import json_repair
import json 
from openai import OpenAI
import time
from requests.exceptions import RequestException
from core.config_utils import load_key

LOG_FOLDER = 'output/gpt_log'
LOCK = Lock()

def save_log(model, prompt, response, log_title = 'default', message = None):
    os.makedirs(LOG_FOLDER, exist_ok=True)
    log_data = {
        "model": model,
        "prompt": prompt,
        "response": response,
        "message": message
    }
    log_file = os.path.join(LOG_FOLDER, f"{log_title}.json")
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_data)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)
        
def check_ask_gpt_history(prompt, model, log_title):
    # check if the prompt has been asked before
    if not os.path.exists(LOG_FOLDER):
        return False
    file_path = os.path.join(LOG_FOLDER, f"{log_title}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if item["prompt"] == prompt:
                    return item["response"]
    return False

def ask_gpt(prompt, response_json=True, valid_def=None, log_title='default'):
    api_set = load_key("api")
    llm_support_json = load_key("llm_support_json")
    max_retries = 3
    
    with LOCK:
        history_response = check_ask_gpt_history(prompt, api_set["model"], log_title)
        if history_response:
            return history_response
    
    if not api_set["key"]:
        raise ValueError("⚠️API_KEY is missing")
    
    messages = [{"role": "user", "content": prompt}]
    base_url = api_set["base_url"].strip('/') + '/v1' if 'v1' not in api_set["base_url"] else api_set["base_url"]
    client = OpenAI(api_key=api_set["key"], base_url=base_url)
    response_format = {"type": "json_object"} if response_json and api_set["model"] in llm_support_json else None
    
    for attempt in range(max_retries):
        try:
            completion_args = {
                "model": api_set["model"],
                "messages": messages
            }
            if response_format is not None:
                completion_args["response_format"] = response_format
            
            response = client.chat.completions.create(**completion_args)
            
            if response_json:
                try:
                    response_data = json_repair.loads(response.choices[0].message.content)
                    if valid_def:
                        valid_response = valid_def(response_data)
                        if valid_response['status'] != 'success':
                            save_log(api_set["model"], prompt, response_data, log_title="error", message=valid_response['message'])
                            if attempt < max_retries - 1:
                                time.sleep(2)
                                continue
                            raise ValueError(f"❎ API response error: {valid_response['message']}")
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    raise
            else:
                response_data = response.choices[0].message.content
                break
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise
            
    with LOCK:
        if log_title != 'None':
            save_log(api_set["model"], prompt, response_data, log_title=log_title)
    
    return response_data


if __name__ == '__main__':
    print(ask_gpt('hi there hey response in json format, just return 200.' , response_json=True, log_title=None))
