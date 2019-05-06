import os

from firexapp.fileregistry import FileRegistry
from firexapp.submit.submit import get_log_dir_from_output
from firexapp.testing.config_base import FlowTestConfiguration, assert_is_good_run

from firex_recorder.launcher import RECORDER_LOG_REGISTRY_KEY


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
                assert False, ""

    def assert_expected_return_code(self, ret_value):
        assert_is_good_run(ret_value)
