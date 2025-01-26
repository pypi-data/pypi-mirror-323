import json
import os

def saveVar(variable, name=None):
    """Save a variable to variables.json."""
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        
        var_name = None
        for var, val in {**frame.f_locals, **frame.f_globals}.items():
            if val is variable:
                var_name = var
                break
        
        name = var_name or 'unnamed_variable'
    
    file_path = os.path.join(os.getcwd(), 'variables.json')
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    data[name] = variable
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def deleteVar(name):
    """Delete a variable from variables.json."""
    file_path = os.path.join(os.getcwd(), 'variables.json')
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    
    if name in data:
        del data[name]
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

def seeAllVar():
    """Return a dictionary of all variables in variables.json."""
    file_path = os.path.join(os.getcwd(), 'variables.json')
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def getVar(name):
    """Retrieve a specific variable from variables.json."""
    file_path = os.path.join(os.getcwd(), 'variables.json')
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise KeyError(f"No variable named '{name}' found")
    
    if name not in data:
        raise KeyError(f"No variable named '{name}' found")
    
    return data[name]