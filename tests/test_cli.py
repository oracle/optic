import pytest
from click.testing import CliRunner

from optic.cli import alias, cli, cluster, index, init


@pytest.fixture
def runner():
    return CliRunner(echo_stdin=False)


class TestCli:
    @pytest.mark.parametrize("command", [alias, cli, cluster, index, init])
    def test_commands_help(self, runner, command):
        result = runner.invoke(command, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_cluster_command_fail(self, mocker, runner, optic_settings_file_path):
        # mock 'exit' to prevent the test from exiting
        mock_exit = mocker.patch("builtins.exit", side_effect=SystemExit(1))

        # with pytest.raises(OpticError) as exc_info:
        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "cluster",
                "info",
                "--cluster-config",
                "dummy.yml",
            ],
        )
        mock_exit.assert_called_once_with(1)

    def test_cluster_command_success(
        self, mocker, runner, optic_settings_file_path, optic_settings, cluster_config
    ):
        mock_cluster_config_class = mocker.patch("optic.cli.ClusterConfig")
        mock_get_cluster_info = mocker.patch("optic.cli.get_cluster_info")

        runner.invoke(
            cli,
            [
                "--settings",
                optic_settings_file_path,
                "cluster",
                "info",
                "--clusters",
                "cluster_1",
            ],
        )
        mock_cluster_config_class.assert_called_once()
        mock_get_cluster_info.assert_called_once()

    def test_init_command(self, mocker, runner):
        mock_initialize_optic = mocker.patch("optic.cli.initialize_optic")

        runner.invoke(
            init,
            [
                "--cluster-config-setup",
                "Y",
                "--settings-setup",
                "Y",
                "--shell-setup",
                "Y",
            ],
        )
        mock_initialize_optic.assert_called_with(True, True, True)

        runner.invoke(
            init,
            [
                "--cluster-config-setup",
                "Y",
                "--settings-setup",
                "Y",
                "--shell-setup",
                "N",
            ],
        )
        mock_initialize_optic.assert_called_with(True, True, False)
