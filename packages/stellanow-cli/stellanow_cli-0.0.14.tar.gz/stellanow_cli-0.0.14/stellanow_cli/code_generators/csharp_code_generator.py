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

import difflib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from stellanow_api_internals.datatypes.workflow_mgmt import (
    StellaEntity,
    StellaEventDetailed,
    StellaField,
    StellaFieldType,
    StellaModelDetailed,
    StellaModelField,
)

from stellanow_cli.code_generators.code_generator import CodeGenerator
from stellanow_cli.core.enums import StellaDataStructure
from stellanow_cli.core.utils.string_utils import camel_to_snake, remove_comments, snake_to_camel, snake_to_lower_camel
from stellanow_cli.exceptions.cli_exceptions import (
    StellaNowCLINamespaceNotFoundException,
    StellaNowCLINoEntityAssociatedWithEventException,
)


def field_type_mapping(field: StellaField | StellaModelField, model_details: Dict[str, StellaModelDetailed]) -> str:
    if isinstance(field.fieldType, Dict):
        field_type = StellaFieldType(**field.fieldType)
    else:
        field_type = field.fieldType
    value_type = field_type.value
    if value_type == StellaDataStructure.MODEL:
        return f"{snake_to_camel(model_details[field_type.modelRef].name)}Model" if field_type.modelRef else "object"
    mapping = {
        "Decimal": "decimal",
        "Integer": "int",
        "Boolean": "bool",
        "String": "string",
        "Date": "DateOnly",
        "DateTime": "DateTime",
    }
    return mapping.get(value_type, "object")  # default to object if unknown


def field_format_mapping(value_type: str) -> str:
    mapping = {
        "Decimal": '.ToString("F2", CultureInfo.InvariantCulture)',
        "Integer": ".ToString()",
        "Boolean": ".ToString().ToLower()",
        "String": "",
        "Date": '.ToString("yyyy-MM-dd")',
        "DateTime": '.ToString("yyyy-MM-ddTHH:mm:ss.ffffffZ")',
    }
    return mapping.get(value_type, "")


def escape_reserved_words(word: str) -> str:
    reserved_words = [
        "abstract",
        "as",
        "base",
        "bool",
        "break",
        "byte",
        "case",
        "catch",
        "char",
        "checked",
        "class",
        "const",
        "continue",
        "decimal",
        "default",
        "delegate",
        "do",
        "double",
        "else",
        "enum",
        "event",
        "explicit",
        "extern",
        "false",
        "finally",
        "fixed",
        "float",
        "for",
        "foreach",
        "goto",
        "if",
        "implicit",
        "in",
        "int",
        "interface",
        "internal",
        "is",
        "lock",
        "long",
        "namespace",
        "new",
        "null",
        "object",
        "operator",
        "out",
        "override",
        "params",
        "private",
        "protected",
        "public",
        "readonly",
        "ref",
        "return",
        "sbyte",
        "sealed",
        "short",
        "sizeof",
        "stackalloc",
        "static",
        "string",
        "struct",
        "switch",
        "this",
        "throw",
        "true",
        "try",
        "typeof",
        "uint",
        "ulong",
        "unchecked",
        "unsafe",
        "ushort",
        "using",
        "virtual",
        "void",
        "volatile",
        "while",
    ]

    return f"{word}_" if word in reserved_words else word


@dataclass
class CSharpField:
    original_name: str
    csharp_name: str
    type: str
    is_model: bool

    @classmethod
    def from_stella_field(cls, field: StellaField | StellaModelField, model_details: Dict[str, StellaModelDetailed]):
        field_type = field_type_mapping(field, model_details)
        is_model = field_type.endswith("Model")
        return cls(
            original_name=field.name,
            csharp_name=escape_reserved_words(snake_to_camel(camel_to_snake(field.name))),
            type=field_type,
            is_model=is_model,
        )

    def to_constructor_parameter_declaration(self):
        return f"{self.type} {self.csharp_name}"


