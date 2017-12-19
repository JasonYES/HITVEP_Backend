from sanic.log import DefaultFilter
import sys
import logging

LOGGING = {
    'version': 1,
    'filters': {
        'showFilter': {
            '()': DefaultFilter,
            'param': [0, 10, 20, 30, 40, 50]
        },
        'accessFilter': {
            '()': DefaultFilter,
            'param': [20]
        },
        'errorFilter': {
            '()': DefaultFilter,
            'param': [30, 40, 50]
        }
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s - (%(name)s)[%(levelname)s]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'net' : {
            'format': '%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: ' +
                      '%(request)s %(message)s %(status)d %(byte)d',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }

    },
    'handlers': {
        'internal': {
            'class': 'logging.StreamHandler',
            'filters': ['showFilter'],
            'formatter': 'simple',
            'stream': sys.stderr
        },
        'internalnet': {
            'class': 'logging.StreamHandler',
            'filters': ['showFilter'],
            'formatter': 'net',
            'stream': sys.stderr
        },
        'accessTimedRotatingFile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filters': ['accessFilter'],
            'formatter': 'simple',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 0,
            'filename': './log/access.log'
        },
        'errorTimedRotatingFile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filters': ['errorFilter'],
            'when': 'midnight',
            'interval': 1,
            'backupCount': 0,
            'filename': './log/error.log',
            'formatter': 'simple'
        },
        'accessnetTimedRotatingFile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filters': ['accessFilter'],
            'formatter': 'net',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 0,
            'filename': './log/access.log'
        },
        'errornetTimedRotatingFile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filters': ['errorFilter'],
            'when': 'midnight',
            'interval': 1,
            'backupCount': 0,
            'filename': './log/error.log',
            'formatter': 'net'
        }
    },
    'loggers': {
        'sanic': {
            'level': 'DEBUG',
            'handlers': ['accessTimedRotatingFile', 'errorTimedRotatingFile','internal']
        },
        'network': {
            'level': 'DEBUG',
            'handlers': ['internalnet','accessnetTimedRotatingFile','errornetTimedRotatingFile']
        }
    }
}
logging.basicConfig(filename="access.log", filemode="a",
                    level=logging.INFO, format='%(levelname)s   %(asctime)s %(message)s')
ERROR = logging.FileHandler("error.log")
ERROR.setLevel(logging.ERROR)
formatter = logging.Formatter('%(levelname)s   %(asctime)s %(message)s')
ERROR.setFormatter(formatter)
logging.getLogger('').addHandler(ERROR)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatters = logging.Formatter('%(asctime)s %(message)s')
console.setFormatter(formatters)
logging.getLogger('').addHandler(console)

def do_log(level, info):
    if level == 5:
        logging.critical(info)
    elif level == 4:
        logging.error(info)
    elif level == 3:
        logging.warning(info)
    elif level == 2:
        logging.info(info)
    elif level == 1:
        logging.debug(info)