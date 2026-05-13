from flask import Flask, render_template, request, redirect, url_for
import json
import os
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes
import requests
from time import time

app = Flask(__name__)

# Load existing seed phrases or initialize
SEED_FILE = "seed_phrases.json"
LOG_FILE = "wallet_balances.json"

if not os.path.exists(SEED_FILE):
    with open(SEED_FILE, "w") as file:
        json.dump([], file)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        json.dump([], file)

def fetch_seeds():
    with open(SEED_FILE, "r") as file:
        return json.load(file)

def save_seeds(seeds):
    with open(SEED_FILE, "w") as file:
        json.dump(seeds, file, indent=4)

def fetch_logs():
    with open(LOG_FILE, "r") as file:
        return json.load(file)

def save_logs(logs):
    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)

@app.route("/")
def index():
    seeds = fetch_seeds()
    logs = fetch_logs()
    return render_template("index.html", seeds=seeds, logs=logs)

@app.route("/generate_seed", methods=["POST"])
def generate_seed():
    mnemonic_generator = Mnemonic("english")
    new_seed = mnemonic_generator.generate(128)
    seeds = fetch_seeds()

    seeds.append({"seed": new_seed, "used": False, "timestamp": time()})
    save_seeds(seeds)

    return redirect(url_for("index"))

@app.route("/check_balance/<int:seed_index>")
def check_balance(seed_index):
    seeds = fetch_seeds()
    seed_data = seeds[seed_index]
    seed_phrase = seed_data["seed"]

    # Derive the first wallet address from the seed phrase
    bip44_mst = Bip44.FromMnemonic(seed_phrase, Bip44Coins.BITCOIN)
    wallet = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    wallet_address = wallet.PublicAddress()

    # Check balance via blockchain API
    balance = fetch_wallet_balance(wallet_address)

    # Update logs and mark seed as used
    logs = fetch_logs()
    logs.append({"seed": seed_phrase, "wallet_address": wallet_address, "balance": balance, "timestamp": time()})
    save_logs(logs)

    seeds[seed_index]["used"] = True
    save_seeds(seeds)

    return redirect(url_for("index"))

def fetch_wallet_balance(address):
    url = f"https://blockchain.info/q/addressbalance/{address}"
    response = requests.get(url)
    if response.status_code == 200:
        return int(response.text) / 10**8  # Convert Satoshis to BTC
    return 0.0

if __name__ == "__main__":
    app.run(debug=True)