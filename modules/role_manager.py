import json

class Role:
    def __init__(self, name, behavior, llm_config):
        self.name = name
        self.behavior = behavior
        self.llm_config = llm_config
        
    def __repr__(self):
        return f"Role(name='{self.name}', behavior='{self.behavior[:20]}...', llm_config={self.llm_config})"

class RoleManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        # Singleton pattern: Ensure only one RoleManager instance exists
        if not cls._instance:
            cls._instance = super(RoleManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self, roles_file='config/roles.json'):
        # Initialize only once
        if not self.initialized:
            self.roles = self.load_roles(roles_file)
            self.temp_roles = []
            self.initialized = True
            print(f"Loaded {len(self.roles)} roles: {[r.name for r in self.roles]}")

    def load_roles(self, roles_file):
        try:
            with open(roles_file, 'r') as f:
                roles_data = json.load(f)
            return [Role(r['name'], r['behavior'], r['llm_config']) for r in roles_data]
        except Exception as e:
            print(f"Error loading roles file: {e}")
            return []

    def get_role(self, name):
        # First check temporary roles
        for role in self.temp_roles:
            if role.name == name:
                print(f"Found in temporary roles: {name}")
                return role
            
        # Then check permanent roles
        for role in self.roles:
            if role.name == name:
                print(f"Found in permanent roles: {name}")
                return role
        
        print(f"Warning: Role '{name}' not found")
        print(f"Available roles: {[r.name for r in self.roles]}")
        print(f"Temporary roles: {[r.name for r in self.temp_roles]}")
        return None
    
    def add_temp_role(self, name, behavior, llm_config):
        """Add a temporary role"""
        try:
            # Ensure no role with the same name exists
            existing = self.get_role(name)
            if existing:
                print(f"Role with name '{name}' already exists, will be replaced")
                # Remove it if it's a temporary role
                self.temp_roles = [r for r in self.temp_roles if r.name != name]
            
            new_role = Role(name, behavior, llm_config)
            self.temp_roles.append(new_role)
            print(f"Added temporary role: {new_role}")
            return new_role
        except Exception as e:
            print(f"Error creating temporary role: {str(e)}")
            return None
    
    def clear_temp_roles(self):
        """Clear all temporary roles"""
        print(f"Clearing {len(self.temp_roles)} temporary roles")
        self.temp_roles = []