'dishoom'

The 'dishoom' is a Python package for the GUI of aircrack-ng.

Requirements:
-------------
'gnome-terminal'(if you are using gnome desktop then you have already in your system)  and 'aircrack-ng' should be installed.
You can install these using the following commands:

    sudo apt install gnome-terminal
    sudo apt install aircrack-ng

Installation:
-------------
To install 'dishoom', use the following command:

    pip install dishoom

After installation, you can type 'dishoom' anywhere in the terminal to run it.

Usage:
------
Once successfully run, it will show you the main window containing available interfaces 
on your machine, as well as three buttons to interact with them.

General Workflow:
-----------------
1. **Scan** and **Manage Interface** buttons:
  - Before clicking these buttons, you need to select an interface.
  - Once selected, the action will be performed on the chosen interface.

2. **Scan**:
  - Click 'Scan' after selecting an interface to see the available Wi-Fi networks around you. 
  - Choose a target and click the 'Capture' button.

3. **Monitor Mode**:
  - Click 'Monitor Mode Start' to enable the interface to capture the 4-way handshake. 
  - Note: Your Wi-Fi connection will be disconnected and you won’t be able to reconnect while in monitor mode. 
  - You can undo this later (see the last part of this text).

4. **Check for interfering processes**:
  - You can click 'Interface check' to view any processes that might interfere with your work. 
  - If necessary, you can click 'Kill Processes' to terminate these processes.
  - It's not required, but some processes can cause issues.

5. **Stopping Network Manager**:
  - Before continuing, click 'Network Manager Stop' to disable services that might prevent your work.

6. **Capture**:
  - Click 'Capture', it will ask for a filename (don't add an extension). Enter a filename and click 'Start Capture on ...'.
  - A terminal window will open (you might be asked for your sudo password to run the script as sudo). 
  - Look for a line starting with "WPA handshake: ...". If you see this, you're good to go.
  - If you don't see the handshake, refer to the terminal window and provide a station input.
  - (Look for "STATION" and use a value under it).
  - Provide a deauthentication value (e.g., '10' for fewer requests or '100' for more). 
  - Click 'Deauthenticate' to disconnect the target device. 
  - When the device reconnects, the "WPA handshake: ..." message should appear in the terminal window.

7. **Cracking**:
  - After capturing, click 'Crack' to select the .cap file you created earlier.
  - (You can found .cap file in the .dishoom folder in your home directory).
  - The program will prompt for a wordlist file. You can use popular wordlists like 'rockyou.txt' or create your own.
  - Select the wordlist and click 'Start Crack'. If the wordlist contains the correct password or hash, the password will appear in the last opened window.

Notes:
------
  - Cracking may take some time depending on the wordlist size and password complexity.
  - If no password is found, it’s possible your wordlist doesn't contain the correct password.

Final Steps:
-------------
  - After you're done, you should stop monitor mode to return your interface to managed mode (for reconnecting to Wi-Fi). You can also restart the Network Manager.
  - To do this, go to the main window and click 'Manage Interface'. From there, you can stop monitor mode and start the Network Manager.

Now you can connect to your cracked Wi-Fi and enjoy!

Thanks for using 'dishoom'!  

********************************************************************************************
                                       End
********************************************************************************************
