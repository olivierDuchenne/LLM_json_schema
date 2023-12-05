import re
from typing import Union
from enum import Enum

end_token = "\0"

class EarlyEndOfValue(Exception):
    def __init__(self, index):
        self.index = index

ongoing_string_regexp = re.compile(r'^(?!.*(?<!\\)").*$')

def auto_complete_string(incomplete_string: str):
    if len(incomplete_string)==0:
        return ['"']
    first_quote_match = re.search(r'^\s*"', incomplete_string)
    if first_quote_match and len(incomplete_string)>first_quote_match.end() and incomplete_string[-1]=='"' and incomplete_string[-2]!="\\":
        return [end_token]
    else: return [ongoing_string_regexp]

def auto_complete_number(incomplete_string):
    suggestions = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    if len(incomplete_string)==0 or incomplete_string[-1]=="e":
        suggestions.append("+")
        suggestions.append("-")
    if "." not in incomplete_string and "e" not in incomplete_string:
        suggestions.append(".")
    if len(incomplete_string)>0 and incomplete_string[-1].isdigit() and "e" not in incomplete_string:
        suggestions.append("e")
    if len(incomplete_string)>0 and incomplete_string[-1].isdigit():
        suggestions.append(end_token)
    return suggestions

def auto_complete_boolean(incomplete_string: str):
    if len(incomplete_string)==0:
        return ["true"+end_token, "false"+end_token]
    elif incomplete_string.startswith("t"):
        return [("true"+end_token)[len(incomplete_string):]]
    elif incomplete_string.startswith("f"):
        return [("false"+end_token)[len(incomplete_string):]]

def auto_complete_array(incomplete_string:str, items):
    if re.match(r'^\s*$', incomplete_string):
        return ["["]
    current_item_completions = []
    bracket_index = re.search(r'\s*\[', incomplete_string)
    if bracket_index:
        ind = bracket_index.end()
    while True:
        item_end = find_value_end(incomplete_string[ind:], items)
        if isinstance(item_end, ValueEndSymbol):
            item_completions = auto_complete(incomplete_string[ind:], items)
            if item_completions is None:
                return None
            # remove the end token, because we also need to close the object "}" before ending
            item_completions = [c for c in item_completions if c!=end_token]
            item_completions = [c.replace(end_token, "") if type(c)is str else c for c in item_completions]
            if item_end == END_NOT_REACHED:
                return item_completions
            if item_end == CAN_END_OR_CONTINUE:
                current_item_completions = item_completions
            item_end = len(incomplete_string[ind:])
        match = re.search(r'^\s*,\s*', incomplete_string[ind+item_end:])
        if match:
            ind += item_end + match.end()
        else:
            return [", ", "]"+end_token, *current_item_completions]

def auto_complete_object(incomplete_string:str, properties: dict):
    if len(incomplete_string)==0:
        return ["{"]
    current_item_completions = []
    bracket_index = re.search(r'\s*\{', incomplete_string)
    if bracket_index:
        first_bracket_ind = bracket_index.end()
        ind = first_bracket_ind
    for property, val_type in properties.items():
        pattern = f'"{property}":'
        sanitized_pattern = re.escape(pattern)
        match = re.search(r'^\s*,?\s*' + sanitized_pattern, incomplete_string[ind:])
        if match:
            ind += match.end()
        else:
            if ind==first_bracket_ind:
                completion = pattern
            else:
                if re.search(r",\s*$", incomplete_string):
                    completion = pattern
                else:
                    completion = ", "+pattern
            # return [completion, "}"+end_token]
            return [completion, *current_item_completions]
        item_end = find_value_end(incomplete_string[ind:], val_type)
        if isinstance(item_end, ValueEndSymbol):
            item_completions = auto_complete(incomplete_string[ind:], val_type)
            if item_completions is None:
                return None
            # remove the end token, because we also need to close the object "}" before ending
            item_completions = [c for c in item_completions if c!=end_token]
            item_completions = [c.replace(end_token, "") if type(c)is str else c for c in item_completions]
            if item_end == END_NOT_REACHED:
                return item_completions
            if item_end == CAN_END_OR_CONTINUE:
                current_item_completions = item_completions
            item_end = len(incomplete_string[ind:])
        ind += item_end
    match = re.search(r'^\s*}\s*', incomplete_string[ind:])
    if match:
        return [end_token, *current_item_completions]    
    return ["}"+end_token, *current_item_completions]

