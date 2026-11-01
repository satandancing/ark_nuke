# -*- coding=UTF-8 -*-
"""Run cmd on start up.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def _main():
    import logging
    import os
    import subprocess
    import sys

    __dirname__ = os.path.abspath(os.path.dirname(__file__))

    script_dir = os.path.join(__dirname__, sys.platform)
    if not os.path.exists(script_dir):
        return
    for i in os.listdir(script_dir):
        logging.info('Execute: %s', i)
        subprocess.call(os.path.join(script_dir, i))



if __name__ == '__main__':
    _main()

del _main
