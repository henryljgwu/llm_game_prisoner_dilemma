from openai import OpenAI
import os
import json
import time
import concurrent.futures

class LLMAccess:
    def __init__(self, providers_file='config/llm_providers.json'):
        self.providers = self.load_providers(providers_file)
        self.clients = {}

    def load_providers(self, providers_file):
        with open(providers_file, 'r') as f:
            return json.load(f)

    def get_client(self, provider_name):
        if (provider_name not in self.clients):
            provider_config = self.providers[provider_name]
            api_key = os.getenv(provider_config['api_key_env'])
            self.clients[provider_name] = OpenAI(
                api_key=api_key,
                base_url=provider_config['base_url']
            )
        return self.clients[provider_name]

    def send_request(self, prompt, provider_name, model, max_retries=5, retry_delay=10, timeout=120):
        client = self.get_client(provider_name)
        retries = 0
        
        while retries <= max_retries:
            try:
                # 使用concurrent.futures来实现超时机制
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    if not model.startswith("o"):
                        future = executor.submit(
                            client.chat.completions.create,
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.6,
                            max_tokens=1500
                        )
                    else:
                        print("Using o1 or o3")
                        future = executor.submit(
                            client.chat.completions.create,
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            max_completion_tokens=2500
                        )
                    
                    try:
                        response = future.result(timeout=timeout)
                        print('-'*10,'\n',response.choices[0].message.content,'\n','-'*10)
                        return response.choices[0].message.content
                    except concurrent.futures.TimeoutError:
                        # 请求超时
                        raise TimeoutError(f"Request timed out after {timeout} seconds")
                        
            except Exception as e:
                retries += 1
                if retries <= max_retries:
                    print(f"API request failed (attempt {retries}/{max_retries}): {e}")
                    print(f"Retrying after {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"API request failed, maximum retry attempts reached: {e}")
                    return None