"""DoHome device discovery example"""

from asyncio import run
from dohome import discover, UDPBroadcast

async def main():
    """Example entrypoint"""
    broadcast = UDPBroadcast()
    devices = await discover(broadcast)
    if not devices:
        print("No devices found")
        return

    print(f"Found {len(devices)} devices")
    for device in devices:
        print(f"{device['sta_ip']} {device['device_id']}")

    # Close the UDP broadcast socket
    broadcast.close()

if __name__ == '__main__':
    run(main())