def auto_complete(incomplete_string, json_schema):
    """
    This function auto completes the incomplete string based on the json schema provided.

    Parameters:
    incomplete_string (str): The string that needs to be auto completed.
    json_schema (dict): The JSON schema to enforce.

    Returns:
    list: List of possible completions.
    """
    if json_schema["type"] == "string":
        return auto_complete_string(incomplete_string)
    elif json_schema["type"] == "number":
        return auto_complete_number(incomplete_string)
    elif json_schema["type"] == "boolean":
        return auto_complete_boolean(incomplete_string)
    elif json_schema["type"] == "object":
        return auto_complete_object(incomplete_string, json_schema["properties"])
    elif json_schema["type"] == "array":
        return auto_complete_array(incomplete_string, json_schema["items"])
    else:
        raise Exception(f"""Unknown type: '{json_schema["type"]}'""")

class ValueEndSymbol(Enum):
    END_NOT_REACHED = "END_NOT_REACHED"
    CAN_END_OR_CONTINUE = "CAN_END_OR_CONTINUE"

END_NOT_REACHED = ValueEndSymbol.END_NOT_REACHED
CAN_END_OR_CONTINUE = ValueEndSymbol.CAN_END_OR_CONTINUE

def find_string_end(incomplete_string:str) -> Union[int, ValueEndSymbol]:
    match = re.search(r'^\s*"(?:[^"\\]|\\.)*"', incomplete_string)
    if match:
        return match.end()
    else:
        return END_NOT_REACHED

def find_number_end(incomplete_string:str) -> Union[int, ValueEndSymbol]:
    match = re.search(r'^\s*-?\d+(\.\d+)?([eE][+-]?\d+)?', incomplete_string)
    if match:
        end = match.end()
        if end == len(incomplete_string):
            return CAN_END_OR_CONTINUE
        else:
            return match.end()
    else:
        return END_NOT_REACHED

def find_boolean_end(incomplete_string:str) -> Union[int, ValueEndSymbol]:
    match = re.search(r'^\s*(true|false)', incomplete_string)
    if match:
        return match.end()
    else:
        return END_NOT_REACHED

def find_array_end(incomplete_string:str) -> Union[int, ValueEndSymbol]:
    depth = 0
    in_quotes = False
    for i, c in enumerate(incomplete_string):
        if c == '"' and (i == 0 or incomplete_string[i-1] != '\\'):
            in_quotes = not in_quotes
        elif not in_quotes:
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return i + 1
    return END_NOT_REACHED

def find_object_end(incomplete_string:str) -> Union[int, ValueEndSymbol]:
    depth = 0
    in_quotes = False
    for i, c in enumerate(incomplete_string):
        if c == '"' and (i == 0 or incomplete_string[i-1] != '\\'):
            in_quotes = not in_quotes
        elif not in_quotes:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return i + 1
    return END_NOT_REACHED

def find_value_end(incomplete_string:str, json_schema) -> Union[int, ValueEndSymbol]:
    """
    This function finds the end index of a value in a JSON string based on the provided JSON schema.
    It uses the type of the value specified in the schema to call the appropriate function to find the end of the value.
    
    Parameters:
    incomplete_string (str): The truncated JSON string in which to find the end of the value.
    json_schema (dict): The JSON schema that specifies the type of the value.
    
    Returns:
    Union[int, None]: The index of the end of the value in the JSON string,
    or END_NOT_REACHED if the end could not be found because the value is truncated,
    or CAN_END_OR_CONTINUE if the value could stop there or continue: ex: 123 could be a finished number or the beginning of a longer number 1234.
    """
    if json_schema['type'] == 'string':
        return find_string_end(incomplete_string)
    elif json_schema['type'] == 'number':
        return find_number_end(incomplete_string)
    elif json_schema['type'] == 'boolean':
        return find_boolean_end(incomplete_string)
    elif json_schema['type'] == 'array':
        return find_array_end(incomplete_string)
    elif json_schema['type'] == 'object':
        return find_object_end(incomplete_string)



if __name__ == '__main__':
    res = auto_complete("[", {"type":"array", "items":{"type":"string"}})
    # res = auto_complete("", {"type":"string"})
    print(res)

