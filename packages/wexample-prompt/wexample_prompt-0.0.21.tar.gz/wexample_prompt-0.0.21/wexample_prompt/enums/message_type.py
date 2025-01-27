from enum import Enum


class MessageType(Enum):
    ALERT = "alert"
    CRITICAL = "critical"
    DEBUG = "debug"
    ERROR = "error"
    FAILURE = "failure"
    INFO = "info"
    LOG = "log"
    SUCCESS = "success"
    TASK = "task"
    WARNING = "warning"
