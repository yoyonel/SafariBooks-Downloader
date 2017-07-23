#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
#
from colorlog import ColoredFormatter
# from subprocess import Popen, PIPE, STDOUT
from voluptuous import Schema, Url, Required, MultipleInvalid
import yaml
from from_url import launch_safaribooks_downloader, get_book_informations_from_url

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


def process(args):
    """

    :param args:
    :return:

    safaribooks-downloader -b 9781119077954 -u lionel.atty -p <password> -o "books/fpga-based-implementation-of.epub"
    """
    yaml_configs = list(yaml.load_all(args.configs))
    logger.debug("yaml_configs.items(): {}".format(yaml_configs))

    # https://stackoverflow.com/questions/3262569/validating-a-yaml-document-in-python
    # https://pypi.python.org/pypi/voluptuous/
    # https://julien.danjou.info/blog/2015/python-schema-validation-voluptuous
    # Create the validation schema
    schema = Schema({
        Required('safari_user'): str,
        Required('safari_password'): str,
        Required('safari_urls'): [Url(str)],
    })

    for yaml_config in yaml_configs:
        try:
            # use the validation schema
            schema(yaml_config)
        except MultipleInvalid as e:
            logger.error("Schema not valid !\nException {}".format(e.msg(e)))
        else:
            # get access login/password
            safari_user = yaml_config['safari_user']
            safari_password = yaml_config['safari_password']

            for safari_url in yaml_config['safari_urls']:
                logger.debug("safari_url: {}".format(safari_url))

                book_id, book_name = get_book_informations_from_url(safari_url)

                launch_safaribooks_downloader(
                    book_id,
                    safari_user,
                    safari_password,
                    "books/",
                    book_name
                )


def parse_arguments():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    #
    parser.add_argument('configs', type=argparse.FileType('r'),
                        help='<Required> Configs file')
    #
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="increase output verbosity")
    # return parsing
    return parser.parse_args()


def main():
    args = parse_arguments()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    process(args)


if __name__ == '__main__':
    main()
