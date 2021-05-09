# Copyright (c) 2016-2018, Neil Booth
# Copyright (c) 2017, the ElectrumX authors
# Copyright (c) 2021, the Kevacoin Project Core Developers
#
# All rights reserved.
#
# See the file "LICENCE" for information about the copyright
# and warranty status of this software.

'''Ban txs, i.e. hide their contents and search results.'''

from aiorpcx import TaskGroup, run_in_thread

import electrumx.lib.util as util
from electrumx.lib.util import pack_be_uint16, unpack_be_uint16_from
from electrumx.lib.hash import hash_to_hex_str, HASHX_LEN


class KevaBan(object):

    DB_VERSIONS = [0]

    PREFIX_HIDE = b'_'

    def __init__(self):
        self.logger = util.class_logger(__name__, self.__class__.__name__)
        self.db_version = max(self.DB_VERSIONS)
        self.db = None

    def open_db(self, db_class, for_sync):
        self.db = db_class('keva_ban', for_sync)

    def close_db(self):
        if self.db:
            self.db.close()
            self.db = None

    async def put_keva_ban_tx(self, tx_hash, reason=0):
        return await run_in_thread(self.db.put, self.PREFIX_HIDE + tx_hash, bytes([reason]))

    async def get_keva_ban_tx(self, tx_hash):
        return await run_in_thread(self.db.get, self.PREFIX_HIDE + tx_hash)

    def get_keva_all_ban_tx_sync(self, reason):
        keys = []
        for key, r in self.db.iterator(prefix=self.PREFIX_HIDE):
            if reason == -1 or reason == int(r[0]):
                entry = {
                    'tx': key[1:].hex(),
                    'reason': r[0],
                }
                keys.append(entry)
        return keys

    async def get_keva_all_ban_tx(self, reason=-1):
        return await run_in_thread(self.get_keva_all_ban_tx_sync, reason)

    async def delete_keva_ban_tx(self, tx_hash):
        return await run_in_thread(self.db.delete, self.PREFIX_HIDE + tx_hash)
