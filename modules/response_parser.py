import re
import streamlit as st

class ResponseParser:
    def parse_response(self, response, game_actions):
        if not response:
            st.warning("Warning: Response is empty. Returning default action.")
            print("Warning: Response is empty. Returning default action.")
            return self._get_first_action(game_actions)
        
        # 使用正则表达式提取 <Action> 标签中的内容
        match = re.search(r'<Action>(.*?)</Action>', response, re.DOTALL)
        if match:
            chosen_action = match.group(1).strip().lower()
            st.write(f"Extracted action: '{chosen_action}'")
            
            # 将game_actions转换为一致的格式进行比较
            available_actions = self._normalize_actions(game_actions)
            
            # 验证行动是否在可用行动列表中
            for valid_action_key, valid_action_lower in available_actions.items():
                if valid_action_lower == chosen_action:
                    return valid_action_key
            
            # 如果没有精确匹配，尝试模糊匹配
            for valid_action_key, valid_action_lower in available_actions.items():
                if valid_action_lower in chosen_action or chosen_action in valid_action_lower:
                    st.write(f"Fuzzy matched to: {valid_action_key}")
                    return valid_action_key
                    
            st.warning(f"Warning: Chosen action '{chosen_action}' is not in available actions: {list(available_actions.keys())}. Returning default action.")
            print(f"Warning: Chosen action '{chosen_action}' not found in: {list(available_actions.keys())}")
            return self._get_first_action(game_actions)
        else:
            # 如果没找到标签，尝试在文本中查找动作关键词
            response_lower = response.lower()
            available_actions = self._normalize_actions(game_actions)
            
            for valid_action_key, valid_action_lower in available_actions.items():
                if valid_action_lower in response_lower:
                    st.write(f"Found action mention in text: {valid_action_key}")
                    return valid_action_key
            
            st.warning("Warning: No valid <Action> tag or action mention found in response. Returning default action.")
            print("Warning: No valid action found in response")
            return self._get_first_action(game_actions)
            
    def _normalize_actions(self, game_actions):
        """将各种可能的动作格式转换为统一的小写字典用于比较"""
        if isinstance(game_actions, dict):
            return {action: action.lower() for action in game_actions.keys()}
        elif isinstance(game_actions, list):
            return {action: action.lower() for action in game_actions}
        else:
            return {'default': 'default'}
    
    def _get_first_action(self, game_actions):
        """获取第一个可用动作作为默认值"""
        if isinstance(game_actions, dict) and game_actions:
            return list(game_actions.keys())[0]
        elif isinstance(game_actions, list) and game_actions:
            return game_actions[0]
        else:
            return "default"

    def parse_reflection(self, response):
        if not response:
            return "No reflection provided"
        
        match = re.search(r'<Reflection>(.*?)</Reflection>', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # 如果没找到标签，返回整个响应作为反思内容
            return response.strip()