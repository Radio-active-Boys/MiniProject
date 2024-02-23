#include <Windows.h>
#include <BluetoothAPIs.h>
#include <iostream>

int main() {
    while (true) {
        BLUETOOTH_DEVICE_SEARCH_PARAMS searchParams = {};
        searchParams.dwSize = sizeof(BLUETOOTH_DEVICE_SEARCH_PARAMS);
        searchParams.fReturnAuthenticated = TRUE;
        searchParams.fReturnRemembered = TRUE;
        searchParams.fReturnUnknown = TRUE;
        searchParams.fReturnConnected = TRUE;
        searchParams.fIssueInquiry = TRUE;
        searchParams.cTimeoutMultiplier = 4;

        BLUETOOTH_DEVICE_INFO deviceInfo = {};
        deviceInfo.dwSize = sizeof(BLUETOOTH_DEVICE_INFO);

        HANDLE hFind = BluetoothFindFirstDevice(&searchParams, &deviceInfo);

        if (hFind != NULL) {
            do {
                std::wcout << L"Device Name: " << deviceInfo.szName << std::endl;
                std::wcout << L"Device Address: " << deviceInfo.Address.ullLong << std::endl;
                std::wcout << std::endl;
            } while (BluetoothFindNextDevice(hFind, &deviceInfo));
        }

        BluetoothFindDeviceClose(hFind);
        Sleep(10000); // 10 seconds delay
    }

    return 0;
}
