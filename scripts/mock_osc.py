from pythonosc.udp_client import SimpleUDPClient

ip = "127.0.0.1"
port = 9000

client = SimpleUDPClient(ip, port)
client.send_message("/control/start", 1)
print("Mock OSC message sent: /control/start 1")