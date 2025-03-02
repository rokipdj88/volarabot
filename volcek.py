import time
import subprocess
import requests
from web3 import Web3
from datetime import datetime
import os

# Logo
logo = '''
$$\   $$\ $$$$$$$$\      $$$$$$$$\           $$\                                       $$\     
$$$\  $$ |\__$$  __|     $$  _____|          $$ |                                      $$ |    
$$$$\ $$ |   $$ |        $$ |      $$\   $$\ $$$$$$$\   $$$$$$\  $$\   $$\  $$$$$$$\ $$$$$$\   
$$ $$\$$ |   $$ |$$$$$$\ $$$$$\    \$$\ $$  |$$  __$$\  \____$$\ $$ |  $$ |$$  _____|\_$$  _|  
$$ \$$$$ |   $$ |\______|$$  __|    \$$$$  / $$ |  $$ | $$$$$$$ |$$ |  $$ |\$$$$$$\    $$ |    
$$ |\$$$ |   $$ |        $$ |       $$  $$<  $$ |  $$ |$$  __$$ |$$ |  $$ | \____$$\   $$ |$$\ 
$$ | \$$ |   $$ |        $$$$$$$$\ $$  /\$$\ $$ |  $$ |\$$$$$$$ |\$$$$$$  |$$$$$$$  |  \$$$$  |
\__|  \__|   \__|        \________|\__/  \__|\__|  \__| \_______| \______/ \_______/    \____/ 

Join our Telegram channel: https://t.me/NTExhaust 🚀
'''

print(logo)

# RPC VANA
vana_rpc_url = "https://rpc.vana.org"
web3 = Web3(Web3.HTTPProvider(vana_rpc_url))

# Load custom gas fee limit
def load_gas_limit():
    try:
        if os.path.exists("gas_limit.txt"):
            with open("gas_limit.txt", "r") as file:
                return float(file.read().strip())
    except:
        pass
    return 0.5  # Default gas fee


def save_gas_limit(limit):
    with open("gas_limit.txt", "w") as file:
        file.write(str(limit))


def save_token(token):
    with open("token.txt", "w") as file:
        file.write(token)


def load_token():
    if os.path.exists("token.txt"):
        with open("token.txt", "r") as file:
            return file.read().strip()
    return None


def check_docker_status(container_name):
    result = subprocess.run(["docker", "ps", "-q", "-f", f"name={container_name}"], capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip() != ""


def check_gas_fee():
    try:
        gas_limit = load_gas_limit()
        if web3.is_connected():
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] - 🔍 Memeriksa gas fee...")

            gas_price = web3.eth.gas_price
            gas_in_gwei = web3.from_wei(gas_price, 'gwei')
            print(f"⛽ Harga gas saat ini: {gas_in_gwei} GWEI (Batas: {gas_limit} GWEI)")

            if gas_in_gwei <= gas_limit:
                print("✅ Gas fee rendah")
                if not check_docker_status("volara_miner"):
                    result = subprocess.run(["docker", "start", "volara_miner"], capture_output=True, text=True)
                    if result.returncode == 0:
                        print("🚀 Docker container volara_miner berhasil dijalankan.")
                    else:
                        print("❌ Gagal menjalankan docker container volara_miner.")
                else:
                    print("🔒 Docker container volara_miner sudah berjalan.")
            else:
                print("⚠️ Gas fee tinggi")
                if check_docker_status("volara_miner"):
                    result = subprocess.run(["docker", "stop", "volara_miner"], capture_output=True, text=True)
                    if result.returncode == 0:
                        print("🛑 Docker container volara_miner berhasil dihentikan.")
                    else:
                        print("❌ Gagal menghentikan docker container volara_miner.")
                else:
                    print("🔓 Docker container volara_miner sudah dihentikan.")
        else:
            print("❗ Gagal terhubung ke jaringan Vana")
    except Exception as e:
        print(f"❗ Kesalahan: {e}")


def run_checks():
    token = load_token()
    if not token:
        token = input("🔑 Masukkan token API Anda: ")
        save_token(token)
        print("✅ Token disimpan!")

    gas_limit = input("⚙️ Masukkan batas gas fee (GWEI, default 0.5): ")
    if gas_limit:
        save_gas_limit(float(gas_limit))
        print(f"✅ Batas gas fee disimpan: {gas_limit} GWEI")
    else:
        print(f"ℹ️ Menggunakan batas gas fee default: {load_gas_limit()} GWEI")

    while True:
        check_gas_fee()
        time.sleep(30)


run_checks()
