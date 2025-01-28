"""
Copyright (C) 2022-2024 Stella Technologies (UK) Limited.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List

from jinja2 import Environment, FileSystemLoader, Template
from stellanow_api_internals.datatypes.workflow_mgmt import StellaEventDetailed, StellaModelDetailed

GenerateMethodType = Callable[[Any, Dict[str, StellaModelDetailed], str], str]


class CodeGenerator:
    @staticmethod
    def load_template(language: str) -> Template:
        # Get the current file path
        current_file_path = Path(__file__).parent

        # Define the relative path to the templates directory
        templates_relative_path = Path("templates")

        # Get the absolute path to the templates directory
        templates_path = current_file_path / templates_relative_path

        # Create a Jinja2 environment with the FileSystemLoader
        env = Environment(loader=FileSystemLoader(templates_path))

        # Get the template
        template = env.get_template(f"{language}.template")

        return template

    @staticmethod
    def generate_message_class(
        event: StellaEventDetailed, model_details: Dict[str, StellaModelDetailed], **kwargs
    ) -> str:
        raise NotImplemented

    @staticmethod
    def generate_model_class(
        model: StellaModelDetailed, model_details: Dict[str, StellaModelDetailed], **kwargs
    ) -> str:
        raise NotImplemented

    @staticmethod
    def get_file_name_for_event_name(event_name: str) -> str:
        raise NotImplemented

    @staticmethod
    def get_file_name_for_model_name(event_name: str) -> str:
        raise NotImplemented

    @staticmethod
    def get_message_diff(
        event: StellaEventDetailed, existing_code: str, models_details: Dict[str, StellaModelDetailed]
    ) -> List[str]:
        raise NotImplemented

    @staticmethod
    def get_model_diff(
        model: StellaModelDetailed, existing_code: str, models_details: Dict[str, StellaModelDetailed]
    ) -> List[str]:
        raise NotImplemented
