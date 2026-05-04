class VercajkException(Exception):
    pass


class VercajkImageException(VercajkException):
    pass


class VercajkAnsibleException(VercajkException):
    pass


class VercajkConfigException(VercajkException):
    pass


class VercajkSnapshotException(VercajkException):
    pass
