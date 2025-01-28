"""client test module"""
import unittest
from aiman.core.classes import AIModel, Prompt, PromptOptions

class ClassesTest(unittest.TestCase):
    """_summary_

    Args:
        unittest (_type_): _description_
    """
    def test_model_class(self):
        """_summary_"""
        empty_model = AIModel()
        empty_model.from_dict({})
        self.assertEqual(empty_model.name, "")

        model = AIModel()
        result = model.from_dict({"name":"TEST"})
        self.assertEqual(result.name, "TEST")

        dict_model = model.to_dict()
        self.assertEqual(dict_model["name"], "TEST")

    def test_prompt_class(self):
        """_summary_"""
        prompt = Prompt()
        prompt.from_dict({})
        self.assertEqual(prompt.prompt, "")
        to_compare = "this is my prompt"
        prompt.from_dict({"prompt": to_compare})
        self.assertEqual(prompt.prompt, to_compare)
        prompt_dict = prompt.to_dict()
        self.assertEqual(prompt_dict["prompt"], to_compare)

    def test_prompt_options_class(self):
        """_summary_"""
        prompt_options = PromptOptions()
        self.assertEqual(prompt_options.mirostat, 0)
        self.assertEqual(prompt_options.mirostat_eta, 0.1)
        self.assertEqual(prompt_options.mirostat_tau, 5)
        self.assertEqual(prompt_options.raw, False)
        self.assertEqual(prompt_options.keep_context, True)

        po_dict  = prompt_options.to_dict()
        self.assertEqual(po_dict["mirostat"], 0)
        self.assertEqual(po_dict["mirostat_eta"], 0.1)
        self.assertEqual(po_dict["mirostat_tau"], 5)
        self.assertEqual(po_dict["raw"], False)
        self.assertEqual(po_dict["keep_context"], True)
