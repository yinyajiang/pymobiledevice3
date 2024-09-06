import re
from ctypes import (byref, c_wchar_p,
                    create_string_buffer, sizeof, memmove, cast, POINTER, Structure, c_uint8, c_uint16,
                    windll, c_ubyte, c_ulong, c_ushort, c_void_p, resize, wstring_at)
from ctypes.wintypes import (DWORD, LPVOID, HWND, PDWORD, ULONG, WCHAR, BOOL, HANDLE, LPCWSTR, LPDWORD,
                             LPWSTR)
import usb.core as core

USBError = core.USBError


# *****************kernel32 api********************


class USBControlRequest(Structure):
    _fields_ = [
        ("bmRequestType", c_uint8),
        ("bRequest", c_uint8),
        ("wValue", c_uint16),
        ("wIndex", c_uint16),
        ("wLength", c_uint16),
    ]


class OVERLAPPED(Structure):
    _fields_ = [
        ('Internal', LPVOID),
        ('InternalHigh', LPVOID),
        ('Offset', DWORD),
        ('OffsetHigh', DWORD),
        ('hEvent', HANDLE),
    ]


LPOVERLAPPED = POINTER(OVERLAPPED)

GetLastError = windll.kernel32.GetLastError
GetLastError.restype = DWORD
GetLastError.argtypes = []

CreateFile = windll.kernel32.CreateFileW
CreateFile.restype = HANDLE
CreateFile.argtypes = [
    LPCWSTR,
    DWORD,
    DWORD,
    LPVOID,
    DWORD,
    DWORD,
    HANDLE,
]

CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = [HANDLE]
CloseHandle.restype = BOOL

DeviceIoControl = windll.kernel32.DeviceIoControl
DeviceIoControl.restype = BOOL
DeviceIoControl.argtypes = [
    HANDLE,
    DWORD,
    LPVOID,
    DWORD,
    LPVOID,
    DWORD,
    LPDWORD,
    LPVOID,
]

CancelIo = windll.kernel32.CancelIo
CancelIo.argtypes = [HANDLE]
CancelIo.restype = BOOL

GetOverlappedResult = windll.kernel32.GetOverlappedResult
GetOverlappedResult.argtypes = [HANDLE, LPOVERLAPPED, LPDWORD, BOOL]
GetOverlappedResult.restype = BOOL

WaitForSingleObject = windll.kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = [HANDLE, DWORD]
WaitForSingleObject.restype = DWORD

CreateEvent = windll.kernel32.CreateEventW
CreateEvent.argtypes = [LPVOID, BOOL, BOOL, LPWSTR]
CreateEvent.restype = HANDLE

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_FLAG_OVERLAPPED = 0x40000000


# *************setupapi****************************

class GUID(Structure):
    _fields_ = [
        ("Data1", c_ulong),
        ("Data2", c_ushort),
        ("Data3", c_ushort),
        ("Data4", c_ubyte * 8),
    ]


class SP_DEVICE_INTERFACE_DATA(Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("InterfaceClassGuid", GUID),
        ("Flags", DWORD),
        ("Reserved", POINTER(ULONG)),
    ]


class SP_DEVICE_INTERFACE_DETAIL_DATA(Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("DevicePath", WCHAR * 1),
    ]


class SP_DEVINFO_DATA(Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("ClassGuid", GUID),
        ("DevInst", DWORD),
        ("Reserved", POINTER(ULONG)),
    ]


SetupDiGetClassDevs = windll.setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.restype = HANDLE
SetupDiGetClassDevs.argtypes = [
    POINTER(GUID),
    LPCWSTR,
    HWND,
    DWORD,
]

SetupDiDestroyDeviceInfoList = windll.setupapi.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.restype = BOOL
SetupDiDestroyDeviceInfoList.argtypes = [HANDLE]

SetupDiEnumDeviceInfo = windll.setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.restype = BOOL
SetupDiEnumDeviceInfo.argtypes = [
    HANDLE,
    DWORD,
    POINTER(SP_DEVINFO_DATA),
]

SetupDiEnumDeviceInterfaces = windll.setupapi.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.restype = BOOL
SetupDiEnumDeviceInterfaces.argtypes = [
    HANDLE,
    c_void_p,
    POINTER(GUID),
    DWORD,
    POINTER(SP_DEVICE_INTERFACE_DATA),
]

SetupDiGetDeviceInterfaceDetail = windll.setupapi.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.restype = BOOL
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HANDLE,
    POINTER(SP_DEVICE_INTERFACE_DATA),
    POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA),
    DWORD,
    POINTER(DWORD),
    POINTER(SP_DEVINFO_DATA),
]

SetupDiGetDeviceRegistryProperty = windll.setupapi.SetupDiGetDeviceRegistryPropertyW
SetupDiGetDeviceRegistryProperty.restype = BOOL
SetupDiGetDeviceRegistryProperty.argtypes = [
    HANDLE,
    POINTER(SP_DEVINFO_DATA),
    DWORD,
    PDWORD,
    c_void_p,
    DWORD,
    PDWORD,
]

