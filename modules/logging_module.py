import json
import os
import datetime

class LoggingModule:
    def __init__(self, log_directory='logs/'):
        self.log_directory = log_directory
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

    def start_game_log(self, game_name):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_id = f"{game_name}_{timestamp}_{id(self)}"
        self.current_log = os.path.join(self.log_directory, f"{log_id}.json")
        with open(self.current_log, 'w') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return log_id

    def log_round(self, round_data):
        with open(self.current_log, 'r+') as f:
            logs = json.load(f)
            logs.append(round_data)
            f.seek(0)
            json.dump(logs, f, ensure_ascii=False, indent=4)

    def save_log(self):
        print(f"Saving log: {self.current_log}")