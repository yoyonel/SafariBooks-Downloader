#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
#
from colorlog import ColoredFormatter
from subprocess import Popen, PIPE, STDOUT

__author__ = 'atty_l'

# ---- LOG -----
LOGFORMAT = '%(log_color)s[%(asctime)s][%(levelname)s][%(filename)s][%(funcName)s] %(message)s'

formatter = ColoredFormatter(LOGFORMAT)
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
logger = logging.getLogger('pythonConfig')
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
# --------------


def process(args):
    """

    :param args:
    :return:

    safaribooks-downloader -b 9781119077954 -u lionel.atty -p <password> -o "books/fpga-based-implementation-of.epub"
    """
    try:
        url = args.url
        safari_user = args.user
        safari_passwd = args.passwd
        output_dir = args.output_dir
        url_tokens = url.split('/')
        book_id = filter(lambda token: token.isdigit(), url_tokens)[0]
        book_name = url_tokens[url_tokens.index(book_id) - 1]
    except Exception, e:
        logger.error("Exception: {}".format(e))
    else:
        cmd = 'safaribooks-downloader -b {} -u {} -p {} -o {}/{}.epub'.format(
            book_id,
            safari_user,
            safari_passwd,
            output_dir,
            book_name
        )
        logger.debug("cmd: {}".format(cmd))

        p = Popen(cmd.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1)
        p.stdin.close()  # eof
        for line in iter(p.stdout.readline, ''):
            print line,  # do something with the output here
        p.stdout.close()
        rc = p.wait()
        logger.debug("rc: {}".format(rc))


def parse_arguments():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    #
    parser.add_argument('url', type=str, default=None, help='<Required> url link')
    parser.add_argument('user', type=str, default=None, help='<Required> Safari user')
    parser.add_argument('passwd', type=str, default=None, help='<Required> Safari password')
    parser.add_argument('-o', '--output_dir', type=str, default="books/",
                        help='<Optional> Output directory (default: %(default)s)')
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
