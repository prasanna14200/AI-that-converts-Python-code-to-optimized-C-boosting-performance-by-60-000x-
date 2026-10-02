import os
import unittest
from unittest.mock import Mock, patch

import app
from converter import build_prompt, clean_model_output


class ConverterTests(unittest.TestCase):
    def test_prompt_uses_python_to_cpp_direction(self):
        prompt = build_prompt("print('hello')")
        self.assertIn("Python code", prompt)
        self.assertIn("C++17", prompt)
        self.assertNotIn("Convert the following C++", prompt)

    def test_clean_model_output_removes_markdown_fence(self):
        cpp = clean_model_output("```cpp\n#include <iostream>\nint main(){}\n```")
        self.assertEqual(cpp, "#include <iostream>\nint main(){}")


class AppTests(unittest.TestCase):
    def setUp(self):
        app.app.config.update(TESTING=True)
        self.client = app.app.test_client()

    def test_healthz(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_empty_input(self):
        response = self.client.post("/api/convert", json={"code": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Enter Python code", response.get_json()["error"])

    def test_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post("/api/convert", json={"code": "print(1)"})
        self.assertEqual(response.status_code, 503)
        self.assertIn("GEMINI_API_KEY", response.get_json()["error"])

    @patch("converter.genai.Client")
    def test_successful_conversion(self, client_class):
        fake_client = Mock()
        fake_response = Mock()
        fake_response.text = "```cpp\n#include <iostream>\nint main(){std::cout << 1;}\n```"
        fake_client.models.generate_content.return_value = fake_response
        client_class.return_value = fake_client

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"}):
            response = self.client.post("/api/convert", json={"code": "print(1)"})

        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["direction"], "Python to C++")
        self.assertEqual(body["model"], "test-model")
        self.assertIn("#include <iostream>", body["cpp_code"])

    @patch("converter.genai.Client")
    def test_model_error(self, client_class):
        fake_client = Mock()
        fake_client.models.generate_content.side_effect = RuntimeError("rate limit")
        client_class.return_value = fake_client

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            response = self.client.post("/api/convert", json={"code": "print(1)"})

        self.assertEqual(response.status_code, 503)
        self.assertIn("Gemini conversion failed", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
