# Imports
import streamlit as st
from dataclasses import dataclass
from typing import List
import datetime as datetime
import pandas as pd
import hashlib


@dataclass()
class Record:
    # Attributes
    sender: str
    receiver: str
    amount: float


@dataclass
class Block:
    # Attributes
    record: Record
    creator_id: int
    prev_hash: str = "0"
    timestamp: str = datetime.datetime.utcnow().strftime("%H:%M:%S")
    nonce: int = 0

    def hash_block(self):
        sha = hashlib.sha256()

        record = str(self.record).encode()
        sha.update(record)

        creator_id = str(self.creator_id).encode()
        sha.update(creator_id)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        prev_hash = str(self.prev_hash).encode()
        sha.update(prev_hash)

        nonce = str(self.nonce).encode()
        sha.update(nonce)

        return sha.hexdigest()


# The ledger
@dataclass
class PyChain:
    # Attributes
    chain: List[Block]
    difficulty: int = 4

    # Difficulty of validation
    def proof_of_work(self, block):

        calculated_hash = block.hash_block()

        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):
            block.nonce += 1

            calculated_hash = block.hash_block()

        print("Wining Hash", calculated_hash)
        return block

    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    # Validate blocks
    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is Valid")
        return True


# Adds the genesis node to the cache
# The genesis node is viewable as a block on the ledger and dropdown
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain")
    return PyChain([Block("Genesis", 0)])


# Top of page
st.markdown("# PyChain")
st.markdown("## Store a Transaction Record in the PyChain")

pychain = setup()

# Add an input area where you can get a value for `sender` from the user.
sender = st.text_input("Who is the sender???")

# Add an input area where you can get a value for `receiver` from the user.
receiver = st.text_input("Who is the receiver???")

# Add an input area where you can get a value for `amount` from the user.
amount = st.number_input("How much will be sent???")

if st.button("Add Block"):
    # Create new hash
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()

    # Create New block with information from sender, receiver, and amount input
    new_block = Block(
        record=Record(sender=sender, receiver=receiver, amount=amount),
        creator_id=42,
        prev_hash=prev_block_hash
    )

    # Add new block
    pychain.add_block(new_block)
    st.balloons()

# Bottom of page
st.markdown("## The PyChain Ledger")

# THe ledger table
pychain_df = pd.DataFrame(pychain.chain).astype(str)
st.write(pychain_df)

# Validate Chain button
if st.button("Validate Chain"):
    st.write(pychain.is_valid())

# Side of page
# Difficulty selector
difficulty = st.sidebar.slider("Block Difficulty", 1, 5, 2)
pychain.difficulty = difficulty

# Block selector dropdown
st.sidebar.write("# Block Inspector")
selected_block = st.sidebar.selectbox(
    "Which block would you like to see?", pychain.chain
)

# Block display
st.sidebar.write(selected_block)
