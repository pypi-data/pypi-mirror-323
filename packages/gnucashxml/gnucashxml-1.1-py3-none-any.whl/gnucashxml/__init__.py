# Copyright (c) David Nagy
# SPDX-License-Identifier: N/A

from sys import version_info
if version_info < (3, 6):
    raise ImportError('gnucashxml requires Python 3.6+')
del version_info

from gnucashxml import gnucashxml
