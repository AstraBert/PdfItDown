class FileExistsWarning(Warning):
    """Use when an output file exists and will be overwritten"""


class EmptyImageError(Exception):
    """Raised when an image does not contain any bytes"""
