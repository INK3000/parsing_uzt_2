import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--marker', type=str, help='Log marker')

args = parser.parse_args()
marker = args.marker or ''

settings = {
    'version': 1,
    'formatters': {
        'blue': {
            'format': '\x1b[34;20m'
            + marker
            + ' {asctime} {levelname}: {message}'
            + '\x1b[0m',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'yellow': {
            'format': '\x1b[33;20m'
            + marker
            + ' {asctime} {levelname}: {message}'
            + '\x1b[0m',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'default': {
            'format': marker + ' {asctime} {levelname}: {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'yellow',
        },
        # "telegram": {
        #     "class": "loggers.handlers.TelegramBotHandler",
        #     "level": "INFO",
        #     "formatter": "default",
        # },
    },
    'loggers': {
        '__main__': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        }
    },
    'disable_existing_loggers': False,
    # 'filters': {},
    # 'incremental': False,
    # 'root': {}, # '': {},
}
