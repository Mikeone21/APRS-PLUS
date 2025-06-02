# APRS-PLUS

W3XPT's APRS Communicator v2.8.9-APRS-ParserFix - User Guide
Welcome! This guide covers APRS-IS and TNC operations.
TABLE OF CONTENTS

Introduction
Prerequisites & Setup
APRS-IS & TNC Tab
3.1. APRS Configuration (Common for IS & TNC)
3.2. APRS-IS Specific Settings
3.3. TNC (KISS Mode) Settings
3.3.1. Automatic Beacon Settings (Dedicated Text)
3.3.2. Timed Status/Position Beacon (Uses Manual Status Text)
3.4. Connecting & Sending Data
3.5. APRS Log & Display Customization
3.6. Heard APRS Stations List
APRS Map Tab
Activity Log
Menu Bar
User Guide Tab
General Tips
Acknowledgements
1. INTRODUCTION
This application allows communication with the APRS network via APRS-IS (Internet Service) and directly via a KISS-mode TNC connected to a radio. You can send position/status beacons, direct messages, monitor APRS activity, and set up automatic beacons for either interface. TNC communication is handled in a separate thread to keep the UI responsive and includes error reporting.
2. PREREQUISITES & SETUP
Network: Internet connection required for APRS-IS.
APRS Callsign & Passcode: Needed for APRS-IS transmission.
TNC & Radio: For TNC operation, a KISS-compatible TNC and a configured radio are required.
Serial Port: A serial port (likely USB-to-Serial adapter) to connect to the TNC. Ensure drivers are installed and the correct port is selected in the application.
Dependencies: Python 3, PySide6 (including QtSerialPort).
3. APRS-IS & TNC TAB
3.1. APRS Configuration (Common for IS & TNC)
These settings are used by both APRS-IS and TNC transmission modes:
APRS Callsign-SSID: Your amateur radio callsign and SSID (e.g., N0CALL-9). This is crucial for forming your packets.
Latitude & Longitude (Dec Deg): Your geographical coordinates for position reports.
💠 Select Symbol Button: Choose your APRS symbol.
3.2. APRS-IS Specific Settings
APRS Passcode: Your APRS-IS passcode. Enter -1 for receive-only on APRS-IS.
APRS-IS Server & Port: Address and port of the APRS-IS server (e.g., noam.aprs2.net:14580).
Filter (optional): An APRS filter string for APRS-IS.
Connect/Disconnect APRS-IS Buttons: Manage your connection to the APRS-IS server.
3.3. TNC (KISS Mode) Settings
Serial Port: Select the COM port your TNC is connected to. Click 🔄 to refresh the list if ports are not appearing or have changed.
Baud Rate: Set the baud rate for the serial connection (e.g., 9600, 19200). This must match your TNC's configuration.
Connect/Disconnect TNC Buttons: Manage your serial connection to the TNC.
TNC Status: Displays the current connection status of the TNC. Errors during connection or operation will be shown here and in the Activity Log.
Use TNC for Sending: Check this box to direct outgoing manual sends, DMs, and automatic beacons through the TNC instead of APRS-IS. If unchecked, APRS-IS (if connected) will be used.
3.3.1. Automatic Beacon Settings (Dedicated Text)
Beacon Text: Text for the primary automatic beacon.
Beacon Interval (min): Interval for this beacon.
🔔 Enable Beacon / 🔕 Disable Beacon Button: Toggles this beacon.
3.3.2. Timed Status/Position Beacon (Uses Manual Status Text)
Status/Pos Comment (Manual): Text entered here can be sent manually or as a timed beacon.
Status Beacon Interval (min): Interval for this secondary timed beacon.
📡🔔 Enable Status Beacon / 📡🔕 Disable Status Beacon Button: Toggles this beacon.
3.4. Connecting & Sending Data
Manual Send: The "Send Manual Pos/Status" button uses the "Status/Pos Comment (Manual)" field. It sends via APRS-IS or TNC based on the "Use TNC for Sending" checkbox.
Direct Messages: Sent via APRS-IS or TNC based on the "Use TNC for Sending" checkbox.
Automatic Beacons: Sent via APRS-IS or TNC based on the "Use TNC for Sending" checkbox.
Note: For TNC transmission, a valid passcode is not strictly required by the TNC itself, but your callsign must be set. For APRS-IS transmission, a valid passcode (not -1) is needed.
Error Handling: The application provides feedback for TNC connection errors (e.g., port not found, permission denied), write failures, and some protocol issues in the Activity Log and Status Bar.
3.5. APRS Log & Display Customization
Displays incoming APRS packets from APRS-IS (prefixed with [IS]) and TNC (prefixed with [TNC]), plus server/TNC messages.
Customize font size and colors.
3.6. Heard APRS Stations List
Displays stations heard from APRS-IS or TNC. Each item in the list provides a multi-line summary including:
Callsign, Last Heard Time (local), Packet Type (e.g., Position, Status, Generic APRS Data).
Packet Timestamp (if available), Latitude / Longitude, Symbol (for position packets).
Speed, Course, Altitude (if available for position packets).
A snippet of the Comment or Status message.
Single-click on a station in the list to open a dialog showing more detailed decoded information including: Callsign, Last Heard Time, Packet Type, Packet Timestamp, Latitude, Longitude, Symbol, Speed, Course, Altitude, the full Comment/Status, and the Raw Packet Body (which includes destination and path).
Double-click (or select and click "🗺️ Track on Map") to track the station on the APRS Map tab.
🧹 Clear List Button: Clears the station list.
4. APRS MAP TAB
Displays APRS data on maps.
5. ACTIVITY LOG (Common Panel)
General application messages and errors, including TNC status and errors.
6. MENU BAR
File Menu: Exit
Help Menu: About
7. USER GUIDE TAB
This document.
8. GENERAL TIPS
Ensure correct serial port and baud rate for TNC are selected and match TNC settings.
Select "Use TNC for Sending" to transmit over radio.
Check the Activity Log for detailed TNC communication status and errors if issues arise.
9. ACKNOWLEDGEMENTS
APRS, Bob Bruninga (WB4APR), APRS.fi, Google Maps, PySide6 (The Qt Company).
We hope you enjoy using W3XPT's APRS Communicator!
