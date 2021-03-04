# Copyright (c) 2016-2018, Neil Booth
# Copyright (c) 2017, the ElectrumX authors
# Copyright (c) 2021, the Kevacoin Project Core Developers
#
# All rights reserved.
#
# See the file "LICENCE" for information about the copyright
# and warranty status of this software.

'''Transaction input and output addresses by tx id.'''

from aiorpcx import run_in_thread

import electrumx.lib.util as util

import json

class TxDb(object):

    DB_VERSIONS = [0]
    # Only use first 16 bytes of tx hash to save space.
    # The chance of collision is extremely small.
    PARTIAL_TX_HASH = 16

    def __init__(self):
        self.logger = util.class_logger(__name__, self.__class__.__name__)
        self.db_version = max(self.DB_VERSIONS)
        self.db = None

    def open_db(self, db_class, for_sync):
        self.db = db_class('tx_info', for_sync)

    def close_db(self):
        if self.db:
            self.db.close()
            self.db = None

    def put_tx_info(self, tx_hash, tx_info):
        self.db.put(tx_hash[0:self.PARTIAL_TX_HASH], tx_info)

    def put_tx_info_batch(self, tx_info_batch):
        with self.db.write_batch() as batch:
            for tx_hash, tx_info in tx_info_batch.items():
                batch.put(tx_hash[0:self.PARTIAL_TX_HASH], json.dumps(tx_info).encode())

    def get_tx_info_sync(self, tx_hash):
        return self.db.get(tx_hash[0:self.PARTIAL_TX_HASH])

    async def get_tx_info(self, tx_hash):
        return await run_in_thread(self.db.get, tx_hash[0:self.PARTIAL_TX_HASH])
