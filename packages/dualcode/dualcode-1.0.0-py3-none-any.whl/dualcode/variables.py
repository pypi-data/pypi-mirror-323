import json
import os

def saveVar(variables):
    try:
        if os.path.exists('variables.json'):
            with open('variables.json', 'r', encoding='utf-8') as file:
                json_data = json.load(file)
        else:
            json_data = {}

        json_data.update(variables)

        with open('variables.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)

        print(f"Variables saved successfully")
    except Exception as e:
        print(f"Error saving variables: {e}")

def deleteVar(variable):
    try:
        if os.path.exists('variables.json'):
            with open('variables.json', 'r', encoding='utf-8') as file:
                json_data = json.load(file)
        else:
            print("No variables defined (file does not exist).")
            return

        variable_name = variable if isinstance(variable, str) else list(variable.keys())[0]

        if variable_name in json_data:
            del json_data[variable_name]
            print(f"Variable '{variable_name}' deleted successfully")
        else:
            print(f"Variable '{variable_name}' does not exist.")
            return

        with open('variables.json', 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error deleting variable: {e}")

def seeAllVars():
    try:
        if os.path.exists('variables.json'):
            with open('variables.json', 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                print("All variables:", json_data)
                return json_data
        else:
            print("No variables defined (file does not exist).")
            return {}
    except Exception as e:
        print(f"Error reading variables: {e}")
        return {}

def getVar(variable_name):
    try:
        if os.path.exists('variables.json'):
            with open('variables.json', 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            if variable_name in json_data:
                return json_data[variable_name]
            else:
                print(f"Variable '{variable_name}' does not exist.")
                return None
        else:
            print("No variables defined (file does not exist).")
            return None
    except Exception as e:
        print(f"Error reading variable: {e}")
        return None
