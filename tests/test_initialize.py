import os

import pytest

from optic.initialize import initialize_service
from optic.initialize.initialize_service import (
    OPTIC_COLOR,
    configure_shell_to_use_completion,
    get_shell_env,
    initialize_optic,
    setup_cluster_config,
    setup_settings,
    setup_shell_completion,
    validate_file_exists,
)


@pytest.fixture
def mock_shell_complete_file_path_bash(temp_dir):
    os.system(  # noqa: S605, S607
        f"_OPTIC_COMPLETE=bash_source optic > {temp_dir}/.optic-complete.bash"
    )
    return f"{temp_dir}/.optic-complete.bash"


@pytest.fixture
def mock_shell_complete_file_path_zsh(temp_dir):
    os.system(  # noqa: S605, S607
        f"_OPTIC_COMPLETE=zsh_source optic > {temp_dir}/.optic-complete.zsh"
    )
    return f"{temp_dir}/.optic-complete.zsh"


@pytest.fixture
def mock_shell_configuration_file_path(temp_dir):
    mock_shell_configuration_file_path = f"{temp_dir}/.zshrc"
    with open(mock_shell_configuration_file_path, "w") as f:
        f.write("#Mocked shell configuration file")

    return mock_shell_configuration_file_path


class TestInitialize:

    def test_initialize_optic(self, mocker):
        # Mock setup_cluster_config, setup_settings, and setup_shell_completion
        mock_setup_cluster_config = mocker.patch(
            "optic.initialize.initialize_service.setup_cluster_config"
        )
        mock_setup_settings = mocker.patch(
            "optic.initialize.initialize_service.setup_settings"
        )
        mock_setup_shell_completion = mocker.patch(
            "optic.initialize.initialize_service.setup_shell_completion"
        )

        initialize_optic()

        # Check if the mocked functions were called
        mock_setup_cluster_config.assert_called_once()
        mock_setup_settings.assert_called_once()
        mock_setup_shell_completion.assert_called_once()

    def test_setup_cluster_config_file_create(self, mocker, temp_dir):
        mock_dir = f"{temp_dir}/optic"
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", mock_dir)

        # Mock "Y" input
        mocker.patch(
            "optic.initialize.initialize_service.prompt_question", return_value=True
        )

        setup_cluster_config()

        # Assert cluster_config file was created
        assert validate_file_exists(f"{mock_dir}/cluster-config.yaml")

    def test_setup_cluster_config_file_exists(
        self, mocker, cluster_config_file_path, temp_dir, capsys
    ):
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", temp_dir)

        setup_cluster_config()

        captured = capsys.readouterr()
        assert (
            f"Cluster configuration file: {OPTIC_COLOR.OK_CYAN}{cluster_config_file_path}{OPTIC_COLOR.STOP} "
            "already exists" in captured.out
        )

    def test_setup_settings_file_create(self, mocker, temp_dir):
        mock_dir = f"{temp_dir}/optic"
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", mock_dir)

        # Mock "Y" input
        mocker.patch(
            "optic.initialize.initialize_service.prompt_question", return_value=True
        )

        setup_settings()

        # Assert settings file was created
        assert validate_file_exists(f"{mock_dir}/optic-settings.yaml")

    def test_setup_settings_file_exists(
        self, mocker, optic_settings_file_path, temp_dir, capsys
    ):
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", temp_dir)

        setup_settings()

        captured = capsys.readouterr()
        assert (
            f"Settings file: {OPTIC_COLOR.OK_CYAN}{optic_settings_file_path}{OPTIC_COLOR.STOP} already exists"
            in captured.out
        )

    def test_get_shell_env(self, mocker):
        # Test when $SHELL environment variable is set
        mocker.patch.dict(os.environ, {"SHELL": "/bin/bash"})
        assert get_shell_env() == "/bin/bash"

        # Test when $SHELL environment variable is not set
        mocker.patch.dict(os.environ, {}, clear=True)
        with pytest.raises(Exception):  # noqa: B017
            get_shell_env()

    def test_setup_shell_completion_zsh(self, mocker):
        # Test when shell is /bin/zsh
        mocker.patch(
            "optic.initialize.initialize_service.get_shell_env", return_value="/bin/zsh"
        )
        mock_configure_shell_to_use_completion = mocker.patch(
            "optic.initialize.initialize_service.configure_shell_to_use_completion"
        )

        setup_shell_completion()

        mock_configure_shell_to_use_completion.assert_called_once_with("zsh")

    def test_setup_shell_completion_bash(self, mocker):
        # Test when shell is /bin/bash
        mocker.patch(
            "optic.initialize.initialize_service.get_shell_env",
            return_value="/bin/bash",
        )

        mock_configure_shell_to_use_completion = mocker.patch(
            "optic.initialize.initialize_service.configure_shell_to_use_completion"
        )

        setup_shell_completion()

        mock_configure_shell_to_use_completion.assert_called_with("bash")

    def test_setup_shell_completion_fail(self, mocker):
        # Test when shell is /bin/bash
        mocker.patch(
            "optic.initialize.initialize_service.get_shell_env",
            return_value="/fish",
        )

        mock_configure_shell_to_use_completion = mocker.patch(
            "optic.initialize.initialize_service.configure_shell_to_use_completion"
        )

        setup_shell_completion()

        mock_configure_shell_to_use_completion.assert_not_called()

    @pytest.mark.parametrize("extension", ["bash", "zsh"])
    def test_configure_shell_to_use_completion_create(
        self, mocker, mock_shell_configuration_file_path, temp_dir, extension
    ):
        mock_dir = f"{temp_dir}/optic"
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", mock_dir)

        # Mock "Yes" (True) input
        mocker.patch(
            "optic.initialize.initialize_service.prompt_question", return_value=True
        )

        mocker.patch.object(
            initialize_service,
            "get_shell_configuration_file",
            return_value=mock_shell_configuration_file_path,
        )

        # Test when shell completion file exists
        configure_shell_to_use_completion(extension)

        # Assert cluster_config file was created
        assert validate_file_exists(f"{mock_dir}/.optic-complete.{extension}")

    def test_configure_shell_to_use_completion_bash_file_exists(
        self, mocker, temp_dir, mock_shell_complete_file_path_bash, capsys
    ):
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", temp_dir)

        configure_shell_to_use_completion("bash")

        captured = capsys.readouterr()
        assert "Shell completion is already setup" in captured.out

    def test_configure_shell_to_use_completion_zsh_file_exists(
        self, mocker, temp_dir, mock_shell_complete_file_path_zsh, capsys
    ):
        mocker.patch.object(initialize_service, "CONFIG_BASE_DIR", temp_dir)

        configure_shell_to_use_completion("zsh")

        captured = capsys.readouterr()
        assert "Shell completion is already setup" in captured.out

    def test_validate_file_exists_success(
        self, cluster_config_file_path, optic_settings_file_path
    ):
        assert validate_file_exists(cluster_config_file_path)
        assert validate_file_exists(optic_settings_file_path)

    def test_validate_file_exists_fail(self):
        assert validate_file_exists("/temp/dummy_settings.yaml") is False
