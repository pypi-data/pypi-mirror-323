import asyncio

from niceterminal import xterm
from niceterminal.interface.subprocess import ShellInterface

from loguru import logger

class TerminalInterfaces:
    """ This provides multiple terminals and services for a single user
    """
    def __init__(self, controller: "TerminalController" = None):
        self.controller = controller

        # We do take advantage of the fact that dicts are ordered
        self.interfaces = {}
        self.creation_count = 0

    def new_interface(self, interface: xterm.Interface = None):
        """
        """
        if not interface:
            logger.info("Starting ShellInterface!")
            interface = ShellInterface()
            self.creation_count += 1
            interface.creation_index = self.creation_count
            asyncio.create_task(interface.launch_interface())

        self.interfaces[interface.id] = interface

        return interface

    def __len__(self) -> int:
        return len(self.interfaces)

    def __delitem__(self, k):
        del self.interfaces[k]

    def items(self):
        return self.interfaces.items()

    def __iter__(self):
        return iter(self.interfaces.values())

    def __getitem__(self, k):
        if isinstance(k, int):
            return list(self.interfaces.values())[k]
        return self.interfaces[k]

