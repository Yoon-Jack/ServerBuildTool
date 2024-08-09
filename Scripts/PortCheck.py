import socket
import threading, time
import requests

global g_gameServerLive
g_gameServerLive = False

class PortChecker:
    def GameServerCheck(self, ip, port):
        addr = (ip, port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)

        try:
            s.connect(addr)
            return True
        except socket.error:
            return False

    def ToolServerCheck(self, ip, port):
        healthz_url = f"http://{ip}:{port}/healthz"
        try:
            response = requests.get(healthz_url, timeout=1)
            return response.status_code == 200
        except requests.RequestException as e:
            return False

    def DoWork(self, ip, port):
        global g_gameServerLive
        while True:
            g_gameServerLive = self.PortCheck(ip, port)
            if g_gameServerLive:
                print("GameServer is live")
            else:
                print("GameServer is dead")
            time.sleep(10)
    
    def Start(self, ip, port):
        worker = threading.Thread(target=self.DoWork, args=(ip, port))
        worker.daemon = True
        worker.start()