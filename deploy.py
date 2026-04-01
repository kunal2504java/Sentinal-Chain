"""Deploy the EventLogger contract to Avalanche."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3


def compile_contract(contract_path: Path) -> tuple[list[dict], str]:
    """Compile the Solidity contract and return its ABI and bytecode."""
    source = contract_path.read_text(encoding="utf-8")
    install_solc("0.8.20")
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {contract_path.name: {"content": source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode.object"],
                    }
                }
            },
        },
        solc_version="0.8.20",
    )
    contract_data = compiled["contracts"][contract_path.name]["EventLogger"]
    return contract_data["abi"], contract_data["evm"]["bytecode"]["object"]


def main() -> None:
    """Compile and deploy the EventLogger contract."""
    load_dotenv()

    rpc_url = os.getenv("RPC_URL", "https://api.avax-test.network/ext/bc/C/rpc")
    chain_id = int(os.getenv("CHAIN_ID", "43113"))
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY is required to deploy the contract.")

    contract_path = Path("chain") / "EventLogger.sol"
    abi_path = Path("chain") / "abi.json"
    abi, bytecode = compile_contract(contract_path)
    abi_path.write_text(json.dumps(abi, indent=2), encoding="utf-8")

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise ConnectionError(f"Unable to connect to RPC at {rpc_url}")

    account = web3.eth.account.from_key(private_key)
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = web3.eth.get_transaction_count(account.address)
    transaction = contract.constructor().build_transaction(
        {
            "chainId": chain_id,
            "from": account.address,
            "nonce": nonce,
            "gas": 1500000,
            "gasPrice": web3.eth.gas_price,
        }
    )
    signed = account.sign_transaction(transaction)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt["contractAddress"]
    explorer_base = "https://testnet.snowtrace.io/address"
    if chain_id == 43114:
        explorer_base = "https://snowtrace.io/address"

    print(f"Contract deployed at: {contract_address}")
    print(f"Explorer URL: {explorer_base}/{contract_address}")
    print("Set CONTRACT_ADDRESS in .env to the deployed address before running the logger.")


if __name__ == "__main__":
    main()
