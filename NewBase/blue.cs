using System;
using System.Threading.Tasks;
using Windows.Devices.Bluetooth;
using Windows.Devices.Bluetooth.Advertisement;

class Program
{
    static async Task Main()
    {
        while (true)
        {
            var watcher = new BluetoothLEAdvertisementWatcher();
            watcher.Received += (sender, args) =>
            {
                Console.WriteLine($"Device Name: {args.Advertisement.LocalName}, Address: {args.BluetoothAddress}");
            };

            watcher.Start();
            await Task.Delay(10000); // 10 seconds delay
            watcher.Stop();
        }
    }
}
