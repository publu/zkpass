from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
from eth_utils import keccak, to_bytes, remove_0x_prefix, to_int, to_checksum_address, to_hex
from eth_hash.auto import keccak as keccak_256
import rlp
from rlp.sedes import Binary, big_endian_int, binary
from trie import HexaryTrie
import poseidon
from toolz import concat

# Connect to an Ethereum node
w3 = Web3(Web3.HTTPProvider('https://sepolia-rpc.scroll.io'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# User's Address and Token Address
token_address = '0x5300000000000000000000000000000000000004' # weth address 
user_address = '0x7739e567b9626ca241bdc5528343f92f7e59af37' # whale on scroll
block_number = 2721258

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

state_root = get_state_root(block_number)  # From your existing code
storage_key = get_storage_key(token_address, user_address, block_number)
expected_value = "185399054461883619056"  # Replace with actual expected value
proof = get_proof(token_address, [storage_key], block_number)
# print(proof['storageProof'])
proof_nodes = proof['storageProof']

proof_components = concat([
    f"0x{len(proof['accountProof']).to_bytes(1, 'big').hex()}",
    [p.hex() for p in proof['accountProof']],
    f"0x{len(proof['storageProof'][0]['proof']).to_bytes(1, 'big').hex()}",
    [p.hex() for p in proof['storageProof'][0]['proof']],
])
with open("proof.txt", "w") as file:
    file.write(f"Token: {token_address}\n")
    file.write(f"Address: {user_address}\n")
    file.write(f"Storage Key: {storage_key}\n")
    file.write(f"Block: {block_number}\n")
    file.write(f"State Root: {state_root.hex()}\n")
    file.write(f"Expected Value: {expected_value}\n")
    file.write("Proof:\n")
    file.write(''.join(proof_components))


# Token: 0x5300000000000000000000000000000000000004
# Address: 0xeFaAE8E0381bD4e23CE9A662cfA833Fb4ED916e5
# Storage Keys: ['0xf86d6180b1493b20c1fcd3c308473ef43eeda5f7028675d1bb6adf523bae8a44']
# Block: 1811605
# Proof: AttributeDict({'address': '0x5300000000000000000000000000000000000004', 'accountProof': [HexBytes('0x09107c5b319c932728baf6ba5feeb60d7df192cfc812d05f84750a6c9d0f2efc5214ab8047619bf33fafcb72ae1028d2fe597ccc5ac76e1fe0812c383ca5436004'), HexBytes('0x0921296f847edd6c8079f810f7422d8a824f36045530c075c5592fb55499bd04462321cc8f7b7ed0869d1b16ca455eb277bdaeda0ffcd26c596920e38f0a1d7b72'), HexBytes('0x0912038e378bb5ee81d443dad66a4e9fab50c108891522fca63341828c2aba1a860598f23762d5293f276b70027e8080db3f5d918ec13146089112b7fa9e00f231'), HexBytes('0x091e822b3a8def87f7836fa6e9be6a42ef306516770fd0f29ed0a06da3ee4075530818918e5f6d97804b3f549599fbdce5f277295841c02ac3ee660daa9440c57b'), HexBytes('0x0918b1d08410a94d806bf5d51eed41ae48bcbe91723d55aaad0186a8bc4091ab682a0f8f8a313bc44ac01263ac00b06898a53b43390a596c058214009ac85f62f7'), HexBytes('0x0920b43597b88e67a0760a3b761dad0cf3c32b75d954a59981dababb5abdcb9916301d4e1f5f67ce05ad2f09efed16927a30458fb7c7a3f7d3fa07b5c420ab4188'), HexBytes('0x0921acf809dfef6bf01ec89dbdddc606f6987b8d5f19753fe39a15ec79943c77b605373641b290062c27936ae02be9833b51367853227518c1327406c73c91bd4c'), HexBytes('0x0913bfefb691169549ba2cdf7cf19515627172ecf7ce8b2c288a06207064e6436f01fcaa48ecbe1675575f924282d3a6e125ac21fae7f75032622513d06f288fa3'), HexBytes('0x092e6bcd3ea1ca88a5cb08dc72d3b87c42089a65a3b9d494ab748e109598514d451e08d90a30c6dccf8d04275a04a17562f8388b69e43a99bcad00f39f04dca414'), HexBytes('0x092c693962f047e0fd428a4e0ca903b53b2503ab1a27a8419d1b057c7a5ce96f5011b1b45ddd0ece4a8f833cba2e2241128b5cef5c18c1124d007170bdb1ef7938'), HexBytes('0x092d502f5b67ca3f32eb2a00a59f8d7b90b4493bf1f48cf69299308296359752542b23bc39b5151c6d39d1420301ccf8cafe69b0caf6b462576522c0f1e8604d8e'), HexBytes('0x091d2f2490510216f0f713c3b2e41c8496559e64315a19269a427643f4381c852911c914335511ae5732e996802540f281c64931c77dcb8df66c246c244d36eb95'), HexBytes('0x0907b237744408280c7df01fa9e85a0e59efdb1498ac798a5976c2d8b96c86aac02f4e76d5d8ba821ec86ea8361496f323c6dcb82d4d8edade6173db08642df373'), HexBytes('0x092dc0a196a746469c35ee149b5a739eea564a06e36f095b651947f8ac0987f72e2d586fd0288f48a9c258ef70f1c356913606881d99b2d231352b852de2ea89ee'), HexBytes('0x091ceea8f062f919d5651e279c4273cbb247f6e9cb3a82fe739f39b5029af4be8a269700a9610c9de4e3b50eebc57ce97279b5dd018273c827b8e010adc9a66c3c'), HexBytes('0x092741293b36431ba0b917d49ba968e68a44967630a799527c47fd8d842654d8a716d13a09eb31861c383b338b2ab2c497ea8de6080b45741988041e25564826ad'), HexBytes('0x091ee32e1c846d536124dae382bf539eb74bc713aebc98d458b42ad2ba94bc92fa0d92e7a5e8f202fc996eceacf4f02529a6ec57939ad0949b34d36ea24dca401f'), HexBytes('0x090949d22aa9f5a8e5fc5ca6bd6b262fe6001364a6f9087863f8c00b1121b853a81ba34a9a7e3f63397f53d0fb8ecd84899e2a58f1ab9c91e12e0ac4e5f5c29448'), HexBytes('0x092f32161bef25bd83951e59fae0fb6560478372d90151c4ec00a1699c9fee6a4821bc0532d4a6554eadceec15d8e33aa2bbdc525b9265766e3099b235ac6fc4b4'), HexBytes('0x092303c766f482c97a43a8a21fc824e7e0daeb7347489d8a4a463aee7b8dbb2ec60feb1211e5aa8ea92d38557caa48e67b342440abbb32b42cf5953f77d63a5195'), HexBytes('0x080995c6e8d5de483bba1d8191a29856fad9c98dbf45791c500aa683b2a750321c0a5029a62ddc14c9c07c549db300bd308b6367454966c94b8526f4ceed5693b2'), HexBytes('0x08168e06970599dabe80522f77c7507a405d9b59e3ece893b2acd35222258a429a0000000000000000000000000000000000000000000000000000000000000000'), HexBytes('0x06181314c9580d02be83b4d6b5c3b4bbbb33309c5832d823534a943dcc5550175821fb69ccdb00e6eaeaf7fc1e73630f39f846970b72ac801e396da0033fb0c247'), HexBytes('0x0420e9fb498ff9c35246d527da24aa1710d2cc9b055ecf9a95a8a2a11d3d836cdf050800000000000000000000000000000000000000000000000016ef000000000000000000000000000000000000000000000000000000000000004a08e20056da5fe01c1a8083b0af6f244ccf84353c1e129229ffafcaeb9d720a96d6852c4e0d6cfca7e8c4073351c26b9831c1e5af153b9be4713a4af9edfdf32b58077b735e120f14136a7980da529d9e8d3a71433fc9dc5aa8c01e3a4eb60cb3a4f9cf9ca5c8e0be205300000000000000000000000000000000000004000000000000000000000000'), HexBytes('0x5448495320495320534f4d45204d4147494320425954455320464f5220534d54206d3172525867503278704449')], 'balance': 1365699135924577755164, 'poseidonCodeHash': '0x136a7980da529d9e8d3a71433fc9dc5aa8c01e3a4eb60cb3a4f9cf9ca5c8e0be', 'keccakCodeHash': '0xe8c4073351c26b9831c1e5af153b9be4713a4af9edfdf32b58077b735e120f14', 'codeSize': '0x16ef', 'nonce': 0, 'storageHash': HexBytes('0x1a8083b0af6f244ccf84353c1e129229ffafcaeb9d720a96d6852c4e0d6cfca7'), 'storageProof': [AttributeDict({'key': HexBytes('0xf86d6180b1493b20c1fcd3c308473ef43eeda5f7028675d1bb6adf523bae8a44'), 'value': HexBytes('0x0a0cedc1bf2ddf96f0'), 'proof': [HexBytes('0x090632c79f2dd1b488e601021af679c005478313a2e7259e22249050d2b2a429e50c118fe11cbe5bd369c40f17395350c1995b955ee96a169ead05127f0b2cb7eb'), HexBytes('0x0901b9dbda41617e0d2ad40769e3cd6f34d1717d982d45800300a6d57b2ffb314415dcb4306dbc98959e1d8418319e55863ef4b3e78b3f0104fbc4b775e6716929'), HexBytes('0x0919ce1f420e58c826ace7cd3e65273a795e529354504d03e8a23f8c69fd0a79721630f62b50967d8fbdc6a605c6dde6d6b60922d3f738df10f375731e019990fe'), HexBytes('0x0904d6783e37319dd5d0616bb20417ae1a415c6b1f85f6e6fa6b8ecf129b731fdc2d63664f30d03d565c9c1f49b1c52642e68da50c138cb6c2720d7bb62a9dec55'), HexBytes('0x092a39f1ad1aec3ef4e4cce29d253087bb193e134f37e7de537a145d540038e47d1df8e64be5408042562bdd08f620ccae979a3c31f85a564be210b7438820ad2b'), HexBytes('0x091adbb9e4362cc3e5a2066ca3ef5d6a8104b920eb1d07c4e6433d7629b4deeb2a22bf1a7dbb9ef0a5e2e82e323426310763a2e6c67674b6d433fe49e5bc9ae708'), HexBytes('0x0928ca9a9c2a4fece8bb5ef1cf72c57c24451d7a5e275caacfabbf4637d08fe49a0bbbbf166769a0f5dbfde19abf0c8696682bb260861412917c69b8a4a8812ce0'), HexBytes('0x0919a2b0e04c01590f1d67e2e67038a866670e7d98886ceca3ab6227186c6660bf015e4e7609534574fb7e304a60304788c5f0d1f3b871bac3900f080bd3bcea72'), HexBytes('0x0902ac93a3af23e248b733d7947bb52fbdcff1976bdfe51f0b221296465672b62f2e097bacf09e869346a6f9997cd2d5e8dfdb841cd221fc07944e932e0ceb6fc3'), HexBytes('0x091bb0c1991b583ef7d8d71b1e7f5ff0104c756466b85fafa78ee958f5e95b36af176ec7f5ed9458246d5a023f10e76346868f6f1093b5712616f9c48d1774a6bf'), HexBytes('0x09262c6329327fe833ea41f321738ae64b47c7d6da7aca3ba56f921178f8b4df6810f21607c4111394ff4162530713e527baf0b8f34f4f5e7c4520e8542a861c6e'), HexBytes('0x0900a9a2647094f382940998e7129b4b7ca98d133a5428f03fbe1e707c75b2f8e628e38743b8b581eca53437c6ae55bcff356ea1965fe93e8c5544b6343200d760'), HexBytes('0x092f6543396bc4dc66e6b4ce78614515f8b4c211713a667d8be90897553323d03d014a0ef9b6242c6ae2ce09a4497912c1bb1f1371c5db2a75097cf23b1721f1b8'), HexBytes('0x091443d67c45fe0bf735b373b45a391f1b3a4969774afa381d5fdc0ea5ff4f3dee2a53e45df04009261ca20b175b1915079055156b5d886e9b053cba53dacc815e'), HexBytes('0x08183bf8115c24334272f7d4e00dd47c00f4b16c54821ab6391dafed3318dba9700000000000000000000000000000000000000000000000000000000000000000'), HexBytes('0x081fafbb2c88b791d9ab8a686ca5415ef0b10640a9ea012928ee5f97c59c18cd221b27c16c7f02e182fc1fac19c895bb9f0395fce40ea7373aed1f08e60d602a00'), HexBytes('0x0802188485173020cf18378421012cd2173b243a42f5148556e72f0c5bc184cd2e0000000000000000000000000000000000000000000000000000000000000000'), HexBytes('0x0601333eafccf8f03029ff6d0809fe8550726d30ccd090b9e90508ce7afc987e072c4691ee3df7c467feb19890c9aa2c9c8652cf27941d16faba116ed6f156afe7'), HexBytes('0x0411adc0cd78ed236bc6b243aa858a8c6b4ed664e8e07e3ba26f7042a7b18401540101000000000000000000000000000000000000000000000000000a0cedc1bf2ddf96f020f86d6180b1493b20c1fcd3c308473ef43eeda5f7028675d1bb6adf523bae8a44'), HexBytes('0x5448495320495320534f4d45204d4147494320425954455320464f5220534d54206d3172525867503278704449')]})]})

