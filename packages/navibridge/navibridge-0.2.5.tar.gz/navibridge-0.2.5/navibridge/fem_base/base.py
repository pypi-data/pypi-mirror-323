from abc import ABCMeta, abstractmethod


class ApdlWriteable:
    __metaclass__ = ABCMeta

    id: int

    @abstractmethod
    def apdl_str(self):
        pass
