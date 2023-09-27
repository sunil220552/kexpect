"""Exception classes used by k8sExpect"""

class ExceptionKexpect(Exception):
    '''Base class for all exceptions raised by this module.
    '''

    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)

class TIMEOUT(ExceptionKexpect):
    '''Raised when a read time exceeds the timeout.
    '''

class ExceptionK8sAPI(ExceptionKexpect):
    '''Raised when a k8s API fails.
    '''
