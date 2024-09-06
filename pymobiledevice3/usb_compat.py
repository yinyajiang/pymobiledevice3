import sys

if sys.platform.startswith('win'):
    from pymobiledevice3.usb_win import get_string, Device, USBError, find
elif sys.platform.startswith('darwin'):
    from pymobiledevice3.usb_mac import get_string, Device, USBError, find
else:
    from usb.core import Device, USBError, find
    from usb.util import get_string

__all__ = ["Device", "USBError", "find", "get_string"]