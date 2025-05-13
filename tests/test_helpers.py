import pytest

from optic.common.helpers import prompt_question


class TestHelpers:
    @pytest.mark.parametrize(
        "keyboard_input, expected_result",
        [
            ("y", True),
            ("yes", True),
            (" yes       ", True),
            ("YES", True),
            ("    YES", True),
            ("YES        ", True),
            ("Yes", True),
            ("yEs", True),
            ("n", False),
            ("no", False),
            ("no         ", False),
            ("N", False),
            ("N   ", False),
            ("NO", False),
            ("       NO", False),
            ("nO", False),
            ("", False),
            ("       ", False),
        ],
    )
    def test_prompt_question(self, mocker, keyboard_input, expected_result):
        mocker.patch("builtins.input", return_value=keyboard_input)
        assert prompt_question("Test question True") is expected_result

    @pytest.mark.parametrize(
        "keyboard_input, default_response, expected_result",
        [
            ("", True, True),
            ("      ", True, True),
            ("", False, False),
            ("      ", False, False),
        ],
    )
    def test_prompt_question_default_value(
        self, mocker, keyboard_input, default_response, expected_result
    ):
        mocker.patch("builtins.input", return_value=keyboard_input)
        assert (
            prompt_question("Test question True", default_response) is expected_result
        )