DIGCF_PRESENT = 2
DIGCF_DEVICEINTERFACE = 16

GUID_DEVINTERFACE_IBOOT = GUID(
    0xED82A167,
    0xD61A,
    0x4AF6,
    (c_ubyte * 8)(0x9A, 0xB6, 0x11, 0xE5, 0x22, 0x36, 0xC5, 0x76),
)

GUID_DEVINTERFACE_DFU = GUID(
    0xB8085869,
    0xFEB9,
    0x404B,
    (c_ubyte * 8)(0x8C, 0xB1, 0x1E, 0x5C, 0x14, 0xFA, 0x8C, 0x54),
)

GUID_DEVINTERFACE_KIS = GUID(
    0xB36F4137,
    0xF4EF,
    0x4BFC,
    (c_ubyte * 8)(0xA2, 0x5A, 0xC2, 0x41, 0x07, 0x68, 0xEE, 0x37),
)

GUID_DEVINTERFACE_PORTDFU = GUID(
    0xAF633FF1,
    0x1170,
    0x4CA6,
    (c_ubyte * 8)(0xAE, 0x9E, 0x08, 0xD0, 0x01, 0x42, 0x1E, 0xAA),
)


def findDevicesPathBySetup(
    guids=[
        GUID_DEVINTERFACE_IBOOT,
        GUID_DEVINTERFACE_DFU,
        GUID_DEVINTERFACE_KIS,
        GUID_DEVINTERFACE_PORTDFU,
    ],
    flags=DIGCF_PRESENT | DIGCF_DEVICEINTERFACE,
):
    devicePaths = []

    for guid in guids:
        dev_info = SetupDiGetClassDevs(byref(guid), None, None, flags)

        if dev_info == -1:
            raise Exception("SetupDiGetClassDevs failed")

        try:
            cb_sizes = (8, 6, 5)
            index = 0
            while True:
                dev_interface_data = SP_DEVICE_INTERFACE_DATA()
                dev_interface_data.cbSize = sizeof(SP_DEVICE_INTERFACE_DATA)

                dev_info_data = SP_DEVINFO_DATA()
                dev_info_data.cbSize = sizeof(SP_DEVINFO_DATA)

                if not SetupDiEnumDeviceInterfaces(
                    dev_info,
                    None,
                    byref(guid),
                    index,
                    byref(dev_interface_data),
                ):
                    break

                required_size = DWORD(0)
                SetupDiGetDeviceInterfaceDetail(
                    dev_info,
                    byref(dev_interface_data),
                    None,
                    0,
                    byref(required_size),
                    None,
                )

                detail_data = SP_DEVICE_INTERFACE_DETAIL_DATA()
                resize(detail_data, required_size.value)

                path = None
                for cb_size in cb_sizes:
                    detail_data.cbSize = cb_size
                    ret = SetupDiGetDeviceInterfaceDetail(
                        dev_info,
                        byref(dev_interface_data),
                        byref(detail_data),
                        required_size,
                        byref(required_size),
                        byref(dev_info_data),
                    )
                    if ret:
                        cb_sizes = (cb_size,)
                        path = wstring_at(
                            byref(detail_data, sizeof(DWORD)),
                        )
                        break
                if path:
                    devicePaths.append(path)
                index += 1
        finally:
            SetupDiDestroyDeviceInfoList(dev_info)
        return devicePaths


