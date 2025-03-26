import streamlit as st
import json
import os
from modules.main_controller import MainController
from modules.config_manager import ConfigManager
from modules.role_manager import RoleManager
from modules.llm_access import LLMAccess
import pandas as pd
from datetime import datetime

class StreamlitGameApp:
    def __init__(self):
        # 创建一个共享的RoleManager实例
        self.role_manager = RoleManager()
        
        # 将共享的RoleManager传递给MainController
        self.controller = MainController(role_manager=self.role_manager)
        
        self.config_manager = ConfigManager()
        self.llm_access = LLMAccess()
        
        # Initialize session state for storing custom roles
        if 'custom_roles' not in st.session_state:
            st.session_state.custom_roles = []
        if 'game_in_progress' not in st.session_state:
            st.session_state.game_in_progress = False
        if 'current_game_state' not in st.session_state:
            st.session_state.current_game_state = None

    def render_game_config(self):
        st.subheader("Game Configuration")
        
        # Display current roles
        if st.session_state.custom_roles:
            st.write("### Current Players")
            cols = st.columns(len(st.session_state.custom_roles))
            for i, role in enumerate(st.session_state.custom_roles):
                with cols[i]:
                    st.write(f"**Name:** {role['name']}")
                    st.write(f"**Behavior:** {role['behavior']}")
                    st.write(f"**Provider:** {role['provider']}")
                    st.write(f"**Model:** {role['model']}")
                    if st.button(f"Remove {role['name']}", key=f"remove_{i}"):
                        st.session_state.custom_roles.pop(i)
                        st.rerun()
        
        # Create new role section
        st.write("### Add New Player")
        
        # Get LLM providers information
        providers = self.llm_access.providers
        
        # Create combined provider-model options
        provider_model_options = []
        for provider_name, provider_info in providers.items():
            for model in provider_info["available_models"]:
                provider_model_options.append(f"{provider_name}-{model}")
        
        with st.form(key="add_role_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Default names
                name_placeholder = "Jordan" if not st.session_state.custom_roles else "Lee"
                name = st.text_input("Player Name", value=name_placeholder)
                
                # Select behavior from available roles with mapping
                available_roles = {role.name: role for role in self.role_manager.roles}
                role_names = list(available_roles.keys())
                selected_role_name = st.selectbox("Select Role Type", role_names)
                selected_role = available_roles[selected_role_name]
            
            with col2:
                # Combined provider-model selection
                provider_model = st.selectbox(
                    "LLM Provider and Model",
                    provider_model_options
                )
                
                # Split the selection to get provider and model separately
                provider, model = provider_model.split("-", 1)
                
                # Display the provider and model separately for clarity
                st.write(f"**Selected Provider:** {provider}")
                st.write(f"**Selected Model:** {model}")
            
            # Display behavior description
            st.write(f"**Behavior Description:** {selected_role.behavior}")
            
            submit_button = st.form_submit_button(label="Add Player")
            if submit_button:
                new_role = {
                    "name": name,
                    "role_type": selected_role_name,
                    "behavior": selected_role.behavior,
                    "provider": provider,
                    "model": model
                }
                st.session_state.custom_roles.append(new_role)
                st.rerun()
        
        # Remove the Preview section since we now use a combined selection
        
        # Button to clear all roles
        if st.session_state.custom_roles and st.button("Clear All Players"):
            st.session_state.custom_roles = []
            st.rerun()
            
        return st.session_state.custom_roles

    def render_game_status(self, game_state, view_mode="plain"):
        if not game_state:
            return

        st.subheader(f"Round {game_state['round']}")

        # Display actions
        if "actions" in game_state:
            st.write("Actions:")
            actions_df = pd.DataFrame([
                {"Role": role, "Action": data['action']}
                for role, data in game_state["actions"].items()
            ])
            st.table(actions_df)
            
            # Display raw responses
            st.write("Raw Responses:")
            for role, data in game_state["actions"].items():
                if "raw_response" in data:
                    with st.expander(f"{role}'s raw response"):
                        if view_mode == "markdown":
                            st.markdown(f"```\n{data['raw_response']}\n```")
                        else:
                            st.code(data['raw_response'])

        # Display payoffs
        if "payoffs" in game_state:
            st.write("Payoffs:")
            payoffs_df = pd.DataFrame([game_state["payoffs"]])
            st.table(payoffs_df)

        # Display reflections
        if "reflections" in game_state:
            st.write("Reflections:")
            for role, reflection in game_state["reflections"].items():
                st.write(f"**{role}'s reflection:**")
                if view_mode == "markdown":
                    st.markdown(reflection)
                else:
                    st.write(reflection)
                st.write("---")  # Add separator between reflections

    def render_history_viewer(self):
        st.subheader("Game History")
        
        # Get log files
        log_dir = self.config_manager.get_config('log_directory')
        if not os.path.exists(log_dir):
            st.warning("No game logs found.")
            return

        log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
        if not log_files:
            st.warning("No game logs available.")
            return
        
        selected_log = st.selectbox("Select Game Log", log_files, key="plain_history_log")
        
        # Add option to show raw responses - with unique key
        show_raw_responses = st.checkbox("Show Raw Responses", value=False, key="history_raw_responses")
        
        if selected_log:
            with open(os.path.join(log_dir, selected_log), 'r') as f:
                log_data = json.load(f)
                
            for round_idx, round_data in enumerate(log_data):
                with st.expander(f"Round {round_idx + 1}"):
                    self.render_game_status(round_data, "plain") if show_raw_responses else self.render_game_status({
                        "round": round_data["round"],
                        "actions": {k: {"action": v["action"]} for k, v in round_data["actions"].items()} if "actions" in round_data else {},
                        "payoffs": round_data.get("payoffs", {}),
                        "reflections": round_data.get("reflections", {})
                    }, "plain")

    def render_markdown_viewer(self):
        st.subheader("Game History (Markdown View)")
        
        # Get log files
        log_dir = self.config_manager.get_config('log_directory')
        if not os.path.exists(log_dir):
            st.warning("No game logs found.")
            return

        log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
        if not log_files:
            st.warning("No game logs available.")
            return
        
        # File selection
        selected_log = st.selectbox("Select Game Log", log_files, key="markdown_history_log")
        
        if not selected_log:
            return
            
        # Load the selected log
        with open(os.path.join(log_dir, selected_log), 'r') as f:
            log_data = json.load(f)
        
        # Add filtering options
        st.write("### Display Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Option to show specific content
            show_actions = st.checkbox("Show Actions", value=True, key="markdown_actions")
            show_raw_responses = st.checkbox("Show Raw Responses", value=True, key="markdown_raw_responses")
            show_payoffs = st.checkbox("Show Payoffs", value=True, key="markdown_payoffs")
            show_reflections = st.checkbox("Show Reflections", value=True, key="markdown_reflections")
            
        with col2:
            # Get all player names from the log
            all_players = set()
            for round_data in log_data:
                if "actions" in round_data:
                    all_players.update(round_data["actions"].keys())
            
            # Player filter if we have players
            selected_players = st.multiselect(
                "Filter by Players (empty = show all)", 
                list(all_players),
                default=[],
                key="player_filter"
            )
            
            # Round range selection
            total_rounds = len(log_data)
            round_range = st.slider("Round Range", 1, total_rounds, (1, total_rounds))
        
        # Generate markdown content based on filters
        markdown_content = []
        
        # Only process rounds in the selected range
        for round_idx in range(round_range[0]-1, round_range[1]):
            if round_idx >= len(log_data):
                break
                
            round_data = log_data[round_idx]
            round_content = [f"## Round {round_idx + 1}\n"]
            
            # Filter players if needed
            filtered_players = selected_players if selected_players else (
                round_data["actions"].keys() if "actions" in round_data else []
            )
            
            # Display actions
            if show_actions and "actions" in round_data:
                round_content.append("### Actions:")
                actions_text = []
                for role, data in round_data["actions"].items():
                    if not selected_players or role in selected_players:
                        actions_text.append(f"- **{role}**: {data['action']}")
                        
                    # Add raw responses if enabled
                    if show_raw_responses and "raw_response" in data:
                        actions_text.append(f"  \n---\nRaw response:\n```\n{data['raw_response']}\n```\n---\n")
                
                round_content.append("\n".join(actions_text) + "\n")

            # Display payoffs (fix list/dict handling issue)
            if show_payoffs and "payoffs" in round_data:
                round_content.append("### Payoffs:")
                payoffs_text = []
                
                # Check if payoffs is a list or dict and handle accordingly
                if isinstance(round_data["payoffs"], dict):
                    # If it's a dict, handle as originally planned
                    for role, score in round_data["payoffs"].items():
                        if not selected_players or role in selected_players:
                            payoffs_text.append(f"- **{role}**: {score}")
                elif isinstance(round_data["payoffs"], list):
                    # If it's a list, try to get the first element (which might be a dict)
                    if round_data["payoffs"] and isinstance(round_data["payoffs"][0], dict):
                        for role, score in round_data["payoffs"][0].items():
                            if not selected_players or role in selected_players:
                                payoffs_text.append(f"- **{role}**: {score}")
                    else:
                        # If not in expected format, simply display raw content
                        payoffs_text.append(f"- Raw payoffs data: {round_data['payoffs']}")
                else:
                    # Other type cases
                    payoffs_text.append(f"- Payoffs data format not recognized: {type(round_data['payoffs'])}")
                
                round_content.append("\n".join(payoffs_text) + "\n")

            # Display reflections
            if show_reflections and "reflections" in round_data:
                round_content.append("### Reflections:")
                for role, reflection in round_data["reflections"].items():
                    if not selected_players or role in selected_players:
                        round_content.append(f"#### {role}'s reflection:")
                        round_content.append(reflection + "\n")
            
            round_content.append("---\n")  # Add separator between rounds
            markdown_content.extend(round_content)
        
        # Join all content and display
        full_content = "\n".join(markdown_content)
        
        # Add copy button
        st.download_button(
            "Download as Markdown",
            full_content,
            file_name=f"game_log_{selected_log.replace('.json', '')}.md",
            mime="text/markdown"
        )
        
        # Display the markdown content
        st.markdown(full_content)

    def run(self):
        st.title("LLM Game System")
        
        tab1, tab2, tab3 = st.tabs(["Game Runner", "History Viewer", "Markdown Viewer"])
        
        with tab1:
            custom_roles = self.render_game_config()
            
            start_disabled = len(custom_roles) < 2
            
            if st.button("Start Game", disabled=start_disabled):
                if len(custom_roles) < 2:
                    st.error("Please add at least 2 players")
                else:
                    # Setup the game
                    st.session_state.game_in_progress = True
                    st.session_state.current_game_state = None
                    
                    # Clear previous temporary roles
                    self.role_manager.clear_temp_roles()
                    
                    # Convert custom roles to format expected by MainController
                    role_names = []
                    for role in custom_roles:
                        # Get behavior from original role type
                        original_role = self.role_manager.get_role(role["role_type"])
                        
                        # Create a temporary role in the role manager
                        role_obj = self.role_manager.add_temp_role(
                            name=role["name"],
                            behavior=original_role.behavior,
                            llm_config={
                                "provider": role["provider"],
                                "model": role["model"]
                            }
                        )
                        # Ensure role was created successfully
                        if role_obj:
                            role_names.append(role["name"])
                        else:
                            st.error(f"Failed to create role '{role['name']}'")
                            break
                    
                    if len(role_names) == len(custom_roles):
                        # Show debug info
                        st.write(f"Created players: {', '.join(role_names)}")
                        
                        # Run game with progress updates
                        with st.spinner("Game in progress..."):
                            try:
                                game_state = self.controller.run_game("prisoner_dilemma", role_names)
                                st.session_state.current_game_state = game_state
                            except Exception as e:
                                st.error(f"Game execution error: {str(e)}")
                            finally:
                                st.session_state.game_in_progress = False
            
            # Show the current game state if a game is running or complete
            if st.session_state.current_game_state:
                st.write("### Final Game Results")
                self.render_game_status(st.session_state.current_game_state)
        
        with tab2:
            self.render_history_viewer()
        
        with tab3:
            self.render_markdown_viewer()

if __name__ == "__main__":
    app = StreamlitGameApp()
    app.run()
