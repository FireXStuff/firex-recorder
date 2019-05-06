
import os
import subprocess

from celery.utils.log import get_task_logger
from firexapp.fileregistry import FileRegistry
from firexapp.submit.uid import Uid


logger = get_task_logger(__name__)


RECORDER_LOG_REGISTRY_KEY = 'RECORDER_OUTPUT_LOG_REGISTRY_KEY'
FileRegistry().register_file(RECORDER_LOG_REGISTRY_KEY, os.path.join(Uid.debug_dirname, 'recorder.stdout'))


class RecorderLauncher(TrackingService):

    def extra_cli_arguments(self, arg_parser):
        # todo: add the ArgParse arguments
        pass

    def start(self, args, uid=None, **kwargs)->{}:
        # assemble startup cmd
        cmd = "firex_recorder"

        # start the recording service
        logger.debug("Starting Recorder...")
        recorder_stdout = FileRegistry().get_file(RECORDER_LOG_REGISTRY_KEY, uid.logs_dir)
        with open(recorder_stdout, 'wb') as out:
            subprocess.check_call(cmd, shell=True, stdout=out, stderr=subprocess.STDOUT)
