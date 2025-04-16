import asyncio
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

def print_handler(address, *args):
    print(f"Received OSC: {address} {args}")

async def main():
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(print_handler)

    server = AsyncIOOSCUDPServer(("0.0.0.0", 9000), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()
    print("Listening for OSC messages on port 9000...")
    await asyncio.sleep(3600)
    transport.close()

asyncio.run(main())