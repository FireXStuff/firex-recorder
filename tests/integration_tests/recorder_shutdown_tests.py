import os

from firexapp.fileregistry import FileRegistry
from firexapp.submit.arguments import InputConverter
from firexapp.submit.submit import get_log_dir_from_output
from firexapp.testing.config_base import FlowTestConfiguration, assert_is_good_run, assert_is_bad_run

from firex_recorder.launcher import RECORDER_LOG_REGISTRY_KEY, RecorderLauncher
from firexkit.argument_conversion import SingleArgDecorator

RecorderLauncher.default_timeout = 60


class RecorderShutdownOnNormalCompletion(FlowTestConfiguration):
    timeout = 60

    def initial_firex_options(self) -> list:
        rec_file = os.path.join(self.results_folder, "recording.rec")
        return ["submit", "--chain", "nop", "--recording", rec_file]

    def assert_expected_firex_output(self, cmd_output, cmd_err):
        rec_file = os.path.join(self.results_folder, "recording.rec")
        assert os.path.isfile(rec_file), 'recording file not created'

        logs_dir = get_log_dir_from_output(cmd_output)
        recorder_stdout = FileRegistry().get_file(RECORDER_LOG_REGISTRY_KEY, logs_dir)
        assert os.path.isfile(recorder_stdout), 'recorder output not found'
        with open(recorder_stdout) as f:
            for line in f:
                if line.strip().endswith("Shutting down on broker and root task completion"):
                    break
            else:
                assert False, "Recorder did not log it's own shut down"

    def assert_expected_return_code(self, ret_value):
        assert_is_good_run(ret_value)


@InputConverter.register
@SingleArgDecorator('plugins')
def timeout_recorder_test(value):
    if "fail_celery_start.py" in value:
        RecorderLauncher.default_timeout = 1


class RecorderShutdownOnTimeout(FlowTestConfiguration):
    timeout = 60

    def initial_firex_options(self) -> list:
        bad_plugin = os.path.join(os.path.dirname(__file__), "data", "fail_celery_start.py")
        rec_file = os.path.join(self.results_folder, "recording.rec")
        return ["submit", "--chain", "nop", "--recording", rec_file, "--plugin", bad_plugin]

    def assert_expected_firex_output(self, cmd_output, cmd_err):
        logs_dir = get_log_dir_from_output(cmd_output)
        recorder_stdout = FileRegistry().get_file(RECORDER_LOG_REGISTRY_KEY, logs_dir)
        assert os.path.isfile(recorder_stdout), 'recorder output not found'
        for _ in range(0, 6):
            # there could be a delay in shutting down. Give it a change to finish
            with open(recorder_stdout) as f:
                for line in f:
                    if line.strip().endswith("Exiting on timeout"):
                        return
                else:
                    import time
                    time.sleep(0.5)
        else:
            assert False, "Recorder did not log it's own shut down"

    def assert_expected_return_code(self, ret_value):
        assert_is_bad_run(ret_value)
