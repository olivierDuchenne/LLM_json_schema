from typing import Union, List
import json_schema_constraint

end_token = json_schema_constraint.end_token

class Constrainer:
    """
    This is the base class for all constrainers. 
    A constrainer is an object that can compute a completion (suggestions) for an incomplete string.
    """
    def compute_completion(self, incomplete_string: str) -> Union[str, List[str], None]:
        raise NotImplementedError()

class JsonSchemaConstrainer:
    """
    This is a class for constraining JSON schemas. 
    A JsonSchemaConstrainer is an object that can compute a completion (suggestions) for an incomplete string based on a given JSON schema.
    """
    def __init__(self, json_schema):
        self.json_schema = json_schema
    def compute_completion(self, incomplete_string: str) -> Union[str, List[str], None]:
        return json_schema_constraint.auto_complete(incomplete_string, self.json_schema)
    

