const {Web3} = require("web3");
const { keccak256, toHex, toBN } = require("web3-utils");
const HttpProviderOptions = require("web3-core-helpers").HttpProviderOptions;
const Contract = require("web3-eth-contract").Contract;
const BlockTransactionString = require("web3-eth").BlockTransactionString;
const ethers = require("ethers");

const concat = ethers.concat;

 // Initialize web3 instance with HttpProvider
const url ='https://sepolia-rpc.scroll.io';
const httpProvider = new Web3.providers.HttpProvider(url);
const w3 = new Web3(httpProvider);

const block_number = 2721258;
const token_address = '0x5300000000000000000000000000000000000004' // weth address 
const user_address = '0x7739e567b9626ca241bdc5528343f92f7e59af37' // whale on scroll sepolia

/*
  Goal is to get the user's balance storage proof and verify it on the verifier contract (https://sepolia.scrollscan.dev/address/0x092bfFf60A8942d2cAb4D12c7aF862bF74abADE5)
*/

 async function get_state_root(block_number) {
   const block = await w3.eth.getBlock(block_number);
   const state_root = block.stateRoot;
   console.log(state_root);
   return state_root;
 }

 async function get_storage_key(token_address, user_address, block_number) {
   function remove_0x_prefix(address) {
     return address.startsWith('0x') ? address.slice(2) : address;
   }

   function to_int(hexstr) {
     return parseInt(hexstr, 16);
   }

   for (let i = 0; i < 20; i++) {
     const pos = i.toString(16).padStart(64, '0');
     const key = remove_0x_prefix(user_address).padStart(64, '0').toLowerCase();
     const storage_key = toHex(keccak256('0x' + key + pos));
     const storage_value = to_int(await w3.eth.getStorageAt(token_address, storage_key, block_number));
     if (storage_value !== 0) {
       console.log(`position is ${i}`);
       console.log(`Value at storage key: ${storage_value}`); //verified on scrollyscan
       console.log(storage_key);
       return storage_key;
     }
   }
 }

 async function get_proof(address, storage_keys, block) {
   return w3.eth.getProof(address, storage_keys, block);
 }

 async function verify_proof(contractAddress, storageKey, proof) {
   const verifierAddress = '0xd2feb9a618bccab6521053dce63d2bfe855afdd9';
   const verifier = new w3.eth.Contract([
      {"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"bytes32","name":"storageKey","type":"bytes32"},{"internalType":"bytes","name":"proof","type":"bytes"}],"name":"verifyZkTrieProof","outputs":[{"internalType":"bytes32","name":"stateRoot","type":"bytes32"},{"internalType":"bytes32","name":"storageValue","type":"bytes32"}],"stateMutability":"view","type":"function"}
   ], verifierAddress);
   
   const { storageValue } = await verifier.methods.verifyZkTrieProof(contractAddress, storageKey, proof).call();
   return storageValue;
 }

 async function main() {
  const state_root = await get_state_root(block_number); // From your existing code
  const storage_key = await get_storage_key(token_address, user_address, block_number);
  const proof = await get_proof(token_address, [storage_key], block_number);
  // console.log(proof['storageProof']);
  console.log(proof)
  let cleaned_proof = {
    block: block_number,
    account: token_address,
    storage: storage_key,
    expectedRoot: proof.storageHash,
    accountProof: proof.accountProof.map(ap => ap),
    storageProof: proof.storageProof[0].proof.map(sp => sp),
  };

  console.log(cleaned_proof)

  const compiled_proof = concat([
    `0x${cleaned_proof.accountProof.length.toString(16).padStart(2, "0")}`,
    ...cleaned_proof.accountProof,
    `0x${cleaned_proof.storageProof.length.toString(16).padStart(2, "0")}`,
    ...cleaned_proof.storageProof,
  ]);

  console.log(compiled_proof)

  const verified_storage_value = await verify_proof(token_address, proof.storageProof[0].key, compiled_proof);
  console.log(`Verified Storage Value: ${verified_storage_value}`);
 }

 main();