import json
import os

# Ruta al archivo variables.json en node_modules/dualcode
def get_json_path():
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'node_modules', 'dualcode', 'variables.json')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo variables.json no se encontró en {file_path}")
    return file_path

def saveVar(variable, name=None):
    """Save a variable to variables.json in node_modules/dualcode."""
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        
        var_name = None
        for var, val in {**frame.f_locals, **frame.f_globals}.items():
            if val is variable:
                var_name = var
                break
        
        name = var_name or 'unnamed_variable'
    
    file_path = get_json_path()
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    data[name] = variable
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def deleteVar(name):
    """Delete a variable from variables.json in node_modules/dualcode."""
    file_path = get_json_path()
    
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
    """Return a dictionary of all variables in variables.json in node_modules/dualcode."""
    file_path = get_json_path()
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def getVar(name):
    """Retrieve a specific variable from variables.json in node_modules/dualcode."""
    file_path = get_json_path()
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise KeyError(f"No variable named '{name}' found")
    
    if name not in data:
        raise KeyError(f"No variable named '{name}' found")
    
    return data[name]
