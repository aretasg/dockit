def logging_conf():

    logging_conf = {
        "version": 1,
        "loggers": {
            "": {  # root logger
                "level": "NOTSET",
                "handlers": [
                    "debug_console_handler",
                    "info_rotating_file_handler",
                    "error_file_handler",
                    "critical_mail_handler",
                ],
            },
            "my.package": {  # just an example
                "level": "WARNING",
                "propagate": False,
                "handlers": ["info_rotating_file_handler", "error_file_handler"],
            },
        },
        "handlers": {
            "debug_console_handler": {
                "level": "DEBUG",
                "formatter": "info",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "info_rotating_file_handler": {
                "level": "INFO",
                "formatter": "info",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "info.log",
                "mode": "a",
                "maxBytes": 1048576,
                "backupCount": 5,
            },
            "error_file_handler": {
                "level": "WARNING",
                "formatter": "error",
                "class": "logging.FileHandler",
                "filename": "error.log",
                "mode": "a",
            },
            "critical_mail_handler": {  # not configured
                "level": "CRITICAL",
                "formatter": "error",
                "class": "logging.handlers.SMTPHandler",
                "mailhost": "localhost",
                "fromaddr": "monitoring@domain.com",
                "toaddrs": ["dev@domain.com", "qa@domain.com"],
                "subject": "Critical error with application name",
            },
        },
        "formatters": {
            "info": {
                "format": "%(asctime)s : [%(levelname)s] : %(module)s : %(funcName)s :: %(message)s"
            },
            "error": {
                "format": "%(asctime)s : [%(levelname)s] : %(module)s : %(funcName)s|%(lineno)s :: %(message)s"
            },
        },
    }

    return logging_conf
