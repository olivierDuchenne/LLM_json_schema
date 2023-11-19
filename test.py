from LLM_constrained.LLM_json_schema.json_schema_constraint import auto_complete, end_token, find_string_end, find_number_end, find_boolean_end, find_array_end, find_object_end
import unittest

class TestAutoCompleteString(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(auto_complete("", {"type": "string"}), ['"'])

    def test_single_quote(self):
        self.assertEqual(auto_complete('"', {"type": "string"}), None)
        self.assertEqual(auto_complete(' "', {"type": "string"}), None)
        self.assertEqual(auto_complete('  "', {"type": "string"}), None)

    def test_quote_with_character(self):
        self.assertEqual(auto_complete('"a', {"type": "string"}), None)

    def test_quote_with_character_and_closing_quote(self):
        self.assertEqual(auto_complete('"a"', {"type": "string"}), [end_token])
        self.assertEqual(auto_complete('""', {"type": "string"}), [end_token])

    def test_quote_with_character_and_escaped_character(self):
        self.assertEqual(auto_complete('"a\\"5', {"type": "string"}), None)

class TestAutoCompleteNumber(unittest.TestCase):
    def test_empty_string(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', '.'])

    def test_single_digit(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("1", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'e', end_token])

    def test_negative_sign(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("-", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'])

    def test_positive_number(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("+2", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'e', end_token])

    def test_exponential_notation(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("3e", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-'])

    def test_negative_exponential_notation(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("4e-", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    def test_positive_exponential_notation(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("-8e4", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', end_token])

    def test_decimal_point(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("5.", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    def test_decimal_number(self):
        num_schema = {"type": "number"}
        self.assertEqual(auto_complete("5.2", num_schema), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'e', end_token])

class TestAutoCompleteBoolean(unittest.TestCase):
    def test_empty_string(self):
        bool_schema = {"type": "boolean"}
        self.assertEqual(auto_complete("", bool_schema), ['true'+end_token, 'false'+end_token])

    def test_true_string(self):
        bool_schema = {"type": "boolean"}
        self.assertEqual(auto_complete("true", bool_schema), [end_token])

    def test_false_string(self):
        bool_schema = {"type": "boolean"}
        self.assertEqual(auto_complete("false", bool_schema), [end_token])

    def test_partial_true_string(self):
        bool_schema = {"type": "boolean"}
        self.assertEqual(auto_complete("tr", bool_schema), ['ue'+end_token])

    def test_partial_false_string(self):
        bool_schema = {"type": "boolean"}
        self.assertEqual(auto_complete("fal", bool_schema), ['se'+end_token])

class TestFindStringEnd(unittest.TestCase):
    def test_find_string_end(self):
        self.assertEqual(find_string_end('"coucou"  '), 8)
        self.assertEqual(find_string_end('  "coucou"  '), 10)
        self.assertEqual(find_string_end('  coucou"  "'), None)
        self.assertEqual(find_string_end('"cou\\"cou"  '), 10)
        self.assertEqual(find_string_end('"cou\\ncou"  '), 10)
        self.assertEqual(find_string_end('"a", "b"'), 3)

class TestFindNumberEnd(unittest.TestCase):
    def test_find_number_end_empty_string(self):
        self.assertEqual(find_number_end(""), None)

    def test_find_number_end_positive_integer(self):
        self.assertEqual(find_number_end(" 1 "), 2)

    def test_find_number_end_negative_scientific_notation(self):
        self.assertEqual(find_number_end(" -12.4e+10 "), 10)

class TestFindBooleanEnd(unittest.TestCase):
    def test_find_boolean_end(self):
        self.assertEqual(find_boolean_end(" true "), 5)
        self.assertEqual(find_boolean_end(" tru "), None)

class TestFindArrayEnd(unittest.TestCase):
    def test_find_array_end(self):
        self.assertEqual(find_array_end(" [] "), 3)
        self.assertEqual(find_array_end(" [[]] "), 5)
        self.assertEqual(find_array_end(' ["]"] '), 6)
        self.assertEqual(find_array_end(' [{"a":["]"]}] '), 14)

class TestFindObjectEnd(unittest.TestCase):
    def test_find_object_end(self):
        self.assertEqual(find_object_end(" {} "), 3)
        self.assertEqual(find_object_end(" {{}} "), 5)
        self.assertEqual(find_object_end(' {"}"} '), 6)

class TestAutoCompleteArray(unittest.TestCase):
    def test_auto_complete(self):
        self.assertEqual(auto_complete("", {"type":"array", "items":{"type":"string"}}), ["["])
        self.assertEqual(auto_complete(" ", {"type":"array", "items":{"type":"string"}}), ["["])
        self.assertEqual(auto_complete("[", {"type":"array", "items":{"type":"string"}}), ['"'])
        self.assertEqual(auto_complete(" [", {"type":"array", "items":{"type":"string"}}), ['"'])
        self.assertEqual(auto_complete('["', {"type":"array", "items":{"type":"string"}}), None)
        self.assertEqual(auto_complete(' ["', {"type":"array", "items":{"type":"string"}}), None)
        self.assertEqual(auto_complete('["a"', {"type":"array", "items":{"type":"string"}}), [", ", "]"+end_token])
        self.assertEqual(auto_complete(' ["a"', {"type":"array", "items":{"type":"string"}}), [", ", "]"+end_token])
        self.assertEqual(auto_complete('["a", ', {"type":"array", "items":{"type":"string"}}), ['"'])
        self.assertEqual(auto_complete(' ["a", ', {"type":"array", "items":{"type":"string"}}), ['"'])
        self.assertEqual(auto_complete('[[', {"type":"array", "items":{"type":"array", "items":{"type":"string"}}}), ['"'])
        self.assertEqual(auto_complete(' [ [', {"type":"array", "items":{"type":"array", "items":{"type":"string"}}}), ['"'])
        self.assertEqual(auto_complete('["a", "a"', {"type":"array", "items":{"type":"string"}}), [", ", "]"+end_token])
        self.assertEqual(auto_complete(' ["a", "a"', {"type":"array", "items":{"type":"string"}}), [", ", "]"+end_token])

class TestAutoCompleteObject(unittest.TestCase):
    def test_auto_complete(self):
        self.assertEqual(auto_complete("", {"type":"object", "properties":{}}), ['{'])
        self.assertEqual(auto_complete("{", {"type":"object", "properties":{"coucou":{"type":"string"}}}), ['\n  "coucou": ', '}'+end_token])
        self.assertEqual(auto_complete('{"coucou":', {"type":"object", "properties":{"coucou":{"type":"string"}}}), ['"'])
        self.assertEqual(auto_complete('{"coucou":"a"', {"type":"object", "properties":{"coucou":{"type":"string"}}}), ['\n}'+end_token])
        self.assertEqual(auto_complete('{"coucou":"a"}', {"type":"object", "properties":{"coucou":{"type":"string"}}}), [end_token])
        self.assertEqual(auto_complete('{"coucou":"a", "caca":', {"type":"object", "properties":{"coucou":{"type":"string"}, "caca":{"type":"boolean"}}}), ['true', 'false'])
        self.assertEqual(auto_complete('{"coucou":"a", "caca":true', {"type":"object", "properties":{"coucou":{"type":"string"}, "caca":{"type":"boolean"}}}), ['\n}'+end_token])
        self.assertEqual(auto_complete('{"coucou":', {"type":"object", "properties":{"coucou":{"type":"object", "properties":{"caca": {"type":"boolean"}}}}}), ['{'])
        self.assertEqual(auto_complete('{"coucou":{', {"type":"object", "properties":{"coucou":{"type":"object", "properties":{"caca": {"type":"boolean"}}}}}), ['\n  "caca": ', '}'])
        self.assertEqual(auto_complete('{"coucou":{"caca":true', {"type":"object", "properties":{"coucou":{"type":"object", "properties":{"caca": {"type":"boolean"}}}}}), ['\n}'])


if __name__ == '__main__':
    unittest.main()