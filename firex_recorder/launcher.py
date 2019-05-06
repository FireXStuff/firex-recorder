
import os
import subprocess

from celery.utils.log import get_task_logger
from firexapp.broker_manager.broker_factory import BrokerFactory
from firexapp.fileregistry import FileRegistry
from firexapp.submit.uid import Uid
from firexapp.submit.tracking_service import TrackingService


logger = get_task_logger(__name__)


RECORDER_LOG_REGISTRY_KEY = 'RECORDER_OUTPUT_REGISTRY_KEY'
FileRegistry().register_file(RECORDER_LOG_REGISTRY_KEY, os.path.join(Uid.debug_dirname, 'recorder.stdout'))

DEFAULT_RECORDER_DEST_REGISTRY_KEY = 'DEFAULT_RECORDER_DEST_REGISTRY_KEY'
FileRegistry().register_file(DEFAULT_RECORDER_DEST_REGISTRY_KEY, os.path.join(Uid.debug_dirname, 'firex.rec'))


class RecorderLauncher(TrackingService):

    def extra_cli_arguments(self, arg_parser):
        arg_parser.add_argument('--recording', help='A file to record celery events', default=None)

    def start(self, args, uid=None, **kwargs)->{}:
        # assemble startup cmd
        cmd = "firex_recorder"
        if args.recording:
            cmd += ' --destination ' + args.recording
        else:
            cmd += ' --destination ' + FileRegistry().get_file(DEFAULT_RECORDER_DEST_REGISTRY_KEY, uid.logs_dir)
        cmd += ' --broker ' + BrokerFactory.get_broker_url()
        cmd += " &"

        # start the recording service
        logger.debug("Starting Recorder...")
        recorder_stdout = FileRegistry().get_file(RECORDER_LOG_REGISTRY_KEY, uid.logs_dir)
        with open(recorder_stdout, 'wb') as out:
            subprocess.check_call(cmd, shell=True, stdout=out, stderr=subprocess.STDOUT)
