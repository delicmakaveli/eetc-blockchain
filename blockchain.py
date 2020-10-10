import copy
import hashlib
from datetime import datetime
from typing import Dict, Tuple, List
import json


class Block:
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        """
        TODO explain what a Block is

        :param index: Index of the block in the Blockchain (starting at 0).
        :param timestamp: Unix timestamp for when this Block was created.
        :param data: Dict containing the data stored in this Block.
        :param previous_hash: Hash string of the previous Block.
        """

        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.generate_hash()

    def __str__(self):
        return f"Block #{self.index} [Hash: {self.hash}, Data: {self.data}]"

    def generate_hash(self) -> str:
        """
        Generate a Hash string for this Block.
        """

        block_hash = hashlib.sha256()

        block_hash.update(str(self.index).encode("utf-8"))
        block_hash.update(self.timestamp.encode("utf-8"))
        block_hash.update(json.dumps(self.data).encode("utf-8"))
        block_hash.update(self.previous_hash.encode("utf-8"))

        return block_hash.hexdigest()


class Blockchain:
    def __init__(self):
        """
        TODO Explain what a Blockchain is
        """
        self.blocks: List = [self._generate_genesis_block()]

    def __str__(self):
        blocks = "\n\t".join([str(block) for block in self.blocks])
        return f"Blockchain:\n\t{blocks}"

    @property
    def current_unix_timestamp(self) -> str:
        return str(datetime.timestamp(datetime.utcnow()))

    def _generate_genesis_block(self) -> Block:
        """
        Generates the 1st Block for the Blockchain.
        """

        return Block(
            0,
            self.current_unix_timestamp,
            {"author": "Stefan Delic", "message": "Hello world."},
            "Liberate my madness...",
        )

    def insert_block(self, data: Dict) -> Block:
        """
        Insert a Block into the Blockchain by appending it to the end of the Block list.
        :param data: Dict with Data contained in the Block.
        :return: Latest Block after adding it to the Blockchain.
        """

        self.blocks.append(
            Block(
                len(self.blocks),
                self.current_unix_timestamp,
                data,
                self.blocks[-1].hash,
            ),
        )
        return self.latest_block

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the Blockchain to make sure all the data is not corrupted.
        """

        flag = True
        validation_errors = []

        for i in range(1, len(self.blocks)):
            if self.blocks[i].index != i:
                flag = False
                validation_errors.append(f"Wrong block index at block {i}.")
            if self.blocks[i - 1].hash != self.blocks[i].previous_hash:
                flag = False
                validation_errors.append(f"Wrong previous hash at block {i}.")
            if self.blocks[i].hash != self.blocks[i].generate_hash():
                flag = False
                validation_errors.append(f"Wrong hash at block {i}.")
            if self.blocks[i - 1].timestamp >= self.blocks[i].timestamp:
                flag = False
                validation_errors.append(f"Backdating at block {i}.")

        return flag, validation_errors

    @property
    def is_valid(self) -> bool:
        return self.validate()[0]

    @property
    def length(self):
        return len(self.blocks)

    @property
    def latest_block(self):
        return self.blocks[-1]

    def fork(self, upto: int = -1) -> "Blockchain":
        """
        Copy this Blockchain (either whole or part of it) and start a new Blockchain from that.
        :param upto: If you want to branch off from a certain Block in the chain instead of the end.
        :return: A new Blockchain derrived from the current one.
        """

        new_block = copy.deepcopy(self)

        if upto:
            new_block.blocks = new_block.blocks[:upto]

        return new_block

    def get_root(self, child_chain: "Blockchain"):
        """
        Gives you the root of the child Blockchain which was forked from this parent Blockchain. The
        root is the part of this Blockchain that preceded the Fork.
        :param child_chain: The child Blockchain that was forked from this Blockchain.
        :return: Part of the parent Blockchain that precedes the child Blockchain.
        """
        min_len = min(self.length, child_chain.length)

        for i in range(1, min_len):
            if self.blocks[i] != child_chain.blocks[i]:
                return self.fork(i)

        return self.fork(min_len)