@dataclass
class CSharpEntity:
    original_name: str
    csharp_name: str

    @classmethod
    def from_stella_field(cls, entity: StellaEntity):
        return cls(
            original_name=entity.name,
            csharp_name=escape_reserved_words(snake_to_lower_camel(entity.name)) + "Id",
        )

    def to_entity_type_declaration(self):
        return f'new EntityType("{self.original_name}", {self.csharp_name})'

    def to_constructor_parameter_declaration(self):
        return f"string {self.csharp_name}"


@dataclass
class CSharpModel:
    original_name: str
    csharp_name: str


class CsharpCodeGenerator(CodeGenerator):
    @staticmethod
    def generate_message_class(
        event: StellaEventDetailed, model_details: Dict[str, StellaModelDetailed], **kwargs
    ) -> str:
        template = CsharpCodeGenerator.load_template("messages/csharp")

        namespace = kwargs.get("namespace", "StellaNowSDK.Messages")

        fields = [CSharpField.from_stella_field(field=field, model_details=model_details) for field in event.fields]
        entities = [CSharpEntity.from_stella_field(entity) for entity in event.entities]
        if not entities:
            raise StellaNowCLINoEntityAssociatedWithEventException()

        has_model_fields = any(field.type.endswith("Model") for field in fields)

        rendered = template.render(
            className=snake_to_camel(event.name),
            eventName=event.name,
            constructorArguments=", ".join(
                [
                    ", ".join([entity.to_constructor_parameter_declaration() for entity in entities]),
                    ", ".join([field.to_constructor_parameter_declaration() for field in fields]),
                ]
            ),
            entitiesList=", ".join([entity.to_entity_type_declaration() for entity in entities]),
            entities=entities,
            fields=fields,
            namespace=namespace,
            has_model_fields=has_model_fields,
            eventJson=json.dumps(event.model_dump(), indent=4),
            eventId=event.id,
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        return rendered

    @staticmethod
    def generate_model_class(
        model: StellaModelDetailed, model_details: Dict[str, StellaModelDetailed], **kwargs
    ) -> str:
        template = CsharpCodeGenerator.load_template("models/csharp")

        namespace = kwargs.get("namespace", "StellaNowSDK.Messages")

        fields = [
            CSharpField.from_stella_field(field=field, model_details=model_details) for field in model.fields.root
        ]

        rendered = template.render(
            className=snake_to_camel(model.name),
            fields=fields,
            namespace=namespace,
            modelJson=json.dumps(model.model_dump(), indent=4),
            modelId=model.id,
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        return rendered

    @staticmethod
    def get_file_name_for_event_name(event_name: str) -> str:
        return f"{snake_to_camel(event_name)}Message.cs"

    @staticmethod
    def get_file_name_for_model_name(model_name: str) -> str:
        return f"{snake_to_camel(model_name)}Model.cs"

    @classmethod
    def _get_diff(
        cls, generate_method, item, existing_code: str, models_details: Dict[str, StellaModelDetailed]
    ) -> List[str]:
        namespace_search = re.search(r"namespace (.*);", existing_code)
        if namespace_search is None:
            raise StellaNowCLINamespaceNotFoundException()

        namespace = namespace_search.group(1)

        new_code = generate_method(item, models_details, namespace=namespace)

        existing_code_no_comments = remove_comments(existing_code)
        new_code_no_comments = remove_comments(new_code)

        diff = difflib.unified_diff(
            existing_code_no_comments.splitlines(keepends=True), new_code_no_comments.splitlines(keepends=True)
        )

        return [
            line
            for line in diff
            if line.startswith("- ") or line.startswith("+ ") and not (line.startswith("---") or line.startswith("+++"))
        ]

    @classmethod
    def get_message_diff(
        cls, event: StellaEventDetailed, existing_code: str, models_details: Dict[str, StellaModelDetailed]
    ) -> List[str]:
        return cls._get_diff(cls.generate_message_class, event, existing_code, models_details)

    @classmethod
    def get_model_diff(
        cls, model: StellaModelDetailed, existing_code: str, models_details: Dict[str, StellaModelDetailed]
    ) -> List[str]:
        return cls._get_diff(cls.generate_model_class, model, existing_code, models_details)
