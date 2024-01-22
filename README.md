# pydp100: Python scripts for DP100 power supply

This project aim to use the python scripts to communication with Alientek DP100 power supply.

## Guidelines

The config.txt is used to configure the output voltage and the trip current.

Use powerup.py to load the configuration from config.txt, and enable the output.

Use powerread.py to read the status (VIT) from DP100.

Use poweroff.py to disable the output.

## Dependencies

This project is based on the [hid](https://pypi.org/project/hid/) and [crcmod](https://pypi.org/project/crcmod/) libraries.

Before run the script, you have to follow the instruction from [this page](https://pypi.org/project/hid/) to install the necessary libraries. In Ubuntu, `sudo apt install libhidapi-hidraw0` works for this project.

Then `sudo pip3 install crcmod hid`

## Troubleshoot

1. HIDException('unable to open device')

Check if plug in the DP100 using the USB-A to USB-A cable, and make sure it's in "USBD" mode. Usually "USBD" mode is the default mode, you can double-tap ◀ to switch between USBD and USBH.

Use `lsusb` to check the usb bus number for "ALIENTEK ATK-MDP100", and use `ls -al /dev/bus/usb/xxx/` (xxx is the bus number for DP100) to check if the user has the permission to access the usb port. Note the HID device has root-only permission by default. To adjust USB permissions, copy the 99-atk-dp100.rules from this repo to the /etc/udev/rules.d/ folder on your computer, then run `sudo udevadm control --reload-rules` and re-plug the USB cable.

2. We have problem with Python hid on windows OS, the first byte is always missing during write operation.

3. Mac OS is not tested yet.

## Reference

1. [open_dp100](https://github.com/lessu/open_dp100) helps to understand the protocol between host and DP100, this project is migrated from open_dp100.

2. [webdp100](https://github.com/scottbez1/webdp100) is a program to interface DP100 through the chrome or edge browser.

3. [DP100-PyQt5-GUI](https://github.com/ElluIFX/DP100-PyQt5-GUI) use ALIENTEK's DLL to control and monitor the DP100. But this DLL is based on microsoft dotnet, I failed to migrate it to linux.
