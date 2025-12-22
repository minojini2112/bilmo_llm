import json
from schemas import ProductList

def extract_and_validate(text: str):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        json_str = text[start:end]

        data = json.loads(json_str)
        validated = ProductList(**data)
        return True, validated.dict()

    except Exception as e:
        return False, {"error": str(e), "raw_output": text}
