import os
import yaml

class Config(object):

    def __init__(self, config_file_path: str):
        with open(config_file_path, "r") as f:
            c = yaml.safe_load(f)

            self.__runbooks_dir = os.path.abspath(c["runbooksDir"])
            self.__runbook_logs_dir = os.path.abspath(c["runbookLogsDir"])
            self.__runbooks_index_dir = os.path.abspath(c["runbooksIndexDir"])

    @property
    def runbooks_dir(self) -> str:
        return self.__runbooks_dir

    @property
    def runbook_logs_dir(self) -> str:
        return self.__runbook_logs_dir

    @property
    def runbooks_index_dir(self) -> str:
        return self.__runbooks_index_dir

    def validate(self):
        if self.__runbooks_dir is None:
            raise ValueError("Runbooks directory is not set in the configuration file.")

        if self.__runbook_logs_dir is None:
            raise ValueError("Runbook logs directory is not set in the configuration file.")

        if self.__runbooks_index_dir is None:
            raise ValueError("Runbooks index directory is not set in the configuration file.")

        if not os.path.exists(self.__runbooks_dir):
            raise ValueError(f"Runbooks directory does not exist: {self.__runbooks_dir}")

        # Do not check the runbook logs directory and runbooks index directory as
        # they are created on the fly.
