 from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
from eth_utils import keccak, to_bytes, remove_0x_prefix, to_int, to_checksum_address, to_hex
from eth_hash.auto import keccak as keccak_256
import rlp
from rlp.sedes import Binary, big_endian_int, binary
from trie import HexaryTrie
import poseidon

# Connect to an Ethereum node
w3 = Web3(Web3.HTTPProvider('https://sepolia-rpc.scroll.io'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# User's Address and Token Address
token_address = '0x5300000000000000000000000000000000000004' # weth address 
user_address = '0x7739e567b9626ca241bdc5528343f92f7e59af37' # whale on scroll
block_number = 1811605

def get_state_root(block_number):
    block = w3.eth.get_block(block_number)
    state_root = block['stateRoot']
    print(state_root)
    return state_root

# Function to get proof using eth_getProof
def get_proof(address, storage_keys, block):
    return w3.eth.get_proof(address, storage_keys, block)

def getStorageAtIndex(i):
    pos = str(i).rjust(64, '0')
    key = remove_0x_prefix(user_address).rjust(64, '0').lower()
    storage_key = to_hex(w3.keccak(hexstr=key + pos))
    return to_int(w3.eth.get_storage_at(token_address, storage_key, block_identifier=block_number))  # Added block_identifier argument


def get_storage_key(token_address, user_address, block_number):
    for i in range(0, 20):
        storage_value = getStorageAtIndex(i)
        if storage_value != 0:
            print("position is {}".format(i))
            pos = str(i).rjust(64, '0')
            key = remove_0x_prefix(user_address).rjust(64, '0').lower()
            storage_key = to_hex(w3.keccak(hexstr=key + pos))
            value = to_int(storage_value)
            print("Value at storage key:", value) #verified on scrollyscan
            print(storage_key)
            return storage_key

def verify_proof(contract_address, storage_key, proof):
    scroll_chain_commitment_verifier = w3.eth.contract(
        address=contract_address,
        abi=[{"inputs":[{"internalType":"uint256","name":"batchIndex","type":"uint256"},{"internalType":"address","name":"account","type":"address"},{"internalType":"bytes32","name":"storageKey","type":"bytes32"},{"internalType":"bytes","name":"proof","type":"bytes"}],"name":"verifyStateCommitment","outputs":[{"internalType":"bytes32","name":"storageValue","type":"bytes32"}],"stateMutability":"view","type":"function"}]
    )
    batch_index = 0  # Replace with actual batch index if needed
    storage_value = scroll_chain_commitment_verifier.functions.verifyStateCommitment(
        batch_index,
        token_address,
        storage_key,
        proof
    ).call()
    return storage_value

state_root = get_state_root(block_number)  # From your existing code
storage_key = get_storage_key(token_address, user_address, block_number)
expected_value = "4901428453420949724217"  # Updated expected value with 18 decimals
proof = get_proof(token_address, [storage_key], block_number)
# print(proof['storageProof'])
proof_nodes = proof['storageProof']
proof_nodes = [node.hex() for node in proof['storageProof'][0]['proof']]
verified_storage_value = verify_proof(token_address, storage_key, ''.join(proof_nodes))
print(f"Verified Storage Value: {verified_storage_value}")