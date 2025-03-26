import streamlit as st

class PromptGenerator:
    def __init__(self, language='en'):
        self.language = language
        self.templates = {
            'en': {
                'action': """
You are now playing the role of {role_name}. 
Your strategy in this game is to {behavior}.

Game Rules:
{game_rules}

Available Actions:
{actions_description}

{experience_section}

Current Game State:
{game_state}

Based on the above information, please choose your next action. Your response should be in the following format:
<Action>chosen_action</Action>
Where chosen_action is one of the available actions.

You may include additional content in your response, but ensure the action is enclosed in <Action></Action> tags and can be parsed correctly.
""",
                'reflection': """
You are {role_name}, reflecting on the last round of the game.

Last Round Results:
- Your action: {my_action}
- Other players' actions: {other_actions}
- Payoffs: {payoffs}

Game Rules:
{game_rules}

Please analyze the results and provide your strategic thoughts for the next round. 
Your thought should be relate to your behavior. Your behavior is: {behavior}.
Your response should be in the following format:
<Reflection>your_thoughts</Reflection>
"""
            },
            'zh': {
                'action': """
你现在需要扮演{role_name}。
你的游戏策略是{behavior}。

游戏规则：
{game_rules}

可用行动：
{actions_description}

{experience_section}

当前游戏状态：
{game_state}

根据以上信息，请选择你的下一个行动。你的回复格式必须如下：
<Action>chosen_action</Action>
其中 chosen_action 是可用行动之一。

你可以在回复中添加额外内容，但需确保行动被 <Action></Action> 标签包裹并能被正确解析。
""",
                'reflection': """
你是{role_name}，正在反思游戏上一轮的结果。

上一轮结果：
- 你的行动：{my_action}
- 其他玩家的行动：{other_actions}
- 收益：{payoffs}

游戏规则：
{game_rules}

请分析结果并提供你对下一轮的战略思考。
请你确保你的思考和你的行为模式所匹配，你的行为模式是：{behavior}。
你的回复格式必须如下：
<Reflection>your_thoughts</Reflection>
"""
            }
        }

    def generate_prompt(self, role, game_state, game_rules, actions_dict=None, experience=None):
        template = self.templates.get(self.language, self.templates['en'])['action']
        
        # Get actions from game_rules if not provided
        if actions_dict is None:
            if hasattr(game_rules, 'get_actions'):
                actions_dict = game_rules.get_actions()
            else:
                st.warning("No actions provided and game_rules doesn't have get_actions()")
                actions_dict = {}
        
        # Debug
        print(f"Generating prompt for {role.name}")
        print(f"Available actions: {actions_dict}")
        
        # Format actions description
        if isinstance(actions_dict, dict):
            actions_description = "\n".join([f"- {action}" for action in actions_dict.keys()])
        elif isinstance(actions_dict, list):
            actions_description = "\n".join([f"- {action}" for action in actions_dict])
        else:
            actions_description = str(actions_dict)
        
        # Get game rules text
        if hasattr(game_rules, 'get_rules'):
            rules_text = game_rules.get_rules()
        else:
            rules_text = str(game_rules)
        
        # Format game state
        game_state_text = self._format_game_state(game_state)
        
        # Process experience section
        experience_section = "Previous Experience (if any):\n" + experience if experience else ""
        
        # Format the prompt
        formatted_prompt = template.format(
            role_name=role.name,
            behavior=role.behavior,
            game_rules=rules_text,
            actions_description=actions_description,
            experience_section=experience_section,
            game_state=game_state_text
        )
        
        st.write(f"Debug - Prompt for {role.name} created")
        return formatted_prompt

    def _format_game_state(self, game_state):
        """Format game state into readable text"""
        if not isinstance(game_state, dict):
            return str(game_state)
            
        result = []
        
        # Add round information
        round_num = game_state.get('round', 0)
        result.append(f"Current Round: {round_num + 1}")  # +1 for human-readable round number
        
        # Add history of actions if available
        if 'actions' in game_state and game_state['actions']:
            result.append("\nPrevious Actions:")
            for player, data in game_state['actions'].items():
                if isinstance(data, dict) and 'action' in data:
                    result.append(f"- {player}: {data['action']}")
                else:
                    result.append(f"- {player}: {data}")
        
        # Add payoffs if available
        if 'payoffs' in game_state and game_state['payoffs']:
            result.append("\nCurrent Scores:")
            for player, score in game_state['payoffs'].items():
                result.append(f"- {player}: {score}")
        
        return "\n".join(result)

    def generate_reflection_prompt(self, role, game_state, game_rules):
        template = self.templates.get(self.language, self.templates['en'])['reflection']
        
        # Extract player's action
        my_action = "None"
        if role.name in game_state["actions"]:
            action_data = game_state["actions"][role.name]
            if isinstance(action_data, dict) and 'action' in action_data:
                my_action = action_data['action']
            else:
                my_action = str(action_data)
        
        # Format other players' actions
        other_actions_text = ""
        for player, action_data in game_state["actions"].items():
            if player != role.name:
                if isinstance(action_data, dict) and 'action' in action_data:
                    other_actions_text += f"{player}: {action_data['action']}\n"
                else:
                    other_actions_text += f"{player}: {action_data}\n"
        
        # Format payoffs
        payoffs_text = ""
        if isinstance(game_state["payoffs"], dict):
            for player, score in game_state["payoffs"].items():
                payoffs_text += f"{player}: {score}\n"
        else:
            payoffs_text = str(game_state["payoffs"])
        
        # Get rules text
        if hasattr(game_rules, 'get_rules'):
            rules_text = game_rules.get_rules()
        else:
            rules_text = str(game_rules)
            
        # Format the prompt
        formatted_prompt = template.format(
            role_name=role.name,
            behavior=role.behavior,  # Added behavior parameter
            my_action=my_action,
            other_actions=other_actions_text,
            payoffs=payoffs_text,
            game_rules=rules_text
        )
        
        return formatted_prompt