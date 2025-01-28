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

import glob
import os
from typing import List

import click
from loguru import logger

from stellanow_cli.code_generators import CsharpCodeGenerator
from stellanow_cli.core.helpers import SkippedFile
from stellanow_cli.core.utils.logger_utils import log_summary
from stellanow_cli.core.validators import uuid_validator
from stellanow_cli.services.code_generator.code_generator import CodeGeneratorService, pass_code_generator_service
from stellanow_cli.services.code_generator.tools import process_file


@click.command()
@click.option(
    "--project_id",
    "-p",
    required=True,
    prompt=True,
    callback=uuid_validator,
    help="UUID of the project associated with the organization saved in your configuration file.",
)
@click.option("--input_dir", "-i", default=".", help="The directory to read generated classes from.")
@pass_code_generator_service
def plan(service: CodeGeneratorService, project_id: str, input_dir: str, **kwargs):
    """Compares currently generated classes with the specifications fetched from the API and provides a summary of
    changes."""
    logger.info("Planning...")

    workflow_client = service.create_workflow_client(project_id=project_id)
    generators = {".cs": CsharpCodeGenerator()}
    skipped_files: List[SkippedFile] = []
    files_found = 0

    for filename in glob.iglob(f"{input_dir}/**", recursive=True):
        if os.path.isdir(filename):
            continue

        _, ext = os.path.splitext(filename)
        if ext not in generators:
            continue

        files_found += 1
        generator = generators[ext]

        logger.info(f"==============================\nComparison for file: {filename}")
        reasons = process_file(filename=filename, workflow_client=workflow_client, generator=generator)
        if reasons:
            skipped_files.append(SkippedFile(filename, ", ".join(reasons)))

    if files_found == 0:
        logger.warning("No recognized files found to process. Nothing to plan.")
        return

    log_summary(skipped_files)


plan_cmd = plan