class Device:
    def __init__(self, device_path):
        self.device_path = device_path
        self.handle = None
        self.manufacturer = None
        self.serial_number = None
        self.idProduct = None
        self.idVendor = None
        self._parse_serial_number()
        if self.idProduct:
            self._open_device()

    def _open_device(self):
        self.handle = CreateFile(
            c_wchar_p(self.device_path),
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_FLAG_OVERLAPPED,
            None,
        )

        if not self.handle or self.handle == -1:
            self.handle = None
            raise USBError(
                f"CreateFileW({
                    self.device_path}) fail, LastError:{
                    GetLastError()}")

    def _parse_serial_number(self):
        match = re.search(
            r'\\usb#vid_([0-9a-fA-F]{4})&pid_([0-9a-fA-F]{4})#(.+)',
            self.device_path)
        if not match or len(match.groups()) != 3:
            return

        self.idVendor = int(match.group(1), 16)
        if self.idVendor == 0x05ac:
            self.manufacturer = 'Apple Inc.'
        else:
            self.manufacturer = 'Unknown'
        self.idProduct = int(match.group(2), 16)

        serial = match.group(3)
        self.serial_number = ''
        for kv in serial.replace(
                '_', ' ').replace(
                '#', ' ').upper().split(' '):
            if ':' in kv:
                if self.serial_number:
                    self.serial_number += ' '
                self.serial_number += kv

    def set_interface_altsetting(self, interface, alternate_setting):
        if self.ctrl_transfer(0, 0x0B, alternate_setting, interface) < 0:
            raise USBError("Failed to set interface altsetting")

    def get_active_configuration(self):
        buf = self.ctrl_transfer(0x80, 0x08, 0, 0, 1)
        if len(buf) != 1:
            raise USBError("Failed to get active configuration")

        class CONFIGURATION:
            pass
        cfg = CONFIGURATION()
        cfg.bConfigurationValue = int.from_bytes(buf, "little")
        return cfg

    def set_configuration(self, configuration):
        self.ctrl_transfer(0, 0x09, configuration, 0)

    def get_string_descriptor(self, index, langid=None):
        langid = langid if langid else 0x0409
        response = self.ctrl_transfer(
            0x80, 0x06, (3 << 8) | index, langid, 255)
        if response and len(response) >= 2:
            return response[2:].decode('utf-16-le')
        else:
            raise USBError("get_string_descriptor: invalid response from ctrl_transfer")

    def ctrl_transfer(
        self,
        bmRequestType,
        bRequest,
        wValue=0,
        wIndex=0,
        data_or_wLength=None,
        timeout=None,
    ):
        if data_or_wLength is None:
            wLength = 0
            data = None
        elif isinstance(data_or_wLength, int):
            wLength = data_or_wLength
            data = None
        else:
            wLength = len(data_or_wLength)
            data = data_or_wLength
        if data:
            data = data if isinstance(data, bytes) else bytes(data)

        packet = USBControlRequest()
        packet.bmRequestType = bmRequestType
        packet.bRequest = bRequest
        packet.wValue = wValue
        packet.wIndex = wIndex
        packet.wLength = wLength
        buffer = create_string_buffer(sizeof(USBControlRequest) + wLength)

        memmove(buffer, byref(packet), sizeof(USBControlRequest))

        if bmRequestType < 0x80 and wLength > 0:
            memmove(byref(buffer, sizeof(USBControlRequest)), data, wLength)

        bytes_returned = self._device_io_control_overlapped(
            0x2200A0,
            buffer,
            len(buffer),
            buffer,
            len(buffer),
            timeout,
        )

        bytes_returned = bytes_returned - sizeof(USBControlRequest)
        if bytes_returned > 0 and bmRequestType >= 0x80:
            memmove(buffer, byref(buffer, sizeof(
                USBControlRequest)), bytes_returned)
            return buffer[0:bytes_returned]
        else:
            return bytes_returned

    def write(self, endpoint, data, timeout=None):
        if endpoint != 0x4:
            return 0

        # bytes_returned = DWORD(0)
        # DeviceIoControl(
        #     self.handle,
        #      0x2201B6,
        #     cast(data, LPVOID),
        #     len(data),
        #     cast(data, LPVOID),
        #     len(data),
        #     byref(bytes_returned),
        #     None,
        # )
        # return len(data)
        return self._device_io_control_overlapped(
            0x2201B6,
            cast(data, LPVOID),
            len(data),
            cast(data, LPVOID),
            len(data),
            timeout)

    def reset(self):
        DeviceIoControl(
            self.handle,
            0x22000C,
            None,
            0,
            None,
            0,
            None,
            None,
        )

    def close(self):
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None

    def __del__(self):
        self.close()

    def _device_io_control_overlapped(self,
                                      dwIoControlCode: DWORD,
                                      lpInBuffer: LPVOID,
                                      nInBufferSize: DWORD,
                                      lpOutBuffer: LPVOID,
                                      nOutBufferSize: DWORD,
                                      timeout=None,
                                      bWait=False,
                                      ):

        overlapped = OVERLAPPED()
        overlapped.hEvent = CreateEvent(None, True, False, None)
        overlapped.Internal = None
        overlapped.InternalHigh = None
        overlapped.Offset = 0
        overlapped.OffsetHigh = 0

        result = DeviceIoControl(
            self.handle,
            dwIoControlCode,
            lpInBuffer,
            nInBufferSize,
            lpOutBuffer,
            nOutBufferSize,
            None,
            byref(overlapped),
        )
        WaitForSingleObject(overlapped.hEvent, timeout or 10000)
        bytes_returned = DWORD(0)
        result = GetOverlappedResult(self.handle, byref(
            overlapped), byref(bytes_returned), bWait)

        if not result:
            lastError = GetLastError()
            CancelIo(self.handle)
            CloseHandle(overlapped.hEvent)
            overlapped = None
            raise USBError(f"Failed to ctrl_transfer, last error: {lastError}")
        CloseHandle(overlapped.hEvent)
        overlapped = None
        return bytes_returned.value


def find(*_, **__):
    devices = []
    for path in findDevicesPathBySetup():
        devices.append(Device(path))
    return devices


def get_string(device, index, langid=None):
    return device.get_string_descriptor(index, langid)

__all__ = ["Device", "USBError", "find", "get_string"]

