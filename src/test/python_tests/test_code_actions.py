# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Test for code actions over LSP.
"""

import os
from threading import Event

import pytest
from hamcrest import assert_that, is_

from .lsp_test_client import constants, session, utils

TEST_FILE_PATH = constants.TEST_DATA / "sample1" / "sample.py"
TEST_FILE_URI = utils.as_uri(str(TEST_FILE_PATH))
LINTER = utils.get_server_info_defaults()["name"]
TIMEOUT = 10  # 10 seconds


@pytest.mark.parametrize(
    ("code", "contents", "command"),
    [
        (
            "E201",
            "print ( 'Open parentheses should not have any space before or after them.')",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E202",
            "print('Closing parentheses should not have any whitespace before them.' )",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E203",
            "with open('file.dat') as f :\n\tcontents = f.read()",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E211",
            "with open ('file.dat') as f:\n\tcontents = f.read()",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E221",
            "doubled = 10  * 2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E222",
            "doubled = 10 *  2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E223",
            "a\t= 1",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E224",
            "a =\t1",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E225",
            "a=1",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E226",
            "a = 1+2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E226",
            "x = 128<<1",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E228",
            "remainder = 10%2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E231",
            "my_tuple = 1,2,3",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E241",
            "x = [1,   2]",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E251",
            "def func(key1 = 'val1', key2 = 'val2'):\n\treturn key1, key2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E242",
            "a,	b = 1, 2",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E261",
            "a = 1 # This comment needs an extra space",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E262",
            "a = 1  #This comment needs a space",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E265",
            "#This comment needs a space",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E266",
            "## There should be only one leading # for a block comment.",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E271",
            "from collections import    (namedtuple, defaultdict)",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E272",
            "from collections import (namedtuple, defaultdict)     ",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E273",
            "x = 1 in\t[1, 2, 3]",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E274",
            "x = 1\tin [1, 2, 3]",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
        (
            "E275",
            "from collections import(namedtuple, defaultdict)",
            {
                "title": f"{LINTER}: Run document formatting",
                "command": "editor.action.formatDocument",
            },
        ),
    ],
)
def test_command_code_action(code, contents, command):
    """Tests for code actions which run a command."""

    actual = []
    with utils.python_file(contents, TEST_FILE_PATH.parent) as temp_file:
        uri = utils.as_uri(os.fspath(temp_file))
        with session.LspSession() as ls_session:
            ls_session.initialize()

            done = Event()

            def _handler(params):
                nonlocal actual
                actual = params
                done.set()

            ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

            ls_session.notify_did_open(
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "python",
                        "version": 1,
                        "text": contents,
                    }
                }
            )

            # wait for some time to receive all notifications
            done.wait(TIMEOUT)

            diagnostics = [
                {
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 1, "character": 0},
                    },
                    "message": "",
                    "severity": 1,
                    "code": code,
                    "source": LINTER,
                }
            ]

            actual_code_actions = ls_session.text_document_code_action(
                {
                    "textDocument": {"uri": uri},
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 1, "character": 0},
                    },
                    "context": {"diagnostics": diagnostics},
                }
            )

            expected = {
                "title": command["title"],
                "kind": "quickfix",
                "diagnostics": diagnostics,
                "command": command,
            }

        assert_that(actual_code_actions, is_([expected]))
