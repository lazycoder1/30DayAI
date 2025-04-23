import re 

def remove_think_from_string(string: str) -> str:
    return re.sub(r"<think>.*?</think>\n?", "", string, flags=re.DOTALL)