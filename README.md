# LLM Game: Prisoner's Dilemma Simulation

This project simulates the classic Prisoner's Dilemma game using Large Language Models (LLMs) as players. The system allows different AI models to compete against each other with various behavioral strategies, providing insights into how different LLMs approach game theory problems.

## Overview

The Prisoner's Dilemma is a fundamental concept in game theory where two players must choose to either cooperate or defect. The payoff structure creates a tension between individual and collective interests:

- If both players cooperate, each receives a moderate reward (3 points)
- If one defects while the other cooperates, the defector gets a high reward (5 points) while the cooperator gets nothing (0 points)
- If both defect, each receives a small reward (1 point)

This implementation features:
- Multiple rounds of play (default: 3 rounds)
- Customizable AI player roles with different behavioral tendencies
- Support for various LLM providers (OpenAI, Deepseek, etc.)
- Detailed logging of game interactions and decision-making processes
- Streamlit-based UI for easy configuration and visualization

## Installation

### Prerequisites
- Python 3.7+
- Streamlit
- OpenAI Python client
- API keys for supported LLM providers

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-game-prisoner-dilemma.git
cd llm-game-prisoner-dilemma
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API keys:

Edit the `config/llm_providers.json` file to modify the API key values directly instead of using environment variables:
```json
{
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "your-openrouter-key-here",  // Replace "api_key_env" with "api_key"
        "available_models": ["deepseek/deepseek-r1"]
    },
    "gpt": {
        "base_url": "https://api.openai.com/v1",
        "api_key": "your-openai-key-here",      // Replace "api_key_env" with "api_key"
        "available_models": ["gpt-4o","o1-mini"]
    }
}
```

**Note**: You'll need to modify the `llm_access.py` file to read the direct API key instead of using environment variables. Change the following code in the `get_client` method:

```python
# Change this:
api_key = os.getenv(provider_config['api_key_env'])

# To this:
api_key = provider_config.get('api_key') or os.getenv(provider_config.get('api_key_env', ''))
```

## Configuration

### Available Configuration Files

- `config/config.json`: General application settings
- `config/games/prisoner_dilemma.json`: Game rules and payoff structure
- `config/llm_providers.json`: LLM provider configurations
- `config/roles.json`: Pre-defined behavioral roles for AI players

### Role Configuration

The system comes with several pre-defined roles:
- **Cooperative role**: Tends to cooperate, but will remember if another agent defects
- **Negative role**: Always defects initially, but will cooperate if the other agent consistently cooperates
- **Psychopath role**: Behaves randomly and unpredictably, possibly even cooperating with players who defect

You can customize these roles or add new ones by editing the `roles.json` file.

## Usage

1. Run the Streamlit application:
```bash
streamlit run main_app.py
```

2. In the web interface:
   - Add AI players by selecting from predefined roles
   - Configure each player with a name and LLM model
   - Start the game and watch the interactions
   - Review game logs for detailed analysis

## Game Flow

1. **Setup**: Players are initialized with specific roles and LLM configurations
2. **Action Phase**: In each round, players choose to cooperate or defect
3. **Resolution**: The system calculates scores based on the payoff matrix
4. **Reflection**: AI players analyze the round results and adjust their strategies
5. **Repeat**: Steps 2-4 are repeated for the configured number of rounds
6. **Results**: Final scores are calculated and winners declared

## Analysis

The system allows for in-depth analysis of AI decision-making:
- Compare how different LLMs approach the same problem
- Analyze the reflections to understand AI reasoning
- Export game logs in both JSON and Markdown formats
- Visualize game history through the dedicated viewer tabs



## Extending the System

### Adding Game Variations

While the system is primarily designed for the Prisoner's Dilemma, you can create variations by modifying the existing game configuration:

- Adjust the payoff values in the payoff matrix
- Change the number of rounds
- Modify the game rules description

To implement truly different games, significant code changes would be required in:
- `game_rules.py` - To handle different action structures
- `prompt_generator.py` - To create appropriate prompts for different game contexts
- `response_parser.py` - To parse different response formats
- `main_controller.py` - To implement different game flow logic

### Supporting New LLM Providers

To add a new LLM provider:
1. Update the `config/llm_providers.json` file with the provider details
2. Ensure the necessary API keys are set as environment variables
3. The system should automatically recognize and be able to use the new provider

## Important Limitations

This system was primarily designed to simulate the Prisoner's Dilemma game. While the framework suggests extensibility to other games, there are several architectural constraints:

1. The current implementation is tightly coupled to the binary choice structure (Cooperate/Defect) of the Prisoner's Dilemma
2. The payoff calculation logic expects specific action formats
3. The prompt templates are optimized for Prisoner's Dilemma scenarios
4. The UI components assume a specific game flow

Adding support for substantially different games (like Rock-Paper-Scissors or other formats) would require significant code modifications beyond simply adding new configuration files.

## Acknowledgments

This project was inspired by classic game theory concepts and recent advancements in large language models.