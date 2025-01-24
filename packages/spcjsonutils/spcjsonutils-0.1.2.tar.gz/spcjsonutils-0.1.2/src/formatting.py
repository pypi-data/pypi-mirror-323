import json

def pPrintJson(data):
    """
    Prints JSON/dictionary data in a formatted way.
    
    Args:
        data (dict or str): JSON data or dictionary to print
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            print("Invalid JSON string")
            return
    
    print(json.dumps(data, indent=4, sort_keys=True))