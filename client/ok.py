import can

def list_pcan_channels():
    try:
        # Create a Bus instance with no specific channel to list all available ones
        # This works with PCANBasic, but python-can doesn't expose a direct list_channels for pcan
        # So we try to open known common channels and check if they are available
        possible_channels = [
            "PCAN_USBBUS1",
            "PCAN_USBBUS2",
            "PCAN_USBBUS3",
            "PCAN_USBBUS4",
            "PCAN_PCIBUS1",
            "PCAN_PCIBUS2",
            "PCAN_LANBUS1",
        ]

        available_channels = []
        for ch in possible_channels:
            try:
                bus = can.Bus(channel=ch, interface='pcan')
                available_channels.append(ch)
                bus.shutdown()
            except can.CanError:
                # Can't open this channel, ignore
                pass

        print("Available PCAN channels found:")
        for ch in available_channels:
            print(f" - {ch}")
        if not available_channels:
            print("No PCAN channels detected. Please check device connection and drivers.")
    except Exception as e:
        print("Error detecting PCAN channels:", e)

if __name__ == "__main__":
    list_pcan_channels()

