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
import uuid
from datetime import datetime

import pytest
from loguru import logger
from stellanow_api_internals.datatypes.workflow_mgmt import (
    StellaEventDetailed,
    StellaField,
    StellaFieldType,
    StellaModelDetailed,
    StellaModelField,
    StellaModelFieldType,
    StellaShortEntity,
)

from stellanow_cli.code_generators import CsharpCodeGenerator


@pytest.fixture
def test_event():
    return StellaEventDetailed(
        id="1",
        name="test_event",
        projectId=str(uuid.uuid4()),
        entities=[
            StellaShortEntity(id="", name="entity1"),
            StellaShortEntity(id="", name="entity2"),
        ],
        fields=[
            StellaField(id="", name="field1", fieldType=StellaFieldType(value="Decimal"), required=True),
            StellaField(id="", name="field2", fieldType=StellaFieldType(value="Integer"), required=True),
            StellaField(id="", name="fieldValue3", fieldType=StellaFieldType(value="Boolean"), required=True),
            StellaField(id="", name="field4", fieldType=StellaFieldType(value="String"), required=True),
            StellaField(id="", name="field5", fieldType=StellaFieldType(value="Date"), required=True),
            StellaField(id="", name="field6", fieldType=StellaFieldType(value="DateTime"), required=True),
            StellaField(id="", name="field7", fieldType=StellaFieldType(value="Any"), required=True),
            StellaField(
                id="",
                name="field8",
                fieldType=StellaFieldType(value="Model", modelRef="34a736ed-0b51-415a-ac24-0c6a975e9381"),
                required=True,
            ),
        ],
        isActive=True,
        createdAt=datetime(2022, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
        updatedAt=datetime(2022, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
        description="Test event",
    )


@pytest.fixture
def test_event_without_model():
    return StellaEventDetailed(
        id="2",
        name="test_event_no_model",
        projectId=str(uuid.uuid4()),
        entities=[
            StellaShortEntity(id="", name="entity1"),
            StellaShortEntity(id="", name="entity2"),
        ],
        fields=[
            StellaField(id="", name="field1", fieldType=StellaFieldType(value="Decimal"), required=True),
            StellaField(id="", name="field2", fieldType=StellaFieldType(value="Integer"), required=True),
            StellaField(id="", name="fieldValue3", fieldType=StellaFieldType(value="Boolean"), required=True),
            StellaField(id="", name="field4", fieldType=StellaFieldType(value="String"), required=True),
            StellaField(id="", name="field5", fieldType=StellaFieldType(value="Date"), required=True),
            StellaField(id="", name="field6", fieldType=StellaFieldType(value="DateTime"), required=True),
            StellaField(id="", name="field7", fieldType=StellaFieldType(value="Any"), required=True),
        ],
        isActive=True,
        createdAt=datetime(2022, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
        updatedAt=datetime(2022, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
        description="Test event without model",
    )


@pytest.fixture
def model_details():
    return {
        "34a736ed-0b51-415a-ac24-0c6a975e9381": StellaModelDetailed(
            id="34a736ed-0b51-415a-ac24-0c6a975e9381",
            name="TestStructure",
            description="A test model",
            createdAt=datetime(2022, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
            updatedAt=datetime(2022, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
            fields=[
                StellaModelField(
                    id="fieldA",
                    modelId="34a736ed-0b51-415a-ac24-0c6a975e9381",
                    name="fieldA",
                    fieldType=StellaModelFieldType(value="String"),
                ),
                StellaModelField(
                    id="fieldB",
                    modelId="34a736ed-0b51-415a-ac24-0c6a975e9381",
                    name="fieldB",
                    fieldType=StellaModelFieldType(value="Integer"),
                ),
            ],
        ),
        "66a744ed-0b32-125a-ac24-0c6a525e9381": StellaModelDetailed(
            id="66a744ed-0b32-125a-ac24-0c6a525e9381",
            name="TestNested",
            description="A test model",
            createdAt=datetime(2022, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
            updatedAt=datetime(2022, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
            fields=[
                StellaModelField(
                    id="fieldC",
                    modelId="66a744ed-0b32-125a-ac24-0c6a525e9381",
                    name="fieldC",
                    fieldType=StellaModelFieldType(value="String"),
                ),
                StellaModelField(
                    id="fieldD",
                    modelId="66a744ed-0b32-125a-ac24-0c6a525e9381",
                    name="fieldD",
                    fieldType=StellaModelFieldType(value="Model", modelRef="87a324ed-0b21-655a-ac24-0c6a755e9381"),
                ),
            ],
        ),
        "87a324ed-0b21-655a-ac24-0c6a755e9381": StellaModelDetailed(
            id="87a324ed-0b21-655a-ac24-0c6a755e9381",
            name="TestAnother",
            description="A test model",
            createdAt=datetime(2022, 1, 1).strftime("%Y-%m-%dT%H:%M:%S"),
            updatedAt=datetime(2022, 1, 2).strftime("%Y-%m-%dT%H:%M:%S"),
            fields=[
                StellaModelField(
                    id="fieldE",
                    modelId="87a324ed-0b21-655a-ac24-0c6a755e9381",
                    name="fieldE",
                    fieldType=StellaModelFieldType(value="String"),
                ),
                StellaModelField(
                    id="fieldF",
                    modelId="87a324ed-0b21-655a-ac24-0c6a755e9381",
                    name="fieldF",
                    fieldType=StellaModelFieldType(value="Integer"),
                ),
            ],
        ),
    }


@pytest.fixture
def model_details_empty():
    return {}


def test_generate_class_handles_all_valueTypes(test_event, model_details):
    # Generate the class
    generated_class = CsharpCodeGenerator.generate_message_class(test_event, model_details)
    logger.info(generated_class)

    # Assertions
    assert "/*\n *  This file is auto-generated by StellaNowCLI. DO NOT EDIT.\n *\n *" in generated_class
    assert "using StellaNowSDK.Messages;" in generated_class
    assert "using StellaNowSDK.Messages.Models;" in generated_class
    assert "namespace StellaNowSDK.Messages;" in generated_class
    assert "[property: Newtonsoft.Json.JsonIgnore] string entity1Id," in generated_class
    assert "[property: Newtonsoft.Json.JsonIgnore] string entity2Id," in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field1")] decimal Field1,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field2")] int Field2,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("fieldValue3")] bool FieldValue3,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field4")] string Field4,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field4")] string Field4,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field5")] DateOnly Field5,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field6")] DateTime Field6' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field7")] object Field7' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field8")] TeststructureModel Field8' in generated_class
    assert (
        ') : StellaNowMessageBase("test_event", new List<EntityType>{ new EntityType("entity1", entity1Id), new EntityType("entity2", entity2Id) });'
        in generated_class
    )


def test_generate_model_class(model_details):
    model_id = "34a736ed-0b51-415a-ac24-0c6a975e9381"
    model = model_details[model_id]

    # Generate the model class
    generated_model_class = CsharpCodeGenerator.generate_model_class(model, model_details)

    # Assertions
    assert f"public record TeststructureModel" in generated_model_class
    assert '[property: Newtonsoft.Json.JsonProperty("fieldA")] string FieldA,' in generated_model_class
    assert '[property: Newtonsoft.Json.JsonProperty("fieldB")] int FieldB' in generated_model_class


def test_generate_nested_model_class(model_details):
    model_id = "66a744ed-0b32-125a-ac24-0c6a525e9381"
    model = model_details[model_id]

    # Generate the model class
    generated_model_class = CsharpCodeGenerator.generate_model_class(model, model_details)

    # Assertions
    assert "using StellaNowSDK.Messages;" not in generated_model_class
    assert "using StellaNowSDK.Messages.Models;" not in generated_model_class
    assert "namespace StellaNowSDK.Messages.Models;" in generated_model_class
    assert f"public record TestnestedModel(" in generated_model_class
    assert '[property: Newtonsoft.Json.JsonProperty("fieldC")] string FieldC,' in generated_model_class
    assert '[property: Newtonsoft.Json.JsonProperty("fieldD")] TestanotherModel FieldD' in generated_model_class


def test_generate_empty_model_class(test_event_without_model, model_details_empty):
    generated_class = CsharpCodeGenerator.generate_message_class(test_event_without_model, model_details_empty)

    assert "using StellaNowSDK.Messages;" in generated_class
    assert "using StellaNowSDK.Messages.Models;" not in generated_class
    assert "namespace StellaNowSDK.Messages;" in generated_class
    assert "[property: Newtonsoft.Json.JsonIgnore] string entity1Id," in generated_class
    assert "[property: Newtonsoft.Json.JsonIgnore] string entity2Id," in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field1")] decimal Field1,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field2")] int Field2,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("fieldValue3")] bool FieldValue3,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field4")] string Field4,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field4")] string Field4,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field5")] DateOnly Field5,' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field6")] DateTime Field6' in generated_class
    assert '[property: Newtonsoft.Json.JsonProperty("field7")] object Field7' in generated_class
    assert (
        ') : StellaNowMessageBase("test_event_no_model", new List<EntityType>{ new EntityType("entity1", entity1Id), new EntityType("entity2", entity2Id) });'
        in generated_class
    )
