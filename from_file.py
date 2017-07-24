#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
#
from colorlog import ColoredFormatter
# from subprocess import Popen, PIPE, STDOUT
from voluptuous import Schema, Url, Required, Optional, MultipleInvalid
import yaml
from from_url import launch_safaribooks_downloader, get_book_informations_from_url
from fuzzywuzzy import fuzz
import pprint


__author__ = 'atty_l'

# ---- LOG -----
LOGFORMAT = '%(log_color)s[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s] %(message)s'

formatter = ColoredFormatter(LOGFORMAT)
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
# --------------


# ----- PPRINT ------
# https://stackoverflow.com/questions/1713038/super-fails-with-error-typeerror-argument-1-must-be-type-not-classobj
# https://stackoverflow.com/questions/20514525/automatically-shorten-long-strings-when-dumping-with-pretty-print
class P(pprint.PrettyPrinter, object):
    def __init__(self, max_length=10):
        """

        :param max_length:
        """
        super(P, self).__init__()
        self._max_length = max_length
        self._ellipsis = ["..."]

    def _format(self, o, *args, **kwargs):
        if isinstance(o, list):
            if len(o) > self._max_length:
                o = o[:self._max_length] + self._ellipsis
        return pprint.PrettyPrinter._format(self, o, *args, **kwargs)
# --------------


def _create_schema():
    """

    :return:
    """
    # https://stackoverflow.com/questions/3262569/validating-a-yaml-document-in-python
    # https://pypi.python.org/pypi/voluptuous/
    # https://julien.danjou.info/blog/2015/python-schema-validation-voluptuous
    # Create the validation schema
    return Schema({
        Required('safari_user'): str,
        Required('safari_password'): str,
        Required('safari_urls'): [Url(str)],
        Optional('safari_books_ids'): [str, int]
    })


def crypt_config(config, fuzzy_pattern='safari_password', min_ratio=80):
    """

    :param config:
    :param fuzzy_pattern:
    :param min_ratio:
    :return:

    >>> crypt_config({'password': 'toto', 'passwd': 'tata', 'key': 'value'})
    {'passwd': '****', 'password': '****', 'key': 'value'}

    """
    return dict(
        (k, '*'*len(v) if fuzz.token_set_ratio(k, fuzzy_pattern) > min_ratio else v)
        for k, v in config.items()
    )


def _launch_downloader_from_urls(urls, safari_user, safari_password, not_download=False):
    """

    :param urls:
    :param safari_user:
    :param safari_password:
    :param not_download:
    :return:
    """
    for safari_url in urls:
        logger.debug("safari_url: {}".format(safari_url))

        book_id, book_name = get_book_informations_from_url(safari_url)

        if not not_download:
            launch_safaribooks_downloader(
                book_id,
                safari_user,
                safari_password,
                "books/",
                book_name
            )


def _launch_downloader_from_books_ids(books_ids, safari_user, safari_password, not_download=False):
    """

    :param books_ids:
    :param safari_user:
    :param safari_password:
    :param not_download:
    :return:
    """
    for safari_book_id in books_ids:
        logger.debug("safari_book_id: {}".format(safari_book_id))

        book_id, book_name = safari_book_id, safari_book_id

        if not not_download:
            launch_safaribooks_downloader(
                book_id,
                safari_user,
                safari_password,
                "books/",
                book_name
            )


def _process(args):
    """

    :param args:
    :return:

    """
    yaml_configs = list(yaml.load_all(args.configs))

    schema = _create_schema()

    for yaml_config in yaml_configs:
        logger.debug("yaml_config: {}".format(P().pprint(crypt_config(yaml_config))))
        try:
            # use the validation schema
            schema(yaml_config)
        except MultipleInvalid as e:
            logger.error("Schema not valid !\nException {}".format(e))
        else:
            # get access login/password
            safari_user = yaml_config['safari_user']
            safari_password = yaml_config['safari_password']

            _launch_downloader_from_urls(yaml_config['safari_urls'], safari_user, safari_password, args.not_download)

            _launch_downloader_from_books_ids(yaml_config['safari_books_ids'],
                                              safari_user, safari_password,
                                              args.not_download)


def parse_arguments():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    #
    parser.add_argument('configs', type=argparse.FileType('r'),
                        help='<Required> Configs file')
    #
    parser.add_argument("-d", "--not-download", action="store_true", default=False,
                        help="Desactivate downloads (debug purpose)")
    #
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="increase output verbosity")
    # return parsing
    return parser.parse_args()


def main():
    args = parse_arguments()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    _process(args)


if __name__ == '__main__':
    main()
