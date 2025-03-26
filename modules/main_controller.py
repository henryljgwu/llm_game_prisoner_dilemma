from .config_manager import ConfigManager
from .llm_access import LLMAccess
from .role_manager import RoleManager
from .prompt_generator import PromptGenerator
from .response_parser import ResponseParser
from .logging_module import LoggingModule
from .visualization import Visualization
from .game_rules import GameRules
import streamlit as st
import pandas as pd
from datetime import datetime

class MainController:
    def __init__(self, role_manager=None):
        self.config_manager = ConfigManager()
        self.llm_access = LLMAccess()
        # 允许外部传入RoleManager实例
        self.role_manager = role_manager if role_manager else RoleManager()
        self.prompt_generator = PromptGenerator(language=self.config_manager.get_config('default_language'))
        self.response_parser = ResponseParser()
        self.visualization = Visualization()
        self.logging = LoggingModule(log_directory=self.config_manager.get_config('log_directory'))

    def run_game(self, game_name, role_names):
        self.visualization.start_game(game_name)
        game_rules = GameRules(game_name)
        
        # Display game rules at the beginning
        st.markdown("## Game Rules")
        st.markdown(game_rules.get_rules())
        
        st.markdown("### Available Actions")
        actions_dict = game_rules.get_actions()
        for action, desc in actions_dict.items():
            st.markdown(f"- **{action}**: {desc}")
        
        # Add debug information
        st.markdown(f"## Starting Game: {game_name}")
        st.markdown(f"### Player List: {', '.join(role_names)}")
        st.markdown(f"### Available temporary roles: {', '.join([r.name for r in self.role_manager.temp_roles])}")
        
        roles = []
        for name in role_names:
            role = self.role_manager.get_role(name)
            if role is None:
                st.error(f"Role not found: {name}")
                st.markdown(f"Available roles: {[r.name for r in self.role_manager.roles]}")
                st.markdown(f"Temporary roles: {[r.name for r in self.role_manager.temp_roles]}")
            else:
                roles.append(role)
                st.markdown(f"**Retrieved role:** {name} (Behavior: {role.behavior[:50]}...)")
        
        if len(roles) != len(role_names):
            raise ValueError(f"Expected {len(role_names)} roles, but only found {len(roles)}")
        
        # Initialize game state with empty dicts
        game_state = {"round": 0, "actions": {}, "reflections": {}, "payoffs": {}}
        log_id = self.logging.start_game_log(game_name)
        
        # Track cumulative scores
        cumulative_scores = {role.name: 0 for role in roles}
        game_state["cumulative_scores"] = cumulative_scores
        
        # Round progress counter
        round_counter = 1
        
        while not game_rules.is_game_over(game_state):
            # Display round header
            st.markdown(f"## Round {round_counter}")
            st.markdown(f"*Started at {datetime.now().strftime('%H:%M:%S')}*")
            
            # Action Phase
            st.markdown("### 🎭 Players deciding their actions...")
            current_actions = {}
            
            for role in roles:
                st.markdown(f"#### Player: **{role.name}** thinking...")
                
                # Pass game_rules object to prompt generator
                prompt = self.prompt_generator.generate_prompt(
                    role,
                    game_state,
                    game_rules
                )
                
                with st.expander(f"Prompt sent to {role.name} ({role.llm_config['provider']}/{role.llm_config['model']})"):
                    st.markdown(f"```\n{prompt}\n```")
                
                response = self.llm_access.send_request(
                    prompt=prompt,
                    provider_name=role.llm_config['provider'],
                    model=role.llm_config['model']
                )
                
                # Display full response
                with st.expander(f"{role.name}'s full response"):
                    st.markdown(response)
                
                # Parse response using available actions from game_rules
                action = self.response_parser.parse_response(response, game_rules.get_actions())
                current_actions[role.name] = {
                    'action': action,
                    'raw_response': response
                }
                
                st.markdown(f"**{role.name}** chose: **{action}**")
            
            # Update game state with current actions
            game_state["actions"] = current_actions
            
            # Calculate payoffs using the game_rules object
            payoffs = game_rules.get_payoff(game_state["actions"])
            game_state["payoffs"] = payoffs
            
            # Update cumulative scores
            for player, score in payoffs.items():
                game_state["cumulative_scores"][player] += score
            
            # Display round results
            st.markdown("### 📊 Round Results")
            actions_df = pd.DataFrame([
                {"Player": player, "Action": data['action'], "Score": payoffs.get(player, 0)}
                for player, data in current_actions.items()
            ])
            st.table(actions_df)
            
            # Display cumulative scores
            st.markdown("#### Cumulative Scores:")
            cumulative_df = pd.DataFrame([game_state["cumulative_scores"]])
            st.table(cumulative_df)

            # Reflection Phase
            st.markdown("### 💭 Players reflecting on this round...")
            current_reflections = {}
            
            for role in roles:
                st.markdown(f"#### {role.name} is reflecting...")
                
                reflection_prompt = self.prompt_generator.generate_reflection_prompt(
                    role, 
                    game_state,
                    game_rules
                )
                
                with st.expander(f"Reflection prompt for {role.name}"):
                    st.markdown(f"```\n{reflection_prompt}\n```")
                
                reflection_response = self.llm_access.send_request(
                    prompt=reflection_prompt,
                    provider_name=role.llm_config['provider'],
                    model=role.llm_config['model']
                )
                
                reflection = self.response_parser.parse_reflection(reflection_response)
                current_reflections[role.name] = reflection
                
                st.markdown(f"**{role.name}'s reflection:**")
                st.markdown(reflection)
                st.markdown("---")
            
            # Update reflections in game state
            game_state["reflections"] = current_reflections

            # Update game state
            game_state["round"] += 1
            round_counter += 1
            
            self.visualization.update_display(game_state)
            self.logging.log_round(game_state)
            
            # Round summary
            st.markdown(f"### ✅ Round {game_state['round']} completed at {datetime.now().strftime('%H:%M:%S')}")
            st.markdown("---")

        # Game over
        st.markdown("## 🏁 Game Over!")
        
        # Display final scores
        st.markdown("### 🏆 Final Scores")
        final_scores = pd.DataFrame([game_state["cumulative_scores"]])
        st.table(final_scores)
        
        # Determine winner(s)
        max_score = max(game_state["cumulative_scores"].values())
        winners = [player for player, score in game_state["cumulative_scores"].items() if score == max_score]
        
        if len(winners) == 1:
            st.markdown(f"### 👑 Winner: {winners[0]} with {max_score} points!")
        else:
            st.markdown(f"### 👑 Tie between: {', '.join(winners)} with {max_score} points each!")
        
        self.logging.save_log()
        
        # Don't clear temporary roles here - moved to the app logic
        
        return game_state