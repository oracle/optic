from optic.common.helpers import prompt_question


class TestHelpers:
    def test_prompt_question(self, mocker):
        # Test 'y' input
        mocker.patch("builtins.input", return_value="y")
        assert prompt_question("Test question") is True

        # Test 'yes' input
        mocker.patch("builtins.input", return_value="yes")
        assert prompt_question("Test question") is True

        # Test 'n' input
        mocker.patch("builtins.input", return_value="n")
        assert prompt_question("Test question") is False

        # Test 'no' input
        mocker.patch("builtins.input", return_value="no")
        assert prompt_question("Test question") is False

        # Test invalid input
        mocker.patch("builtins.input", side_effect=["invalid", "y"])
        assert prompt_question("Test question") is True
