#
# This file is part of the PyRDP project.
# Copyright (C) 2020 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

"""
File that contains methods related to the MITM command line.
To be consumed either via bin/pyrdp-mitm.py or via twistd plugin.
"""
import argparse
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Tuple

import appdirs
import OpenSSL

from pyrdp.core.ssl import ServerTLSContext
from pyrdp.logging import JSONFormatter, log, LOGGER_NAMES, LoggerNameFilter, SessionLogger, VariableFormatter
from pyrdp.mitm.config import MITMConfig


def parseTarget(target: str) -> Tuple[str, int]:
    """
    Parse a target host:port and return components. Port is optional.
    """
    if ":" in target:
        targetHost = target[: target.index(":")]
        targetPort = int(target[target.index(":") + 1:])
    else:
        targetHost = target
        targetPort = 3389
    return targetHost, targetPort


def validateKeyAndCertificate(private_key: str, certificate: str) -> Tuple[str, str]:
    if (private_key is None) != (certificate is None):
        sys.stderr.write("You must provide both the private key and the certificate")
        sys.exit(1)
    elif private_key is None:
        key, cert = getSSLPaths()
        handleKeyAndCertificate(key, cert)
    else:
        key, cert = private_key, certificate

    try:
        # Check if OpenSSL accepts the private key and certificate.
        ServerTLSContext(key, cert)
    except OpenSSL.SSL.Error as error:
        from pyrdp.logging import log
        log.error(
            "An error occurred when creating the server TLS context. " +
            "There may be a problem with your private key or certificate (e.g: signature algorithm too weak). " +
            "Here is the exception: %(error)s",
            {"error": error}
        )
        sys.exit(1)

    return key, cert


def handleKeyAndCertificate(key: str, certificate: str):
    """
    Handle the certificate and key arguments that were given on the command line.
    :param key: path to the TLS private key.
    :param certificate: path to the TLS certificate.
    """

    from pyrdp.logging import LOGGER_NAMES
    logger = logging.getLogger(LOGGER_NAMES.MITM)

    if os.path.exists(key) and os.path.exists(certificate):
        logger.info("Using existing private key: %(privateKey)s", {"privateKey": key})
        logger.info("Using existing certificate: %(certificate)s", {"certificate": certificate})
    else:
        logger.info("Generating a private key and certificate for SSL connections")

        if generateCertificate(key, certificate):
            logger.info("Private key path: %(privateKeyPath)s", {"privateKeyPath": key})
            logger.info("Certificate path: %(certificatePath)s", {"certificatePath": certificate})
        else:
            logger.error("Generation failed. Please provide the private key and certificate with -k and -c")


def getSSLPaths() -> (str, str):
    """
    Get the path to the TLS key and certificate in pyrdp's config directory.
    :return: the path to the key and the path to the certificate.
    """
    config = appdirs.user_config_dir("pyrdp", "pyrdp")

    if not os.path.exists(config):
        os.makedirs(config)

    key = config + "/private_key.pem"
    certificate = config + "/certificate.pem"
    return key, certificate


def generateCertificate(keyPath: str, certificatePath: str) -> bool:
    """
    Generate an RSA private key and certificate with default values.
    :param keyPath: path where the private key should be saved.
    :param certificatePath: path where the certificate should be saved.
    :return: True if generation was successful
    """

    if os.name != "nt":
        nullDevicePath = "/dev/null"
    else:
        nullDevicePath = "NUL"

    result = os.system("openssl req -newkey rsa:2048 -nodes -keyout %s -x509 -days 365 -out %s -subj \"/CN=www.example.com/O=PYRDP/C=US\" 2>%s" % (keyPath, certificatePath, nullDevicePath))
    return result == 0


def prepareLoggers(logLevel: int, logFilter: str, sensorID: str, outDir: Path):
    """
    :param logLevel: log level for the stream handler.
    :param logFilter: logger name to filter on.
    :param sensorID: ID to differentiate between instances of this program in the JSON log.
    :param outDir: output directory.
    """
    logDir = outDir / "logs"
    logDir.mkdir(exist_ok = True)

    formatter = VariableFormatter("[{asctime}] - {levelname} - {sessionID} - {name} - {message}", style = "{", defaultVariables = {
        "sessionID": "GLOBAL"
    })

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    streamHandler.setLevel(logLevel)
    streamHandler.addFilter(LoggerNameFilter(logFilter))

    logFileHandler = logging.handlers.TimedRotatingFileHandler(logDir / "mitm.log", when = "D")
    logFileHandler.setFormatter(formatter)

    jsonFileHandler = logging.FileHandler(logDir / "mitm.json")
    jsonFileHandler.setFormatter(JSONFormatter({"sensor": sensorID}))
    jsonFileHandler.setLevel(logging.INFO)

    rootLogger = logging.getLogger(LOGGER_NAMES.PYRDP)
    rootLogger.addHandler(streamHandler)
    rootLogger.addHandler(logFileHandler)
    rootLogger.setLevel(logging.DEBUG)

    connectionsLogger = logging.getLogger(LOGGER_NAMES.MITM_CONNECTIONS)
    connectionsLogger.addHandler(jsonFileHandler)

    crawlerFormatter = VariableFormatter("[{asctime}] - {sessionID} - {message}", style = "{", defaultVariables = {
        "sessionID": "GLOBAL"
    })

    crawlerFileHandler = logging.FileHandler(logDir / "crawl.log")
    crawlerFileHandler.setFormatter(crawlerFormatter)

    jsonCrawlerFileHandler = logging.FileHandler(logDir / "crawl.json")
    jsonCrawlerFileHandler.setFormatter(JSONFormatter({"sensor": sensorID}))

    crawlerLogger = logging.getLogger(LOGGER_NAMES.CRAWLER)
    crawlerLogger.addHandler(crawlerFileHandler)
    crawlerLogger.addHandler(jsonCrawlerFileHandler)
    crawlerLogger.setLevel(logging.INFO)

    log.prepareSSLLogger(logDir / "ssl.log")

    return logging.getLogger(LOGGER_NAMES.MITM)


def logConfiguration(config: MITMConfig):
    logging.getLogger(LOGGER_NAMES.MITM).info("Target: %(target)s:%(port)d", {"target": config.targetHost, "port": config.targetPort})
    logging.getLogger(LOGGER_NAMES.MITM).info("Output directory: %(outputDirectory)s", {"outputDirectory": config.outDir.absolute()})