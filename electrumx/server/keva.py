# Copyright (c) 2016-2018, Neil Booth
# Copyright (c) 2017, the ElectrumX authors
# Copyright (c) 2021, the Kevacoin Project Core Developers
#
# All rights reserved.
#
# See the file "LICENCE" for information about the copyright
# and warranty status of this software.

'''Key-value by tx id.'''

import array
import ast
import bisect
import time
from collections import defaultdict
from functools import partial

import electrumx.lib.util as util
from electrumx.lib.util import pack_be_uint16, unpack_be_uint16_from
from electrumx.lib.hash import hash_to_hex_str, HASHX_LEN


class Keva(object):

    DB_VERSIONS = [0]

    def __init__(self, coin):
        self.logger = util.class_logger(__name__, self.__class__.__name__)
        self.db_version = max(self.DB_VERSIONS)
        self.db = None
        self.interpret_name_prefix = coin.interpret_name_prefix
        self.NAME_OPERATIONS = coin.NAME_OPERATIONS

    def open_db(self, db_class, for_sync):
        self.db = db_class('keva', for_sync)

    def close_db(self):
        if self.db:
            self.db.close()
            self.db = None

    def put_keva_script(self, tx_id, keva_script):
        self.db.put(tx_id, keva_script)

    def get_keva_script(self, tx_id):
        return self.db.get(tx_id)

    def parse_keva_script(self, keva_script):
        name_values, _ = self.interpret_name_prefix(keva_script, self.NAME_OPERATIONS)
        name_values['op'] = keva_script[0]
        return name_values