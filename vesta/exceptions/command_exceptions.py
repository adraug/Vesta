class CommandRuntimeError(Exception):
    """
    Exception raised when a command fails to run.
    """

    message: str
    def __init__(self, message: str):
        """
        Initializes the exception with the given message.

        :param message: The reason why the command failed to run as a language key
        """
        self.message = message
        super().__init__(message)