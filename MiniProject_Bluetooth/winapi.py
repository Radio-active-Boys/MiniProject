import ctypes
import uuid

# Define Bluetooth LE device interface GUID
GUID_BLUETOOTHLE_DEVICE_INTERFACE = uuid.UUID("781aee18-7733-4b5d-8b58-f7570bc59dc0")

# Define Bluetooth LE device structure
class BLUETOOTH_LE_DEVICE_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("Address", ctypes.c_ulonglong),
        ("Type", ctypes.c_byte),
        ("Name", ctypes.c_wchar * 256),
    ]

# Load necessary Windows libraries
setupapi = ctypes.windll.LoadLibrary("setupapi")
bthprops = ctypes.windll.LoadLibrary("bthprops.cpl")

# Function to enumerate Bluetooth LE devices
def enumerate_ble_devices():
    ble_devices = []
    size = ctypes.c_ulong()

    # Call SetupDiClassGuidsFromName to get the Bluetooth LE device interface GUID
    setupapi.SetupDiClassGuidsFromNameW("BluetoothLE", None, None, ctypes.byref(size))

    class_guids = (uuid.UUID * size.value)()
    setupapi.SetupDiClassGuidsFromNameW("BluetoothLE", ctypes.byref(class_guids), size, None)

    # Call SetupDiGetClassDevs to get a device information set for Bluetooth LE devices
    device_info_set = setupapi.SetupDiGetClassDevsW(
        ctypes.byref(class_guids[0]), None, None, setupapi.DIGCF_PRESENT
    )

    if device_info_set != setupapi.INVALID_HANDLE_VALUE:
        device_info = BLUETOOTH_LE_DEVICE_INFO()
        device_info.dwSize = ctypes.sizeof(BLUETOOTH_LE_DEVICE_INFO)

        index = 0
        while setupapi.SetupDiEnumDeviceInfo(device_info_set, index, ctypes.byref(device_info)):
            ble_devices.append(device_info)
            index += 1

        # Clean up the device information set
        setupapi.SetupDiDestroyDeviceInfoList(device_info_set)

    return ble_devices

# Example usage
ble_devices = enumerate_ble_devices()
for device in ble_devices:
    print(f"Name: {device.Name}, Address: {device.Address:x}")
