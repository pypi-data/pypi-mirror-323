import logging
import subprocess
import sys
from typing import List, Dict, Optional, Union

from blazetest.core.utils.exceptions import CommandExecutionException

logger = logging.getLogger(__name__)


class CommandExecutor:
    def __init__(self, executable: str, command: str = None, arguments: Dict = None):
        """
        :param executable:
            Executable service or module, for example: sam
        :param command:
            Command for the executable, for example: sam build
        :param arguments:
            Arguments needed to be added to the command
        """
        self.executable = executable
        self.command = command

        if arguments is None:
            arguments = {}

        self.arguments: List = self.__join_arguments(arguments=arguments)

    def execute_command(
        self, allowed_return_codes: List[int] = None, input_data: Optional[Union[str, bytes]] = None
    ) -> int:
        """
        Execute the command with optional input data for stdin.

        :param allowed_return_codes: List of return codes that are considered successful
        :param input_data: Optional data to pipe to the process via stdin
        :return: Return code from the process
        """
        if allowed_return_codes is None:
            allowed_return_codes = [0]

        call = [self.executable, self.command] if self.command else [self.executable]
        logger.debug(f"Command: {call} {' '.join(self.arguments)}")

        # Convert string input to bytes if necessary
        if isinstance(input_data, str):
            input_data = input_data.encode()

        try:
            if input_data is not None:
                process = subprocess.Popen(
                    call + self.arguments, stdout=sys.stdout, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                process.communicate(input=input_data)
                if process.returncode not in allowed_return_codes:
                    raise subprocess.CalledProcessError(process.returncode, call)
            else:
                subprocess.check_call(
                    call + self.arguments,
                    stdout=sys.stdout,
                    stderr=subprocess.STDOUT,
                )
        except subprocess.CalledProcessError as process:
            if process.returncode not in allowed_return_codes:
                logger.error(f"{self.executable} error with return code {process.returncode}")
                raise CommandExecutionException(f"{self.executable} error with return code {process.returncode}")
        return 0

    @staticmethod
    def __join_arguments(arguments: Dict) -> List:
        arguments_list = []
        for arg_key in arguments:
            arg_value = arguments[arg_key]

            arguments_list.append(arg_key)
            if arg_value is not None:
                arguments_list.append(arg_value)

        return arguments_list
