import json
import streamlit as st

class GameRules:
    def __init__(self, game_name):
        self.game_name = game_name
        self.game_config = self.load_game(game_name)
        self.rules = self.game_config['rules']
        print(f"Game rules loaded for: {game_name}")
        
    def load_game(self, game_name):
        try:
            with open(f'config/games/{game_name}.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading game configuration: {e}")
            print(f"Error loading game configuration: {e}")
            return {
                "name": "Default Game",
                "actions": ["Cooperate", "Defect"],
                "payoff": {"Cooperate,Cooperate": [3, 3]},
                "max_rounds": 3,
                "rules": "Default rules"
            }

    def get_actions(self):
        """Return available actions as dict with descriptions"""
        actions = self.game_config.get('actions', [])
        # Convert list to dict with descriptions
        return {action: f"Action: {action}" for action in actions}

    def get_rules(self):
        """Return game rules as string"""
        return self.rules

    def get_payoff(self, actions):
        """Calculate payoffs based on player actions"""
        try:
            # Debug
            st.write(f"Debug - Calculating payoff for: {actions}")
            print(f"Calculating payoff for: {actions}")
            
            # Extract action values from player-action dict
            if isinstance(actions, dict):
                # If actions is a dict of player:action_dict
                action_values = []
                for player, action_data in actions.items():
                    if isinstance(action_data, dict) and 'action' in action_data:
                        action_values.append(action_data['action'])
                    else:
                        action_values.append(str(action_data))
            else:
                # If actions is already a list
                action_values = actions
            
            # Normalize actions to match config case
            normalized_actions = [action.capitalize() for action in action_values]
            key = ','.join(normalized_actions)
            
            st.write(f"Debug - Lookup key: {key}")
            print(f"Lookup key: {key}")
            
            # Get payoffs from config
            payoffs = self.game_config['payoff'].get(key, [0, 0])
            
            # Map payoffs to player names
            if isinstance(actions, dict):
                player_names = list(actions.keys())
                if len(player_names) == len(payoffs):
                    return {player_names[i]: payoffs[i] for i in range(len(player_names))}
                else:
                    st.warning(f"Payoff length {len(payoffs)} doesn't match players {len(player_names)}")
                    # If lengths don't match, assign whatever we can
                    result = {}
                    for i in range(min(len(player_names), len(payoffs))):
                        result[player_names[i]] = payoffs[i]
                    return result
            else:
                # If actions is a list, return raw payoffs
                return payoffs
            
        except Exception as e:
            st.error(f"Error calculating payoff: {e}")
            print(f"Error calculating payoff: {e}")
            return {player: 0 for player in actions.keys()} if isinstance(actions, dict) else [0] * len(actions)

    def is_game_over(self, state):
        """Determine if the game is over based on current state"""
        max_rounds = self.game_config.get('max_rounds', 3)
        return state['round'] >= max_rounds