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
        if web3.is_connected():
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] - 🔍 Memeriksa gas fee...")

            gas_price = web3.eth.gas_price
            gas_in_gwei = web3.from_wei(gas_price, 'gwei')
            print(f"⛽ Harga gas saat ini: {gas_in_gwei} GWEI")

            if gas_in_gwei < 0.5:
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


def check_user_info(token):
    url = "https://api.volara.xyz/v1/user/stats"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            index_stats = data.get("data", {}).get("indexStats", {}).get("totalIndexedTweets", "N/A")
            vortex_score = data.get("data", {}).get("rewardStats", {}).get("vortexScore", "N/A")
            vortex_rank = data.get("data", {}).get("rankStats", {}).get("vortexRank", "N/A")
            
            print(f"\n📊 Informasi Pengguna:")
            print(f"📈 Total Indexed Tweets: {index_stats}")
            print(f"🏅 Vortex Score: {vortex_score}")
            print(f"🏆 Vortex Rank: {vortex_rank}")
        else:
            print("❌ Gagal mendapatkan data pengguna.")
            print(f"🚩 Respons: {response.json()}")
    except Exception as e:
        print(f"❗ Kesalahan saat mengambil data pengguna: {e}")


def run_checks():
    token = load_token()
    if not token:
        token = input("🔑 Masukkan token API Anda: ")
        save_token(token)
        print("✅ Token disimpan!")

    while True:
        check_gas_fee()
        check_user_info(token)
        time.sleep(30)


run_checks()
