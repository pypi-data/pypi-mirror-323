import json
from typing import Dict

from ..types.hf_models import HFChatModels

def litechat_model(model:HFChatModels):
    return model

def litellm_model(model:HFChatModels):
    return f"openai/{model}"


def json_tag(response_format=None):
    if response_format:
        return f"\n strictly ONLY json with keys: \n\n{json.dumps(extract_data_structure(response_format), indent=2)}"
    else:
        return ""

def extract_data_structure(schema: str, definitions: Dict = None) -> Dict:
    if isinstance(schema, str):
        schema = json.loads(schema)
    """Extract expected data structure from a JSON schema"""
    if definitions is None:
        definitions = schema.get('$defs', {})

    result = {}
    properties = schema.get('properties', {})

    for field_name, field_info in properties.items():
        if field_info.get('type') == 'array':
            items = field_info.get('items', {})
            if '$ref' in items:
                # Get the definition name from the reference
                ref_name = items['$ref'].split('/')[-1]
                if ref_name in definitions:
                    result[field_name] = [extract_data_structure(definitions[ref_name], definitions)]
            else:
                result[field_name] = []
        elif field_info.get('type') == 'object':
            result[field_name] = extract_data_structure(field_info, definitions)
        else:
            # For simple types, just use empty string or appropriate default
            if field_info.get('type') == 'string':
                result[field_name] = ""
            elif field_info.get('type') == 'number':
                result[field_name] = 0
            elif field_info.get('type') == 'integer':
                result[field_name] = 0
            elif field_info.get('type') == 'boolean':
                result[field_name] = False
            else:
                result[field_name] = None

    return result