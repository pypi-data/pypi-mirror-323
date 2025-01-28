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
import os
import tempfile
from unittest.mock import patch

from stellanow_cli.cli import cli


def test_configure_default_profile(runner, obj):
    with tempfile.TemporaryDirectory() as temp_dir:
        home_dir = os.path.join(temp_dir, "test_user")

        with patch("os.path.expanduser", return_value=home_dir):
            os.makedirs(os.path.join(home_dir, ".stellanow"), exist_ok=True)

            result = runner.invoke(
                cli,
                args=["configure", "code-generator-service"],
                input="https://example.com\ncustom_username\ncustom_password\na3fb6c97-b231-471e-8a5a-92a55f33ca5e\nf45cd487-7c98-4b72-a2da-c409f662b1e2\n",
                obj=obj,
            )

        config_file_path = os.path.join(home_dir, ".stellanow/config.ini")

        assert os.path.exists(config_file_path), "Config file was not created"
        assert result.exit_code == 0
        assert (
            "Configuration for profile 'DEFAULT' and service 'code-generator-service' saved successfully"
            in result.output
        )


def test_configure_custom_profile(runner, obj):
    with tempfile.TemporaryDirectory() as temp_dir:
        home_dir = os.path.join(temp_dir, "test_user")

        with patch("os.path.expanduser", return_value=home_dir):
            os.makedirs(os.path.join(home_dir, ".stellanow"), exist_ok=True)

            result = runner.invoke(
                cli,
                args=["--profile", "custom", "configure", "code-generator-service"],
                input="https://example.com\ncustom_username\ncustom_password\na3fb6c97-b231-471e-8a5a-92a55f33ca5e\nf45cd487-7c98-4b72-a2da-c409f662b1e2\n",
                obj=obj,
            )

        config_file_path = os.path.join(home_dir, ".stellanow/config.ini")

        assert os.path.exists(config_file_path), "Config file was not created"
        assert result.exit_code == 0
        assert (
            "Configuration for profile 'custom' and service 'code-generator-service' saved successfully"
            in result.output
        )
