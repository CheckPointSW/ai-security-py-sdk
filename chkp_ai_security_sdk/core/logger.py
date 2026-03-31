import logging
import os

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s][%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

_logger = logging.getLogger('chkp_ai_security_sdk:info')
_error_logger = logging.getLogger('chkp_ai_security_sdk:error')
_network_logger = logging.getLogger('chkp_ai_security_sdk:network')

_logger.addHandler(handler)
_error_logger.addHandler(handler)
_network_logger.addHandler(handler)

__activate_logs = os.environ.get('AI_SECURITY_SDK_LOGGER', '')

_logger.setLevel(logging.CRITICAL + 1)
_error_logger.setLevel(logging.CRITICAL + 1)
_network_logger.setLevel(logging.CRITICAL + 1)

logger = _logger.debug
error_logger = _error_logger.error
network_logger = _network_logger.info


def activate_all_loggers():
    _logger.setLevel(logging.DEBUG)
    _error_logger.setLevel(logging.DEBUG)
    _network_logger.setLevel(logging.DEBUG)


def activate_info_logger():
    _logger.setLevel(logging.DEBUG)


def activate_error_logger():
    _error_logger.setLevel(logging.DEBUG)


def activate_network_logger():
    _network_logger.setLevel(logging.DEBUG)


if __activate_logs == '*':
    activate_all_loggers()
else:
    _loggers = __activate_logs.split(',')
    if 'info' in _loggers:
        activate_info_logger()
    if 'error' in _loggers:
        activate_error_logger()
    if 'network' in _loggers:
        activate_network_logger()
