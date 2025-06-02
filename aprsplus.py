# W3XPT's APRS Communicator (Derived from P2P Communicator V2.8.3)
# Authored by: Mike Cintron W3XPT
import sys
import os
import time
import json
import math # For APRS lat/lon conversion

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QLabel, QFileDialog, QMessageBox, QComboBox, QStyleFactory,
    QFrame, QGridLayout, QSizePolicy, QStatusBar, QSplitter, QDialog, QDialogButtonBox,
    QTabWidget, QSplashScreen, QColorDialog, QSpinBox, QGroupBox, QCheckBox
)
from PySide6.QtNetwork import (
    QTcpSocket, QHostAddress
)
from PySide6.QtCore import (
    Qt, Slot, Signal, QIODevice, QByteArray, QTimer, QObject, QStandardPaths,
    QLocale, QUrl, QThread, QMetaObject, Q_ARG 
)
from PySide6.QtGui import QIcon, QColor, QPixmap, QAction, QPainter, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo


# --- Configuration ---
ORGANIZATION_NAME = "MindTech"
APPLICATION_NAME = "W3XPT's APRS Communicator"
APP_VERSION = "v2.8.9-APRS-ParserFix" 
CONFIG_FILE_NAME = "config_aprs.json"

# APRS Defaults
DEFAULT_APRS_SERVER = "noam.aprs2.net"
DEFAULT_APRS_PORT = 14580
CLIENT_APRS_VERSION_INFO = f"APRSComm-{APP_VERSION}"
DEFAULT_APRS_MAP_URL = "https://aprs.fi"
DEFAULT_APRS_SYMBOL_TABLE = '/'
DEFAULT_APRS_SYMBOL_CHAR = 'I'
DEFAULT_BEACON_INTERVAL_MINUTES = 30
DEFAULT_BEACON_TEXT = "APRS Beacon via APRS-IS"
DEFAULT_MANUAL_STATUS_TEXT = "" 
DEFAULT_MANUAL_BEACON_INTERVAL_MINUTES = 15
DEFAULT_TNC_BAUD_RATE = 9600

# APRS Log Display Defaults
DEFAULT_APRS_LOG_FONT_SIZE = 10
DEFAULT_APRS_LOG_TEXT_COLOR = "#00FF7F"
DEFAULT_APRS_LOG_BG_COLOR = "#1E1E2E"

# --- Constants for Icons (Unicode) ---
ICON_DISCONNECT = "🚫"
ICON_CONNECT = "🔌" 
ICON_REFRESH = "🔄"; ICON_LOG = "📜"; ICON_TARGET = "🎯"; ICON_SETTINGS = "⚙️"
ICON_DOWNLOAD_DIR = "💾"; ICON_CLEAR = "🧹"; ICON_APRS = "🛰️"; ICON_LOCATION = "📍"
ICON_MAP = "🗺️"; ICON_GO = "➡️"; ICON_MESSAGE = "💬"; ICON_GUIDE = "📖"; ICON_FONT = "🇦"
ICON_COLOR_TEXT = "🇹"; ICON_COLOR_BG = "🇧"; ICON_STATIONS = "📡"; ICON_SYMBOL_PICKER = "💠"
ICON_BEACON_ON = "🔔"; ICON_BEACON_OFF = "🔕" 
ICON_STATUS_BEACON_ON = "📡🔔"; ICON_STATUS_BEACON_OFF = "📡🔕"
ICON_TNC = "📻"
ICON_INFO = "ℹ️" 


# KISS Protocol Constants
KISS_FEND = 0xC0  # Frame End
KISS_FESC = 0xDB  # Frame Escape
KISS_TFEND = 0xDC # Transposed Frame End
KISS_TFESC = 0xDD # Transposed Frame Escape
KISS_CMD_DATA = 0x00 # Data frame on port 0


# --- APRS Symbol Data ---
APRS_SYMBOLS = [
    {'table': '/', 'char': '>', 'desc': 'Car', 'font_char': '>'},
    {'table': '/', 'char': '<', 'desc': 'Motorcycle', 'font_char': '<'},
    {'table': '/', 'char': 'b', 'desc': 'Bike', 'font_char': 'b'},
    {'table': '/', 'char': 'h', 'desc': 'Home', 'font_char': 'h'},
    {'table': '/', 'char': 'H', 'desc': 'Hospital', 'font_char': 'H'},
    {'table': '/', 'char': 'I', 'desc': 'TCP/IP Node, WX', 'font_char': 'I'},
    {'table': '/', 'char': 'p', 'desc': 'Person (Man)', 'font_char': 'p'},
    {'table': '/', 'char': '[', 'desc': 'Human / Person', 'font_char': '['},
    {'table': '/', 'char': 's', 'desc': 'Ship/Boat (Sail)', 'font_char': 's'},
    {'table': '/', 'char': 'u', 'desc': 'Truck', 'font_char': 'u'},
    {'table': '/', 'char': 'v', 'desc': 'Van', 'font_char': 'v'},
    {'table': '/', 'char': 'x', 'desc': 'Helicopter', 'font_char': 'x'},
    {'table': '/', 'char': 'y', 'desc': 'Aircraft', 'font_char': 'y'},
    {'table': '/', 'char': '$', 'desc': 'Phone', 'font_char': '$'},
    {'table': '/', 'char': '`', 'desc': 'Dish Antenna', 'font_char': '`'},
    {'table': '/', 'char': 'k', 'desc': 'School', 'font_char': 'k'},
    {'table': '/', 'char': 'a', 'desc': 'Aid Station', 'font_char': 'a'},
    {'table': '/', 'char': 'c', 'desc': 'Campsite', 'font_char': 'c'},
    {'table': '/', 'char': 'f', 'desc': 'Fire Station', 'font_char': 'f'},
    {'table': '/', 'char': 'g', 'desc': 'Gas Station (Petrol)', 'font_char': 'g'},
    {'table': '/', 'char': 'L', 'desc': 'Lighthouse', 'font_char': 'L'},
    {'table': '/', 'char': 'N', 'desc': 'Nav Beacon', 'font_char': 'N'},
    {'table': '/', 'char': 'R', 'desc': 'Restaurant', 'font_char': 'R'},
    {'table': '/', 'char': 'X', 'desc': 'Crossed Swords (Emergency)', 'font_char': 'X'},
    {'table': '/', 'char': '#', 'desc': 'Digipeater', 'font_char': '#'},
    {'table': '/', 'char': '-', 'desc': 'House (HF)', 'font_char': '-'},
    {'table': '/', 'char': '0', 'desc': 'Circle (0)', 'font_char': '0'},
    {'table': '/', 'char': 'S', 'desc': 'Space Shuttle/Station', 'font_char': 'S'},
    {'table': '/', 'char': 'Y', 'desc': 'Yacht (Sail)', 'font_char': 'Y'},
    {'table': '/', 'char': 'Q', 'desc': 'Grid Square (QTH)', 'font_char': 'Q'},
    {'table': '/', 'char': 'W', 'desc': 'Weather Station', 'font_char': 'W'},
    {'table': '/', 'char': '_', 'desc': 'Weather Station (Underscore)', 'font_char': '_'},
    {'table': '\\', 'char': '>', 'desc': 'Car (alt)', 'font_char': '>'},
    {'table': '\\', 'char': 's', 'desc': 'Power Boat (alt)', 'font_char': 's'},
    {'table': '\\', 'char': 'p', 'desc': 'Person (alt)', 'font_char': 'p'},
    {'table': '\\', 'char': 'I', 'desc': 'TCP/IP Node (alt)', 'font_char': 'I'},
    {'table': '\\', 'char': 'h', 'desc': 'Home (alt)', 'font_char': 'h'},
    {'table': '\\', 'char': ']', 'desc': 'Mobile Satellite Station', 'font_char': ']'},
    {'table': '\\', 'char': 'j', 'desc': 'Jeep', 'font_char': 'j'},
    {'table': '\\', 'char': 't', 'desc': 'Truck Stop', 'font_char': 't'},
    {'table': '\\', 'char': 'w', 'desc': 'Water Station', 'font_char': 'w'},
    {'table': '\\', 'char': 'r', 'desc': 'RV / Recreational Vehicle', 'font_char': 'r'},
    {'table': '\\', 'char': '\\', 'desc': 'HF Gateway', 'font_char': '\\'},
]


# --- User Guide Documentation (Formatted for QTextEdit Markdown) ---
USER_GUIDE_DOCUMENTATION = """
# W3XPT's APRS Communicator {app_version} - User Guide

Welcome! This guide covers APRS-IS and TNC operations.

## TABLE OF CONTENTS
* 1.  Introduction
* 2.  Prerequisites & Setup
* 3.  APRS-IS & TNC Tab
    * 3.1. APRS Configuration (Common for IS & TNC)
    * 3.2. APRS-IS Specific Settings
    * 3.3. TNC (KISS Mode) Settings
        * 3.3.1. Automatic Beacon Settings (Dedicated Text)
        * 3.3.2. Timed Status/Position Beacon (Uses Manual Status Text)
    * 3.4. Connecting & Sending Data
    * 3.5. APRS Log & Display Customization
    * 3.6. Heard APRS Stations List
* 4.  APRS Map Tab
* 5.  Activity Log
* 6.  Menu Bar
* 7.  User Guide Tab
* 8.  General Tips
* 9.  Acknowledgements

## 1. INTRODUCTION
This application allows communication with the APRS network via APRS-IS (Internet Service) and directly via a KISS-mode TNC connected to a radio. You can send position/status beacons, direct messages, monitor APRS activity, and set up automatic beacons for either interface. TNC communication is handled in a separate thread to keep the UI responsive and includes error reporting.

## 2. PREREQUISITES & SETUP
* **Network:** Internet connection required for APRS-IS.
* **APRS Callsign & Passcode:** Needed for APRS-IS transmission.
* **TNC & Radio:** For TNC operation, a KISS-compatible TNC and a configured radio are required.
* **Serial Port:** A serial port (likely USB-to-Serial adapter) to connect to the TNC. Ensure drivers are installed and the correct port is selected in the application.
* **Dependencies:** Python 3, PySide6 (including QtSerialPort).

## 3. APRS-IS & TNC TAB

### 3.1. APRS Configuration (Common for IS & TNC)
These settings are used by both APRS-IS and TNC transmission modes:
* **APRS Callsign-SSID:** Your amateur radio callsign and SSID (e.g., `N0CALL-9`). This is crucial for forming your packets.
* **Latitude & Longitude (Dec Deg):** Your geographical coordinates for position reports.
* **{icon_symbol_picker} Select Symbol Button:** Choose your APRS symbol.

### 3.2. APRS-IS Specific Settings
* **APRS Passcode:** Your APRS-IS passcode. Enter `-1` for receive-only on APRS-IS.
* **APRS-IS Server & Port:** Address and port of the APRS-IS server (e.g., `{default_aprs_server}:{default_aprs_port}`).
* **Filter (optional):** An APRS filter string for APRS-IS.
* **Connect/Disconnect APRS-IS Buttons:** Manage your connection to the APRS-IS server.

### 3.3. TNC (KISS Mode) Settings
* **Serial Port:** Select the COM port your TNC is connected to. Click {icon_refresh} to refresh the list if ports are not appearing or have changed.
* **Baud Rate:** Set the baud rate for the serial connection (e.g., 9600, 19200). This must match your TNC's configuration.
* **Connect/Disconnect TNC Buttons:** Manage your serial connection to the TNC.
* **TNC Status:** Displays the current connection status of the TNC. Errors during connection or operation will be shown here and in the Activity Log.
* **Use TNC for Sending:** Check this box to direct outgoing manual sends, DMs, and automatic beacons through the TNC instead of APRS-IS. If unchecked, APRS-IS (if connected) will be used.

#### 3.3.1. Automatic Beacon Settings (Dedicated Text)
* **Beacon Text:** Text for the primary automatic beacon.
* **Beacon Interval (min):** Interval for this beacon.
* **{icon_beacon_on} Enable Beacon / {icon_beacon_off} Disable Beacon Button:** Toggles this beacon.

#### 3.3.2. Timed Status/Position Beacon (Uses Manual Status Text)
* **Status/Pos Comment (Manual):** Text entered here can be sent manually or as a timed beacon.
* **Status Beacon Interval (min):** Interval for this secondary timed beacon.
* **{icon_status_beacon_on} Enable Status Beacon / {icon_status_beacon_off} Disable Status Beacon Button:** Toggles this beacon.

### 3.4. Connecting & Sending Data
* **Manual Send:** The "Send Manual Pos/Status" button uses the "Status/Pos Comment (Manual)" field. It sends via APRS-IS or TNC based on the "Use TNC for Sending" checkbox.
* **Direct Messages:** Sent via APRS-IS or TNC based on the "Use TNC for Sending" checkbox.
* **Automatic Beacons:** Sent via APRS-IS or TNC based on the "Use TNC for Sending" checkbox.
* **Note:** For TNC transmission, a valid passcode is not strictly required by the TNC itself, but your callsign must be set. For APRS-IS transmission, a valid passcode (not -1) is needed.
* **Error Handling:** The application provides feedback for TNC connection errors (e.g., port not found, permission denied), write failures, and some protocol issues in the Activity Log and Status Bar.

### 3.5. APRS Log & Display Customization
* Displays incoming APRS packets from APRS-IS (prefixed with `[IS]`) and TNC (prefixed with `[TNC]`), plus server/TNC messages.
* Customize font size and colors.

### 3.6. Heard APRS Stations List
* Displays stations heard from APRS-IS or TNC. Each item in the list provides a multi-line summary including:
    * Callsign, Last Heard Time (local), Packet Type (e.g., Position, Status, Generic APRS Data).
    * Packet Timestamp (if available), Latitude / Longitude, Symbol (for position packets).
    * Speed, Course, Altitude (if available for position packets).
    * A snippet of the Comment or Status message.
* **Single-click** on a station in the list to open a dialog showing more detailed decoded information including: Callsign, Last Heard Time, Packet Type, Packet Timestamp, Latitude, Longitude, Symbol, Speed, Course, Altitude, the full Comment/Status, and the Raw Packet Body (which includes destination and path).
* **Double-click** (or select and click "{icon_map} Track on Map") to track the station on the APRS Map tab.
* **{icon_clear} Clear List Button:** Clears the station list.


## 4. APRS MAP TAB
* Displays APRS data on maps.

## 5. ACTIVITY LOG (Common Panel)
* General application messages and errors, including TNC status and errors.

## 6. MENU BAR
* **File Menu:** `Exit`
* **Help Menu:** `About`

## 7. USER GUIDE TAB
* This document.

## 8. GENERAL TIPS
* Ensure correct serial port and baud rate for TNC are selected and match TNC settings.
* Select "Use TNC for Sending" to transmit over radio.
* Check the Activity Log for detailed TNC communication status and errors if issues arise.

## 9. ACKNOWLEDGEMENTS
* APRS, Bob Bruninga (WB4APR), APRS.fi, Google Maps, PySide6 (The Qt Company).

We hope you enjoy using W3XPT's APRS Communicator!
""".format(
    app_version=APP_VERSION,
    icon_color_text=ICON_COLOR_TEXT,
    icon_color_bg=ICON_COLOR_BG,
    icon_clear=ICON_CLEAR,
    icon_map=ICON_MAP,
    icon_symbol_picker=ICON_SYMBOL_PICKER,
    icon_beacon_on=ICON_BEACON_ON,
    icon_beacon_off=ICON_BEACON_OFF,
    icon_status_beacon_on=ICON_STATUS_BEACON_ON,
    icon_status_beacon_off=ICON_STATUS_BEACON_OFF,
    icon_refresh=ICON_REFRESH,
    default_aprs_server=DEFAULT_APRS_SERVER,
    default_aprs_port=DEFAULT_APRS_PORT,
    default_aprs_map_url=DEFAULT_APRS_MAP_URL,
    default_aprs_symbol_table=DEFAULT_APRS_SYMBOL_TABLE,
    default_aprs_symbol_char=DEFAULT_APRS_SYMBOL_CHAR
)


# --- APRS Symbol Picker Dialog ---
class APRSSymbolPickerDialog(QDialog):
    def __init__(self, current_table, current_char, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select APRS Symbol")
        self.setMinimumSize(400, 500)
        self.selected_symbol_table = current_table
        self.selected_symbol_char = current_char

        layout = QVBoxLayout(self)

        self.symbol_list_widget = QListWidget()
        self.symbol_list_widget.setFont(QFont("Consolas", 12)) 
        for symbol_info in APRS_SYMBOLS:
            display_text = f"{symbol_info['font_char']} ({symbol_info['table']}) - {symbol_info['desc']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, symbol_info)
            self.symbol_list_widget.addItem(item)
            if symbol_info['table'] == current_table and symbol_info['char'] == current_char:
                self.symbol_list_widget.setCurrentItem(item)

        self.symbol_list_widget.itemDoubleClicked.connect(self.on_accept)
        layout.addWidget(self.symbol_list_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def on_accept(self):
        current_item = self.symbol_list_widget.currentItem()
        if current_item:
            selected_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_symbol_table = selected_data['table']
            self.selected_symbol_char = selected_data['char']
        self.accept()

    def get_selected_symbol(self):
        return self.selected_symbol_table, self.selected_symbol_char

# --- Direct Message Dialog (for APRS) ---
class DirectMessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Incoming APRS Message")
        self.setMinimumSize(400, 200)
        layout = QVBoxLayout(self)
        self.from_label = QLabel("From: N/A")
        self.message_display = QTextEdit(); self.message_display.setReadOnly(True)
        layout.addWidget(self.from_label); layout.addWidget(self.message_display, 1)
        self.ok_button = QPushButton("OK"); self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

    def set_message(self, sender_callsign, message_text):
        self.from_label.setText(f"From: {sender_callsign}")
        self.message_display.setText(message_text)
        self.setWindowTitle(f"APRS Message from {sender_callsign}")

# --- Station Detail Dialog ---
class StationDetailDialog(QDialog):
    def __init__(self, callsign, station_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{ICON_INFO} APRS Station Details - {callsign}")
        self.setMinimumWidth(500) 
        self.setModal(True) 

        layout = QGridLayout(self)
        layout.setSpacing(10) 

        row = 0
        parsed_data = station_data.get("parsed_data", {})
        last_seen_local_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(station_data.get("last_seen", time.time())))
        raw_packet_body = station_data.get("raw_packet_body", "N/A") # This is DEST,PATH:BODY


        def add_detail_row(label_text, value_text):
            nonlocal row
            label_widget = QLabel(f"<b>{label_text}:</b>")
            value_str = str(value_text) if value_text is not None else "N/A"
            if not value_str.strip(): 
                value_str = "N/A"
            value_widget = QLabel(value_str)
            value_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse) 
            layout.addWidget(label_widget, row, 0)
            layout.addWidget(value_widget, row, 1)
            row += 1

        add_detail_row("Callsign", callsign)
        add_detail_row("Last Heard (Local)", last_seen_local_time_str)
        
        packet_type_display = parsed_data.get('type', "N/A").replace('_', ' ').title()
        add_detail_row("Packet Type", packet_type_display)
        add_detail_row("Packet Timestamp", parsed_data.get('timestamp', "N/A"))


        lat_val = parsed_data.get('latitude')
        add_detail_row("Latitude", f"{lat_val:.4f}" if lat_val is not None else "N/A")
        lon_val = parsed_data.get('longitude')
        add_detail_row("Longitude", f"{lon_val:.4f}" if lon_val is not None else "N/A")
        
        sym_tbl = parsed_data.get("symbol_table")
        sym_code = parsed_data.get("symbol_code")
        symbol_str = "N/A"
        if sym_tbl and sym_code:
            symbol_str = f"{sym_tbl}{sym_code}"
            for sym_info in APRS_SYMBOLS:
                if sym_info['table'] == sym_tbl and sym_info['char'] == sym_code:
                    symbol_str += f" ({sym_info['desc']})"
                    break
        add_detail_row("Symbol", symbol_str)


        speed_val = parsed_data.get('speed')
        add_detail_row("Speed", f"{speed_val} kts" if speed_val is not None else "N/A")
        
        course_val = parsed_data.get('course')
        add_detail_row("Course", f"{course_val}°" if course_val is not None else "N/A")

        alt_val = parsed_data.get('altitude')
        add_detail_row("Altitude", f"{alt_val} ft" if alt_val is not None else "N/A")
        
        comment = parsed_data.get('comment', 'N/A')
        if not comment or comment.isspace(): 
            comment = "N/A"

        comment_label = QLabel("<b>Comment/Status:</b>")
        self.comment_text_edit = QTextEdit(comment)
        self.comment_text_edit.setReadOnly(True)
        self.comment_text_edit.setFixedHeight(80) 
        layout.addWidget(comment_label, row, 0)
        layout.addWidget(self.comment_text_edit, row, 1)
        row +=1

        raw_packet_label = QLabel("<b>Raw Packet Body (after source):</b>") # Clarified
        self.raw_packet_text_edit = QTextEdit(raw_packet_body)
        self.raw_packet_text_edit.setReadOnly(True)
        self.raw_packet_text_edit.setFixedHeight(100)
        layout.addWidget(raw_packet_label, row, 0)
        layout.addWidget(self.raw_packet_text_edit, row, 1)
        row += 1

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, row, 0, 1, 2, Qt.AlignmentFlag.AlignCenter) 

        self.setLayout(layout)


# --- TNC Manager ---
class TNCManager(QObject):
    tnc_connected = Signal()
    tnc_disconnected = Signal()
    tnc_error = Signal(str) 
    aprs_packet_from_tnc = Signal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_port = None 
        self.port_name = ""
        self.baud_rate = DEFAULT_TNC_BAUD_RATE
        self._is_connected = False
        self._read_buffer = QByteArray()
    
    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] [TNCManager] {message}")

    @Slot()
    def initialize_serial_port(self):
        if self.serial_port is None:
            self.serial_port = QSerialPort(self) 
            self.serial_port.readyRead.connect(self._handle_ready_read)
            self.serial_port.errorOccurred.connect(self._handle_serial_error)
            self.log("QSerialPort instance created and signals connected in TNCManager thread.")
        else:
            self.log("QSerialPort already initialized in TNCManager thread.")


    @staticmethod
    def list_available_ports():
        return QSerialPortInfo.availablePorts()

    def set_port_config(self, port_name, baud_rate):
        self.port_name = port_name
        self.baud_rate = int(baud_rate)
        self.log(f"TNC port config set: {port_name} @ {baud_rate}")


    @Slot()
    def connect_tnc(self):
        if self.serial_port is None:
            self.tnc_error.emit("Serial port object not initialized. Call initialize_serial_port first.")
            self.log("Error: connect_tnc called before serial_port was initialized.")
            return 

        if self._is_connected:
            self.log("Already connected to TNC.")
            return 

        if not self.port_name:
            self.tnc_error.emit("Serial port not selected.")
            return 

        self.serial_port.setPortName(self.port_name)
        self.serial_port.setBaudRate(self.baud_rate)
        self.serial_port.setDataBits(QSerialPort.DataBits.Data8)
        self.serial_port.setParity(QSerialPort.Parity.NoParity)
        self.serial_port.setStopBits(QSerialPort.StopBits.OneStop)
        self.serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

        if self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite):
            self._is_connected = True
            self.log(f"TNC connected on {self.port_name} at {self.baud_rate} baud.")
            self.tnc_connected.emit()
        else:
            self._is_connected = False
            error_msg = f"Failed to open TNC port {self.port_name}: {self.serial_port.errorString()}"
            self.log(error_msg)
            self.tnc_error.emit(error_msg)

    @Slot()
    def disconnect_tnc(self):
        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.close()
            self.log("Serial port closed.")
        if self._is_connected: 
            self._is_connected = False 
            self.log("TNC disconnected by request or error.")
            self.tnc_disconnected.emit()
        else: 
            self.log("TNC already disconnected or was never connected.")

        self._read_buffer.clear()

    def is_tnc_connected(self):
        return self._is_connected and self.serial_port is not None and self.serial_port.isOpen()

    @Slot(str)
    def send_aprs_packet_via_tnc(self, aprs_packet_string: str):
        if not self.is_tnc_connected(): 
            self.log("Cannot send packet: TNC not connected or port not open.")
            self.tnc_error.emit("TNC not connected. Cannot send packet.")
            return 

        self.log(f"Preparing to send to TNC: {aprs_packet_string}")
        data_to_send = aprs_packet_string.encode('ascii', errors='replace') 
        
        kiss_frame = QByteArray()
        kiss_frame.append(KISS_FEND)
        kiss_frame.append(KISS_CMD_DATA) 
        
        for byte_val in data_to_send:
            if byte_val == KISS_FEND:
                kiss_frame.append(KISS_FESC); kiss_frame.append(KISS_TFEND)
            elif byte_val == KISS_FESC:
                kiss_frame.append(KISS_FESC); kiss_frame.append(KISS_TFESC)
            else:
                kiss_frame.append(byte_val)
        kiss_frame.append(KISS_FEND)

        self.log(f"Sending KISS frame (len {len(kiss_frame)}): {kiss_frame.toHex().data().decode()}")
        bytes_written = self.serial_port.write(kiss_frame)
        if bytes_written == -1:
            error_msg = f"TNC write error: {self.serial_port.errorString()}"
            self.log(error_msg)
            self.tnc_error.emit(error_msg)
        elif bytes_written < len(kiss_frame):
            self.log(f"TNC incomplete write: {bytes_written}/{len(kiss_frame)} bytes written.")
            self.tnc_error.emit(f"TNC incomplete write: {bytes_written}/{len(kiss_frame)}")
        else:
            self.log(f"KISS frame ({bytes_written} bytes) written to TNC.")
        
        if not self.serial_port.flush():
            self.log("TNC flush failed.")


    @Slot()
    def _handle_ready_read(self):
        if not self.serial_port or not self.serial_port.isOpen() or not self.serial_port.bytesAvailable(): 
            return
        
        data = self.serial_port.readAll()
        if data.isEmpty(): return

        self.log(f"TNC Raw Rcvd (len {len(data)}): {data.toHex().data().decode()}")
        self._read_buffer.append(data)
        self._process_tnc_buffer()

    def _process_tnc_buffer(self):
        while True:
            start_fend = self._read_buffer.indexOf(KISS_FEND)
            if start_fend == -1: 
                if len(self._read_buffer) > 4096: 
                    self.log("TNC read buffer too large without FEND, clearing.")
                    self._read_buffer.clear()
                return 
            if start_fend > 0:
                self.log(f"Discarding {start_fend} bytes before FEND from TNC buffer.")
                self._read_buffer = self._read_buffer.mid(start_fend)
            
            if len(self._read_buffer) < 2: return

            end_fend_offset = self._read_buffer.indexOf(KISS_FEND, 1) 
            if end_fend_offset == -1: 
                if len(self._read_buffer) > 4096: 
                    self.log("TNC read buffer has unterminated frame, clearing.")
                    self._read_buffer.clear()
                return

            kiss_frame_candidate = self._read_buffer.left(end_fend_offset + 1)
            self._read_buffer = self._read_buffer.mid(end_fend_offset + 1) 

            if len(kiss_frame_candidate) < 3: 
                self.log("Received too short KISS frame candidate.")
                continue 

            raw_data_with_cmd = kiss_frame_candidate[1:-1]
            
            if not raw_data_with_cmd: 
                self.log("Received empty KISS frame content.")
                continue

            kiss_command = raw_data_with_cmd[0] & 0x0F 
            kiss_port = (raw_data_with_cmd[0] & 0xF0) >> 4 

            if kiss_command == KISS_CMD_DATA: 
                aprs_data_escaped = raw_data_with_cmd[1:]
                decoded_payload = QByteArray()
                i = 0
                while i < len(aprs_data_escaped):
                    byte_val = aprs_data_escaped[i]
                    if byte_val == KISS_FESC:
                        i += 1
                        if i < len(aprs_data_escaped):
                            next_byte = aprs_data_escaped[i]
                            if next_byte == KISS_TFEND: decoded_payload.append(KISS_FEND)
                            elif next_byte == KISS_TFESC: decoded_payload.append(KISS_FESC)
                            else: 
                                self.log(f"KISS unescape error: FESC followed by unknown byte {hex(next_byte)}")
                                decoded_payload.append(byte_val); decoded_payload.append(next_byte)
                        else: 
                             self.log("KISS unescape error: FESC at end of data."); decoded_payload.append(byte_val)
                    else:
                        decoded_payload.append(byte_val)
                    i += 1
                
                try:
                    aprs_packet_str = decoded_payload.data().decode('ascii', errors='replace').strip()
                    self.log(f"APRS Pkt from TNC (Port {kiss_port}): {aprs_packet_str}")
                    self.aprs_packet_from_tnc.emit(aprs_packet_str)
                except UnicodeDecodeError as e:
                    self.log(f"Error decoding APRS packet from TNC (not ASCII?): {e} - Data: {decoded_payload.toHex().data().decode()}")
                    self.tnc_error.emit(f"TNC data decode error: {e}")
            else:
                self.log(f"Received non-data KISS frame from TNC: Port={kiss_port}, CMD={hex(kiss_command)}")


    @Slot(QSerialPort.SerialPortError)
    def _handle_serial_error(self, error_code):
        if error_code == QSerialPort.SerialPortError.NoError:
            return
        
        err_str = self.serial_port.errorString() if self.serial_port else "N/A (Serial port not initialized)"
        error_msg = f"Serial Port Error ({self.port_name}): {err_str} (Code: {error_code})"
        self.log(error_msg)
        self.tnc_error.emit(error_msg)
        
        critical_errors = [
            QSerialPort.SerialPortError.DeviceNotFoundError,
            QSerialPort.SerialPortError.PermissionError,
            QSerialPort.SerialPortError.OpenError,
            QSerialPort.SerialPortError.ResourceError, 
            QSerialPort.SerialPortError.UnsupportedOperationError,
            QSerialPort.SerialPortError.IOError,
            QSerialPort.SerialPortError.TermiosError 
        ]
        if error_code in critical_errors:
            if self._is_connected: 
                self.log("Critical serial error, forcing TNC disconnect.")
                self.disconnect_tnc()


# --- APRS Manager --- 
class APRSManager(QObject):
    aprs_connected = Signal()
    aprs_disconnected = Signal()
    aprs_packet_received = Signal(str) 
    aprs_status_update = Signal(str)
    aprs_direct_message_received = Signal(str, str) 
    aprs_station_list_updated = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = QTcpSocket(self)
        self.callsign_ssid = None 
        self.passcode = None
        self.server_address = None
        self.server_port = None
        self.aprs_filter = None
        self.is_connected = False
        self._buffer = QByteArray()
        self.keepalive_timer = QTimer(self)
        self.keepalive_timer.setInterval(120 * 1000) 
        self.heard_stations = {} 
        self.station_update_timer = QTimer(self)
        self.station_update_timer.setInterval(5000) 
        self.station_update_timer.timeout.connect(self._emit_station_list_update)


        self.socket.connected.connect(self._on_connected)
        self.socket.disconnected.connect(self._on_disconnected)
        self.socket.readyRead.connect(self._on_ready_read)
        self.socket.errorOccurred.connect(self._on_socket_error)
        self.keepalive_timer.timeout.connect(self._send_keepalive)

    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] [APRSManager] {message}")
        self.aprs_status_update.emit(message)

    def _format_lat_aprs(self, lat_decimal):
        if not isinstance(lat_decimal, (float, int)): return None
        abs_lat = abs(lat_decimal)
        deg = int(abs_lat)
        minutes = (abs_lat - deg) * 60
        hemisphere = 'N' if lat_decimal >= 0 else 'S'
        return f"{deg:02d}{minutes:05.2f}{hemisphere}"

    def _format_lon_aprs(self, lon_decimal):
        if not isinstance(lon_decimal, (float, int)): return None
        abs_lon = abs(lon_decimal)
        deg = int(abs_lon)
        minutes = (abs_lon - deg) * 60
        hemisphere = 'E' if lon_decimal >= 0 else 'W'
        return f"{deg:03d}{minutes:05.2f}{hemisphere}"

    def connect_to_aprs_is(self, server, port, callsign_ssid, passcode, aprs_filter=None):
        if self.is_connected:
            self.log("Already connected to APRS-IS. Disconnect first.")
            return False

        self.server_address = server
        self.server_port = int(port)
        self.callsign_ssid = callsign_ssid.upper() 
        self.passcode = passcode
        self.aprs_filter = aprs_filter
        self.heard_stations.clear() 

        if not self.callsign_ssid or self.passcode is None: 
            self.log("APRS Callsign-SSID and Passcode are required for APRS-IS.")
            return False

        self.log(f"Attempting to connect to APRS-IS: {server}:{port} as {self.callsign_ssid}")
        self.socket.connectToHost(server, self.server_port)
        return True

    def disconnect_from_aprs_is(self):
        if self.is_connected:
            self.log("Disconnecting from APRS-IS...")
            self.socket.abort() 
        else:
            self.log("Not connected to APRS-IS.")
        if self.keepalive_timer.isActive(): 
            self.keepalive_timer.stop()
        if self.station_update_timer.isActive():
            self.station_update_timer.stop()


    @Slot()
    def _on_connected(self):
        self.log(f"Successfully connected to APRS-IS server {self.server_address}:{self.server_port}.")
        self.is_connected = True
        self._send_login()
        self.aprs_connected.emit()
        if self.passcode != "-1": 
            self.keepalive_timer.start()
        self.station_update_timer.start()


    @Slot()
    def _on_disconnected(self):
        was_connected = self.is_connected 
        self.is_connected = False
        if self.keepalive_timer.isActive():
            self.keepalive_timer.stop()
        if self.station_update_timer.isActive():
            self.station_update_timer.stop()
        if was_connected: 
            self.log("Disconnected from APRS-IS server.")
            self.aprs_disconnected.emit()
            self.heard_stations.clear() 
            self._emit_station_list_update() 
        else:
            self.log("Connection to APRS-IS server failed or was already closed.")


    @Slot(QTcpSocket.SocketError)
    def _on_socket_error(self, socket_error: QTcpSocket.SocketError):
        err_str = self.socket.errorString()
        self.log(f"APRS-IS Socket Error: {socket_error.name} - {err_str}")
        if self.is_connected : 
             self._on_disconnected() 

    def _send_login(self):
        if not self.is_connected: return
        login_string = f"user {self.callsign_ssid} "
        if self.passcode and str(self.passcode) != "-1":
            login_string += f"pass {self.passcode} "
        login_string += f"vers {CLIENT_APRS_VERSION_INFO}"
        if self.aprs_filter:
            login_string += f" filter {self.aprs_filter}"
        login_string += "\r\n"
        self.log(f"Sending APRS-IS login: {login_string.replace(str(self.passcode), '******') if self.passcode and str(self.passcode) != '-1' else login_string.strip()}")
        self.socket.write(login_string.encode('ascii'))
        self.socket.flush()

    def _send_keepalive(self):
        if self.is_connected and self.passcode and str(self.passcode) != "-1":
            keepalive_packet = f"# Keepalive {self.callsign_ssid}\r\n"
            self.log("Sending APRS-IS keepalive.")
            self.socket.write(keepalive_packet.encode('ascii'))
            self.socket.flush()

    def send_aprs_packet_string_to_is(self, packet_string: str):
        if not self.is_connected:
            self.log("Cannot send APRS packet to IS: Not connected to APRS-IS.")
            return False
        if not self.passcode or str(self.passcode) == "-1":
            self.log("Cannot send APRS packet to IS: Logged in for receive-only or no passcode.")
            return False
        if not packet_string.endswith("\r\n"):
            packet_string += "\r\n"
        self.log(f"Sending APRS packet to IS: {packet_string.strip()}")
        self.socket.write(packet_string.encode('ascii'))
        self.socket.flush()
        return True

    def construct_aprs_position_or_status_packet(self, status_text: str, latitude: str = None, longitude: str = None,
                                     destination="APRS", path="TCPIP*", 
                                     symbol_table=DEFAULT_APRS_SYMBOL_TABLE, symbol_char=DEFAULT_APRS_SYMBOL_CHAR):
        if not self.callsign_ssid: 
            self.log("Cannot construct packet: Callsign-SSID not set in APRSManager."); return None

        lat_aprs, lon_aprs = None, None
        if latitude and longitude:
            try:
                lat_dec = float(latitude)
                lon_dec = float(longitude)
                lat_aprs = self._format_lat_aprs(lat_dec)
                lon_aprs = self._format_lon_aprs(lon_dec)
                if not lat_aprs or not lon_aprs: 
                    self.log("Invalid latitude/longitude format for APRS conversion.")
                    lat_aprs, lon_aprs = None, None 
            except ValueError:
                self.log("Latitude/longitude must be valid numbers.")
                lat_aprs, lon_aprs = None, None

        packet_string = ""
        if lat_aprs and lon_aprs: 
            packet_string = f"{self.callsign_ssid}>{destination},{path}:!{lat_aprs}{symbol_table}{lon_aprs}{symbol_char}{status_text}"
        else: 
            packet_string = f"{self.callsign_ssid}>{destination},{path}:>{status_text}"
        return packet_string
    
    def construct_aprs_direct_message_packet(self, recipient_callsign: str, message_text: str, path="TCPIP*"):
        if not self.callsign_ssid:
            self.log("Cannot construct DM: Own Callsign-SSID not set."); return None
        if not recipient_callsign:
            self.log("Cannot construct DM: Recipient callsign is empty."); return None
        if not message_text: 
            self.log("Cannot construct DM: Message text is empty."); return None
        
        formatted_recipient = recipient_callsign.upper().ljust(9)
        packet_string = f"{self.callsign_ssid}>APRS,{path}::{formatted_recipient}:{message_text}"
        return packet_string


    def _update_heard_station(self, callsign, packet_body_after_source):
        # packet_body_after_source is DEST,PATH:BODY
        parsed_data = self._parse_aprs_packet_info(packet_body_after_source)
        
        display_parts = []
        # Line 1: Callsign - Last Heard (Local Time) - Packet Type
        line1 = f"<b>{callsign}</b> - Last: {time.strftime('%H:%M:%S', time.localtime(time.time()))}"
        packet_type_str = parsed_data.get('type', "Unknown").replace('_', ' ').title()
        line1 += f" - Type: {packet_type_str}"
        display_parts.append(line1)

        # Line 2: Packet Timestamp (if any), Lat/Lon, Symbol (if position)
        line2_items = []
        if parsed_data.get('timestamp'):
            line2_items.append(f"Time: {parsed_data.get('timestamp')}")
        
        if "position" in packet_type_str.lower(): 
            lat_val = parsed_data.get('latitude')
            lon_val = parsed_data.get('longitude')
            lat_str = f"{lat_val:.4f}" if lat_val is not None else "N/A"
            lon_str = f"{lon_val:.4f}" if lon_val is not None else "N/A"
            line2_items.append(f"Loc: {lat_str} / {lon_str}")

            sym_tbl = parsed_data.get("symbol_table")
            sym_code = parsed_data.get("symbol_code")
            if sym_tbl and sym_code:
                line2_items.append(f"Sym: {sym_tbl}{sym_code}")
        
        if line2_items:
            display_parts.append(f"  {' '.join(line2_items)}")

        # Line 3: Speed, Course, Altitude (if position)
        if "position" in packet_type_str.lower():
            line3_items = []
            spd_val = parsed_data.get('speed')
            if spd_val is not None: line3_items.append(f"Spd: {spd_val:.0f}kt")
            crs_val = parsed_data.get('course')
            if crs_val is not None: line3_items.append(f"Crs: {crs_val:03d}°")
            alt_val = parsed_data.get('altitude')
            if alt_val is not None: line3_items.append(f"Alt: {alt_val:.0f}ft")
            if line3_items:
                display_parts.append(f"  {' '.join(line3_items)}")
        
        # Line 4: Comment/Status (truncated)
        comment = parsed_data.get('comment')
        if comment:
            display_parts.append(f"  Comment: {comment[:60]}{'...' if len(comment) > 60 else ''}")
        elif "position" not in packet_type_str.lower() and not comment and parsed_data.get('type') != "Malformed (Empty Info)" and parsed_data.get('type') != "Malformed (No Info Field)":
            # For non-position, non-malformed packets without a comment, show some raw data
            # Extract the actual info field for this snippet
            info_field_start = packet_body_after_source.find(':')
            actual_info_field = packet_body_after_source[info_field_start+1:] if info_field_start != -1 else packet_body_after_source
            display_parts.append(f"  Data: {actual_info_field[:50]}{'...' if len(actual_info_field) > 50 else ''}")


        self.heard_stations[callsign] = {
            "last_seen": time.time(),
            "raw_packet_body": packet_body_after_source, 
            "parsed_data": parsed_data,     
            "display_string": "\n".join(display_parts) 
        }

    def _emit_station_list_update(self):
        station_list_for_ui = list(self.heard_stations.values())
        station_list_for_ui.sort(key=lambda x: x["last_seen"], reverse=True)
        for station_data in station_list_for_ui:
            for call, data_dict in self.heard_stations.items():
                if data_dict is station_data: 
                    station_data["callsign"] = call
                    break
        self.aprs_station_list_updated.emit(station_list_for_ui)


    def clear_heard_stations(self):
        self.heard_stations.clear()
        self._emit_station_list_update() 
        self.log("Heard APRS stations list cleared.")

    def _parse_aprs_packet_info(self, full_packet_body_after_source: str) -> dict:
        # full_packet_body_after_source is like "DEST,PATH:!lat/lon..." or "DEST,PATH:>status..."
        parsed = {
            "type": "unknown", "latitude": None, "longitude": None, "timestamp": None,
            "symbol_table": None, "symbol_code": None, "comment": None,
            "course": None, "speed": None, "altitude": None
        }
        
        info_field_start = full_packet_body_after_source.find(':')
        if info_field_start == -1:
            parsed["type"] = "Malformed (No Info Field)"
            parsed["comment"] = full_packet_body_after_source 
            return parsed

        aprs_info_field = full_packet_body_after_source[info_field_start+1:]
        body = aprs_info_field.strip() 

        if not body: # Check if the info field is empty after stripping
            parsed["type"] = "Malformed (Empty Info)"
            parsed["comment"] = full_packet_body_after_source # Store the original for context
            return parsed

        try:
            data_type_id = body[0]
            payload = body[1:]
            
            if data_type_id in ['!', '=', '/', '@']:
                # Default to "position" and then refine if compressed/uncompressed can be determined
                parsed["type"] = "position" 
                if (data_type_id == '@' or data_type_id == '/') and len(payload) >= 7 and payload[6] in ['z', 'h', '/']:
                    parsed["timestamp"] = payload[:7]
                    payload = payload[7:] # Adjust payload after extracting timestamp
                # Note: For '!' and '=', timestamp is not standard in the same way.
                # The payload for '!' and '=' starts directly with lat or other data.

                # Re-evaluate body for parsing after potential timestamp removal
                current_body_for_pos_parse = payload if parsed.get("timestamp") else body[1:] # Use payload if timestamp was stripped, else body[1:]

                is_compressed = False
                if len(current_body_for_pos_parse) >= 10 and current_body_for_pos_parse[0] in ['/', '\\'] + [chr(i) for i in range(33,127) if chr(i) not in ['/','\\']]:
                    try:
                        for i in range(1, 9): 
                            if not (33 <= ord(current_body_for_pos_parse[i]) <= 123): 
                                raise ValueError("Not base91")
                        if current_body_for_pos_parse[9] != ' ': 
                             is_compressed = True
                    except (IndexError, ValueError):
                        is_compressed = False 
                elif len(current_body_for_pos_parse) >= 18 and current_body_for_pos_parse[8] in ['/', '\\']: 
                    is_compressed = False

                if is_compressed:
                    parsed["type"] = "position_compressed"
                    parsed["symbol_table"] = current_body_for_pos_parse[0]
                    lat_comp = current_body_for_pos_parse[1:5]; lon_comp = current_body_for_pos_parse[5:9]
                    parsed["symbol_code"] = current_body_for_pos_parse[9]
                    lat, lon = self._decode_aprs_latlon_compressed(lat_comp, lon_comp, parsed["symbol_table"])
                    if lat is not None and lon is not None:
                        parsed["latitude"] = lat; parsed["longitude"] = lon
                    comment_and_ext = current_body_for_pos_parse[10:] 
                    if "/A=" in comment_and_ext:
                        parts = comment_and_ext.split("/A=",1)
                        try: parsed["altitude"] = float(parts[1].split()[0][:6]) 
                        except (ValueError, IndexError): pass
                        comment_and_ext = parts[0] 
                    if len(comment_and_ext) >= 7 and comment_and_ext[3] == '/':
                        try:
                            parsed["course"] = int(comment_and_ext[:3])
                            parsed["speed"] = int(comment_and_ext[4:7]) 
                            parsed["comment"] = comment_and_ext[7:].strip()
                        except (ValueError, IndexError):
                            parsed["comment"] = comment_and_ext.strip() 
                    else:
                        parsed["comment"] = comment_and_ext.strip()
                elif len(current_body_for_pos_parse) >= 18 and current_body_for_pos_parse[8] in ['/', '\\']: # Uncompressed check based on current_body_for_pos_parse
                    parsed["type"] = "position_uncompressed"
                    # Use current_body_for_pos_parse for uncompressed decoding
                    parsed["latitude"], parsed["longitude"] = self._decode_aprs_latlon_uncompressed(current_body_for_pos_parse[0:8], current_body_for_pos_parse[9:18])
                    parsed["symbol_table"] = current_body_for_pos_parse[8]
                    parsed["symbol_code"] = current_body_for_pos_parse[18]
                    comment_start_index = 19
                    extensions_str = current_body_for_pos_parse[comment_start_index:]
                    alt_idx = extensions_str.find("/A=")
                    if alt_idx != -1:
                        try:
                            alt_val_str = extensions_str[alt_idx+3:].split()[0][:6] 
                            parsed["altitude"] = float(alt_val_str) 
                            extensions_str = extensions_str[:alt_idx] + extensions_str[alt_idx+3+len(alt_val_str):].lstrip()
                        except (ValueError, IndexError): pass
                    if len(extensions_str) >= 7 and extensions_str[3] == '/':
                        try:
                            parsed["course"] = int(extensions_str[0:3])
                            parsed["speed"] = int(extensions_str[4:7]) 
                            parsed["comment"] = extensions_str[7:].strip()
                        except (ValueError, IndexError):
                            parsed["comment"] = extensions_str.strip() 
                    else:
                        parsed["comment"] = extensions_str.strip()
                else: # If not clearly compressed or uncompressed but was a position ID
                    parsed["comment"] = current_body_for_pos_parse # Store rest as comment
            
            elif data_type_id == '>':
                parsed["type"] = "status"
                if len(payload) > 6 and payload[6] in ['z', 'h', '/']: 
                    parsed["timestamp"] = payload[:7]
                    parsed["comment"] = payload[7:].strip()
                else:
                    parsed["comment"] = payload.strip()
            elif data_type_id == ':':
                parsed["type"] = "message_or_generic" 
                parsed["comment"] = payload 
            # Add other specific data_type_id checks here if needed
            
        except IndexError:
            # This might happen if 'body' was just a single character after stripping,
            # and trying to access payload = body[1:] fails.
            self.log(f"APRS Parse Error (Index): Info field too short: {body}")
            # Type remains "unknown" or what was set before error.
            # If body was a single char, it's likely an unclassified type.
            if len(body) == 1 and parsed["type"] == "unknown": # If it was just the data_type_id
                 parsed["type"] = "Generic APRS Data" # Or Unclassified
            parsed["comment"] = body # Store what we have
        except Exception as e:
            self.log(f"APRS Parse Exception: {e} on info field: {body}")
            parsed["comment"] = body # Store the problematic part

        # Fallback for types not specifically handled above
        if parsed["type"] == "unknown" and body: 
            parsed["type"] = "Generic APRS Data"
        
        return parsed

    def _decode_aprs_latlon_uncompressed(self, lat_str, lon_str):
        try:
            lat_deg = float(lat_str[0:2]); lat_min = float(lat_str[2:7]) 
            lat_hem = lat_str[7]; latitude = lat_deg + (lat_min / 60.0)
            if lat_hem == 'S': latitude *= -1
            lon_deg = float(lon_str[0:3]); lon_min = float(lon_str[3:8]) 
            lon_hem = lon_str[8]; longitude = lon_deg + (lon_min / 60.0)
            if lon_hem == 'W': longitude *= -1
            return round(latitude, 5), round(longitude, 5)
        except (ValueError, IndexError) as e:
            self.log(f"Error decoding uncompressed lat/lon: {lat_str}, {lon_str} - {e}")
            return None, None

    def _decode_aprs_latlon_compressed(self, lat_comp_str, lon_comp_str, sym_tbl_char):
        try:
            lat_val = 0
            for i in range(4): lat_val = lat_val * 91 + (ord(lat_comp_str[i]) - 33)
            latitude = 90.0 - lat_val / 380926.0
            lon_val = 0
            for i in range(4): lon_val = lon_val * 91 + (ord(lon_comp_str[i]) - 33)
            longitude = -180.0 + lon_val / 190463.0
            return round(latitude, 5), round(longitude, 5)
        except (ValueError, IndexError, TypeError) as e:
            self.log(f"Error decoding compressed lat/lon: {lat_comp_str}, {lon_comp_str} - {e}")
            return None, None


    @Slot()
    def _on_ready_read(self): # For APRS-IS socket
        if not self.is_connected: return
        self._buffer.append(self.socket.readAll())
        while True:
            newline_index = self._buffer.indexOf(b'\r\n')
            if newline_index == -1: break
            line_bytes = self._buffer.left(newline_index)
            self._buffer = self._buffer.mid(newline_index + 2) 
            line_str = ""
            try: line_str = line_bytes.data().decode('ascii').strip()
            except UnicodeDecodeError:
                try: line_str = line_bytes.data().decode('latin-1').strip(); self.log(f"APRS-IS: Decoded line as latin-1: {line_str}")
                except UnicodeDecodeError: self.log(f"APRS-IS: Undecodable line: {line_bytes.data()}"); continue
            if not line_str: continue

            if line_str.startswith("#"): 
                self.log(f"APRS-IS Server Message: {line_str}")
                if "logresp" in line_str:
                    if "unverified" in line_str or "invalid" in line_str:
                        self.aprs_status_update.emit(f"APRS-IS Login FAILED for {self.callsign_ssid}: {line_str}")
                    elif "verified" in line_str:
                        self.aprs_status_update.emit(f"APRS-IS Login successful for {self.callsign_ssid}.")
            else: 
                self.aprs_packet_received.emit(line_str) # This is from APRS-IS
                parts = line_str.split('>', 1)
                if len(parts) > 1:
                    sender_call = parts[0].strip()
                    packet_body_after_source = parts[1].strip() # This is DEST,PATH:BODY
                    if sender_call and sender_call != self.callsign_ssid: 
                        self._update_heard_station(sender_call, packet_body_after_source)
                    
                    # Check for DMs to us, using the full packet_body_after_source
                    info_field_start = packet_body_after_source.find(':')
                    if info_field_start != -1:
                        aprs_info_field = packet_body_after_source[info_field_start+1:]
                        if aprs_info_field.startswith(":") : # Check for message format ::ADDRESSEE:message
                            # This is a simplified check, full message parsing is more complex
                            dm_parts = aprs_info_field.split(':', 2) # Split by first two colons
                            if len(dm_parts) >= 3: # Should be like ['', 'ADDRESSEE', 'message text']
                                recipient_from_packet = dm_parts[1].strip().upper()
                                if recipient_from_packet == self.callsign_ssid: 
                                    message_text = dm_parts[2]
                                    msg_id_start = message_text.rfind('{')
                                    if msg_id_start != -1: 
                                        message_text = message_text[:msg_id_start].strip()
                                    self.log(f"Direct APRS Message FOR US from {sender_call}: {message_text}")
                                    self.aprs_direct_message_received.emit(sender_call, message_text)


# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_message("MainWindow: Initializing...", "debug")
        self.setWindowTitle(f"{APPLICATION_NAME} {APP_VERSION}")
        self.setGeometry(100, 100, 1100, 800) 
        self.setStatusBar(QStatusBar(self))

        self.aprs_dm_dialog = None 
        self.station_detail_dialog = None 

        # APRS Log display settings
        self.current_aprs_log_font_size = DEFAULT_APRS_LOG_FONT_SIZE
        self.current_aprs_log_text_color = DEFAULT_APRS_LOG_TEXT_COLOR
        self.current_aprs_log_bg_color = DEFAULT_APRS_LOG_BG_COLOR
        self.current_aprs_symbol_table = DEFAULT_APRS_SYMBOL_TABLE
        self.current_aprs_symbol_char = DEFAULT_APRS_SYMBOL_CHAR

        # Dedicated Beacon settings
        self.beacon_timer = QTimer(self)
        self.is_beacon_enabled = False
        self.beacon_interval_minutes = DEFAULT_BEACON_INTERVAL_MINUTES
        self.beacon_text = DEFAULT_BEACON_TEXT

        # Manual Status/POS Timed Beacon settings
        self.manual_beacon_timer = QTimer(self)
        self.is_manual_beacon_enabled = False
        self.manual_beacon_interval_minutes = DEFAULT_MANUAL_BEACON_INTERVAL_MINUTES
        
        # TNC Settings
        self.selected_tnc_port = ""
        self.selected_tnc_baud_rate = DEFAULT_TNC_BAUD_RATE
        self.use_tnc_for_sending = False


        self.aprs_manager = APRSManager(self)
        self.log_message("MainWindow: APRSManager initialized.", "debug")

        self.tnc_manager = TNCManager() 
        self.tnc_thread = QThread(self)  
        self.tnc_manager.moveToThread(self.tnc_thread) 
        
        self.tnc_manager.tnc_connected.connect(self.on_tnc_connected_event)
        self.tnc_manager.tnc_disconnected.connect(self.on_tnc_disconnected_event)
        self.tnc_manager.tnc_error.connect(self.on_tnc_error)
        self.tnc_manager.aprs_packet_from_tnc.connect(self.on_aprs_packet_received_from_tnc)
        
        self.tnc_thread.started.connect(self.tnc_manager.initialize_serial_port)
        self.tnc_thread.start()
        self.log_message("MainWindow: TNCManager moved to thread and thread started.", "debug")


        self._setup_ui_elements()
        self.log_message("MainWindow: UI elements created.", "debug")
        self._setup_ui_layout()
        self.log_message("MainWindow: UI layout configured.", "debug")
        self._connect_signals_slots()
        self.log_message("MainWindow: Signals and slots connected.", "debug")

        self.load_settings() 
        self._apply_aprs_log_style()
        self._update_current_aprs_symbol_label()
        self._update_beacon_button_text() 
        self._update_manual_beacon_button_text() 
        self._update_tnc_status_label()
        self.populate_serial_ports()
        self.log_message("MainWindow: Settings applied.", "debug")

        self._update_ui_state() 
        self.log_message(f"Application '{APPLICATION_NAME} {APP_VERSION}' started.", "info")
        self.statusBar().showMessage("Ready.", 5000)
        self.log_message("MainWindow: Initialization complete.", "debug")


    def _get_config_file_path(self):
        config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
        if not config_dir: 
            config_dir = os.path.join(os.path.expanduser("~"), "." + ORGANIZATION_NAME, APPLICATION_NAME)
        if not os.path.exists(config_dir):
            try: os.makedirs(config_dir, exist_ok=True)
            except OSError as e: self.log_message(f"Could not create config directory: {config_dir} - {e}", "error"); return None
        return os.path.join(config_dir, CONFIG_FILE_NAME)

    def load_settings(self):
        config_path = self._get_config_file_path()
        if not config_path or not os.path.exists(config_path):
            self.log_message("No config file found. Using defaults for APRS.", "info")
            if hasattr(self, 'aprs_server_input'): self.aprs_server_input.setText(DEFAULT_APRS_SERVER)
            if hasattr(self, 'aprs_port_input'): self.aprs_port_input.setText(str(DEFAULT_APRS_PORT))
            if hasattr(self, 'aprs_map_url_input'): self.aprs_map_url_input.setText(DEFAULT_APRS_MAP_URL)
            if hasattr(self, 'aprs_status_message_input'): self.aprs_status_message_input.setText(DEFAULT_MANUAL_STATUS_TEXT)
            self.current_aprs_log_font_size = DEFAULT_APRS_LOG_FONT_SIZE
            self.current_aprs_log_text_color = DEFAULT_APRS_LOG_TEXT_COLOR
            self.current_aprs_log_bg_color = DEFAULT_APRS_LOG_BG_COLOR
            if hasattr(self, 'aprs_log_font_size_spinbox'): self.aprs_log_font_size_spinbox.setValue(self.current_aprs_log_font_size)
            self.current_aprs_symbol_table = DEFAULT_APRS_SYMBOL_TABLE
            self.current_aprs_symbol_char = DEFAULT_APRS_SYMBOL_CHAR
            
            self.beacon_text = DEFAULT_BEACON_TEXT
            self.beacon_interval_minutes = DEFAULT_BEACON_INTERVAL_MINUTES
            self.is_beacon_enabled = False 
            if hasattr(self, 'beacon_text_input'): self.beacon_text_input.setText(self.beacon_text)
            if hasattr(self, 'beacon_interval_spinbox'): self.beacon_interval_spinbox.setValue(self.beacon_interval_minutes)
            
            self.manual_beacon_interval_minutes = DEFAULT_MANUAL_BEACON_INTERVAL_MINUTES
            self.is_manual_beacon_enabled = False
            if hasattr(self, 'manual_beacon_interval_spinbox'): self.manual_beacon_interval_spinbox.setValue(self.manual_beacon_interval_minutes)

            self.selected_tnc_port = ""
            self.selected_tnc_baud_rate = DEFAULT_TNC_BAUD_RATE
            self.use_tnc_for_sending = False
            if hasattr(self, 'tnc_baud_combo'): self.tnc_baud_combo.setCurrentText(str(DEFAULT_TNC_BAUD_RATE))
            if hasattr(self, 'tnc_use_sending_checkbox'): self.tnc_use_sending_checkbox.setChecked(False)

            return
        try:
            with open(config_path, 'r', encoding='utf-8') as f: config = json.load(f)
            if hasattr(self, 'aprs_callsign_ssid_input'): self.aprs_callsign_ssid_input.setText(config.get("aprs_callsign_ssid", ""))
            if hasattr(self, 'aprs_passcode_input'): self.aprs_passcode_input.setText(config.get("aprs_passcode", ""))
            if hasattr(self, 'aprs_server_input'): self.aprs_server_input.setText(config.get("aprs_server", DEFAULT_APRS_SERVER))
            if hasattr(self, 'aprs_port_input'): self.aprs_port_input.setText(config.get("aprs_port", str(DEFAULT_APRS_PORT)))
            if hasattr(self, 'aprs_filter_input'): self.aprs_filter_input.setText(config.get("aprs_filter", ""))
            if hasattr(self, 'aprs_latitude_input'): self.aprs_latitude_input.setText(config.get("aprs_latitude", ""))
            if hasattr(self, 'aprs_longitude_input'): self.aprs_longitude_input.setText(config.get("aprs_longitude", ""))
            if hasattr(self, 'aprs_map_url_input'): self.aprs_map_url_input.setText(config.get("aprs_map_url", DEFAULT_APRS_MAP_URL))
            if hasattr(self, 'aprs_status_message_input'): self.aprs_status_message_input.setText(config.get("manual_status_pos_comment", DEFAULT_MANUAL_STATUS_TEXT))


            self.current_aprs_log_font_size = config.get("aprs_log_font_size", DEFAULT_APRS_LOG_FONT_SIZE)
            self.current_aprs_log_text_color = config.get("aprs_log_text_color", DEFAULT_APRS_LOG_TEXT_COLOR)
            self.current_aprs_log_bg_color = config.get("aprs_log_bg_color", DEFAULT_APRS_LOG_BG_COLOR)
            if hasattr(self, 'aprs_log_font_size_spinbox'): self.aprs_log_font_size_spinbox.setValue(self.current_aprs_log_font_size)

            self.current_aprs_symbol_table = config.get("aprs_symbol_table", DEFAULT_APRS_SYMBOL_TABLE)
            self.current_aprs_symbol_char = config.get("aprs_symbol_char", DEFAULT_APRS_SYMBOL_CHAR)

            self.beacon_text = config.get("beacon_text", DEFAULT_BEACON_TEXT)
            self.beacon_interval_minutes = config.get("beacon_interval_minutes", DEFAULT_BEACON_INTERVAL_MINUTES)
            self.is_beacon_enabled = config.get("beacon_enabled", False)
            if hasattr(self, 'beacon_text_input'): self.beacon_text_input.setText(self.beacon_text)
            if hasattr(self, 'beacon_interval_spinbox'): self.beacon_interval_spinbox.setValue(self.beacon_interval_minutes)
            
            self.manual_beacon_interval_minutes = config.get("manual_beacon_interval_minutes", DEFAULT_MANUAL_BEACON_INTERVAL_MINUTES)
            self.is_manual_beacon_enabled = config.get("manual_beacon_enabled", False)
            if hasattr(self, 'manual_beacon_interval_spinbox'): self.manual_beacon_interval_spinbox.setValue(self.manual_beacon_interval_minutes)

            # TNC Settings
            self.selected_tnc_port = config.get("tnc_port", "")
            self.selected_tnc_baud_rate = config.get("tnc_baud_rate", DEFAULT_TNC_BAUD_RATE)
            self.use_tnc_for_sending = config.get("tnc_use_for_sending", False)
            
            if hasattr(self, 'tnc_baud_combo'): self.tnc_baud_combo.setCurrentText(str(self.selected_tnc_baud_rate))
            if hasattr(self, 'tnc_use_sending_checkbox'): self.tnc_use_sending_checkbox.setChecked(self.use_tnc_for_sending)

            self.log_message(f"APRS settings loaded from {config_path}", "info")
        except (IOError, json.JSONDecodeError) as e:
            self.log_message(f"Error loading APRS settings from {config_path}: {e}", "error")
            if hasattr(self, 'aprs_server_input'): self.aprs_server_input.setText(DEFAULT_APRS_SERVER)
            if hasattr(self, 'aprs_port_input'): self.aprs_port_input.setText(str(DEFAULT_APRS_PORT))
            if hasattr(self, 'aprs_status_message_input'): self.aprs_status_message_input.setText(DEFAULT_MANUAL_STATUS_TEXT)
            self.beacon_text = DEFAULT_BEACON_TEXT
            self.beacon_interval_minutes = DEFAULT_BEACON_INTERVAL_MINUTES
            self.is_beacon_enabled = False
            self.manual_beacon_interval_minutes = DEFAULT_MANUAL_BEACON_INTERVAL_MINUTES
            self.is_manual_beacon_enabled = False
            self.selected_tnc_port = ""
            self.selected_tnc_baud_rate = DEFAULT_TNC_BAUD_RATE
            self.use_tnc_for_sending = False


    def save_settings(self):
        config_path = self._get_config_file_path()
        if not config_path: self.log_message("Could not determine config path. Settings not saved.", "error"); return

        config = {
            "aprs_callsign_ssid": self.aprs_callsign_ssid_input.text(),
            "aprs_passcode": self.aprs_passcode_input.text(),
            "aprs_server": self.aprs_server_input.text(),
            "aprs_port": self.aprs_port_input.text(),
            "aprs_filter": self.aprs_filter_input.text(),
            "aprs_latitude": self.aprs_latitude_input.text(),
            "aprs_longitude": self.aprs_longitude_input.text(),
            "aprs_map_url": self.aprs_map_url_input.text(),
            "manual_status_pos_comment": self.aprs_status_message_input.text(), 
            "aprs_log_font_size": self.current_aprs_log_font_size,
            "aprs_log_text_color": self.current_aprs_log_text_color,
            "aprs_log_bg_color": self.current_aprs_log_bg_color,
            "aprs_symbol_table": self.current_aprs_symbol_table,
            "aprs_symbol_char": self.current_aprs_symbol_char,
            # Dedicated Beacon settings
            "beacon_text": self.beacon_text_input.text(),
            "beacon_interval_minutes": self.beacon_interval_spinbox.value(),
            "beacon_enabled": self.is_beacon_enabled,
            # Manual Status/POS Beacon settings
            "manual_beacon_interval_minutes": self.manual_beacon_interval_spinbox.value(),
            "manual_beacon_enabled": self.is_manual_beacon_enabled,
            # TNC Settings
            "tnc_port": self.tnc_port_combo.currentText() if hasattr(self, 'tnc_port_combo') and self.tnc_port_combo.currentText() != "No Ports Found" else self.selected_tnc_port,
            "tnc_baud_rate": int(self.tnc_baud_combo.currentText()) if hasattr(self, 'tnc_baud_combo') else self.selected_tnc_baud_rate,
            "tnc_use_for_sending": self.tnc_use_sending_checkbox.isChecked() if hasattr(self, 'tnc_use_sending_checkbox') else self.use_tnc_for_sending,
        }
        try:
            with open(config_path, 'w', encoding='utf-8') as f: json.dump(config, f, indent=4)
            self.log_message(f"APRS settings saved to {config_path}", "info")
        except IOError as e: self.log_message(f"Error saving APRS settings to {config_path}: {e}", "error")

    def log_message(self, message, level="info"):
        timestamp = time.strftime('%H:%M:%S')
        prefix_map = {"info": "INFO:", "error": "ERROR:", "success": "SUCCESS:", "warning": "WARN:", "debug": "DEBUG:", "aprs": "APRS:", "aprs_tx": "APRS TX:", "aprs_rx_dm": "APRS DM RX:", "beacon":"BEACON:", "tnc":"TNC:"}
        prefix = prefix_map.get(level, "")
        formatted_message = f"[{timestamp}] {prefix} {message}"
        if hasattr(self, 'log_text_edit'): self.log_text_edit.append(formatted_message)
        print(f"[UI] {formatted_message}") 
        if hasattr(self, 'statusBar'):
            if level == "error": self.statusBar().showMessage(f"Error: {message}", 7000)
            elif level == "success": self.statusBar().showMessage(message, 5000)
            elif level == "warning": self.statusBar().showMessage(f"Warning: {message}", 6000)


    def _update_ui_state(self):
        self.log_message(f"Updating UI state: APRS-IS Conn={self.aprs_manager.is_connected}, TNC Conn={self.tnc_manager.is_tnc_connected()}, DedBeacon={self.is_beacon_enabled}, ManBeacon={self.is_manual_beacon_enabled}", "debug")
        is_aprs_is_connected = self.aprs_manager.is_connected
        is_tnc_connected = self.tnc_manager.is_tnc_connected()

        # APRS-IS UI elements
        self.aprs_connect_button.setEnabled(not is_aprs_is_connected)
        self.aprs_disconnect_button.setEnabled(is_aprs_is_connected)
        
        # TNC UI elements
        self.tnc_connect_button.setEnabled(not is_tnc_connected and bool(self.tnc_port_combo.currentText()) and self.tnc_port_combo.currentText() != "No Ports Found")
        self.tnc_disconnect_button.setEnabled(is_tnc_connected)
        self.tnc_port_combo.setEnabled(not is_tnc_connected)
        self.tnc_baud_combo.setEnabled(not is_tnc_connected)
        self.tnc_refresh_ports_button.setEnabled(not is_tnc_connected)


        can_send_via_aprs_is = is_aprs_is_connected and self.aprs_passcode_input.text().strip() != "-1"
        can_send_via_tnc = is_tnc_connected 
        can_send_aprs_data = (not self.use_tnc_for_sending and can_send_via_aprs_is) or \
                             (self.use_tnc_for_sending and can_send_via_tnc)

        self.aprs_send_status_button.setEnabled(can_send_aprs_data) 
        self.aprs_send_dm_button.setEnabled(can_send_aprs_data)

        self.aprs_callsign_ssid_input.setEnabled(not is_aprs_is_connected and not is_tnc_connected) 
        self.aprs_passcode_input.setEnabled(not is_aprs_is_connected) 
        self.aprs_server_input.setEnabled(not is_aprs_is_connected)   
        self.aprs_port_input.setEnabled(not is_aprs_is_connected)     
        self.aprs_filter_input.setEnabled(not is_aprs_is_connected)   
        
        self.aprs_latitude_input.setEnabled(True)
        self.aprs_longitude_input.setEnabled(True)
        self.aprs_select_symbol_button.setEnabled(True) 
        self.aprs_status_message_input.setEnabled(True) 

        self.aprs_dm_recipient_input.setEnabled(is_aprs_is_connected or is_tnc_connected) 
        self.aprs_dm_message_input.setEnabled(is_aprs_is_connected or is_tnc_connected) 

        self.aprs_map_url_input.setEnabled(True) 
        self.aprs_map_go_button.setEnabled(True)
        self.aprs_map_home_button.setEnabled(True)

        self.aprs_station_list_widget.setEnabled(is_aprs_is_connected or is_tnc_connected)
        self.aprs_clear_station_list_button.setEnabled(is_aprs_is_connected or is_tnc_connected)
        self.aprs_track_selected_station_button.setEnabled((is_aprs_is_connected or is_tnc_connected) and self.aprs_station_list_widget.currentItem() is not None)

        # Beacon UI
        self.beacon_enable_button.setEnabled(is_aprs_is_connected or is_tnc_connected) 
        self.beacon_text_input.setEnabled(True) 
        self.beacon_interval_spinbox.setEnabled(True) 
        self._update_beacon_button_text()

        # Manual Status/POS Beacon UI
        self.manual_beacon_enable_button.setEnabled(is_aprs_is_connected or is_tnc_connected)
        self.manual_beacon_interval_spinbox.setEnabled(True)
        self._update_manual_beacon_button_text()
        self._update_tnc_status_label()


    def _setup_ui_elements(self):
        self.log_text_edit = QTextEdit(); self.log_text_edit.setReadOnly(True)

        menubar = self.menuBar(); file_menu = menubar.addMenu("&File"); help_menu = menubar.addMenu("&Help")
        exit_action = QAction("E&xit", self, triggered=self.close); file_menu.addAction(exit_action)
        about_action = QAction("&About", self, triggered=self.show_about_dialog); help_menu.addAction(about_action)

        # --- APRS Common Config ---
        self.aprs_callsign_ssid_input = QLineEdit(); self.aprs_callsign_ssid_input.setPlaceholderText("CALLSIGN-SSID (e.g., N0CALL-9)")
        self.aprs_latitude_input = QLineEdit(); self.aprs_latitude_input.setPlaceholderText("Latitude (e.g., 34.0522)")
        self.aprs_longitude_input = QLineEdit(); self.aprs_longitude_input.setPlaceholderText("Longitude (e.g., -118.2437)")
        self.aprs_select_symbol_button = QPushButton(f"{ICON_SYMBOL_PICKER} Select Symbol")
        self.aprs_current_symbol_label = QLabel(f"Symbol: {self.current_aprs_symbol_table}{self.current_aprs_symbol_char}")
        
        # --- APRS-IS Specific ---
        self.aprs_passcode_input = QLineEdit(); self.aprs_passcode_input.setPlaceholderText("APRS-IS Passcode (-1 for RX only)")
        self.aprs_passcode_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.aprs_server_input = QLineEdit(DEFAULT_APRS_SERVER)
        self.aprs_port_input = QLineEdit(str(DEFAULT_APRS_PORT))
        self.aprs_filter_input = QLineEdit(); self.aprs_filter_input.setPlaceholderText("Optional APRS Filter (e.g., r/37/-77/100)")
        self.aprs_connect_button = QPushButton(f"{ICON_APRS} Connect APRS-IS")
        self.aprs_disconnect_button = QPushButton(f"{ICON_DISCONNECT} Disconnect APRS-IS")

        # --- TNC Specific ---
        self.tnc_port_combo = QComboBox()
        self.tnc_refresh_ports_button = QPushButton(ICON_REFRESH)
        self.tnc_baud_combo = QComboBox()
        self.tnc_baud_combo.addItems(["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self.tnc_baud_combo.setCurrentText(str(DEFAULT_TNC_BAUD_RATE))
        self.tnc_connect_button = QPushButton(f"{ICON_CONNECT} Connect TNC")
        self.tnc_disconnect_button = QPushButton(f"{ICON_DISCONNECT} Disconnect TNC")
        self.tnc_status_label = QLabel("TNC Status: Disconnected")
        self.tnc_use_sending_checkbox = QCheckBox("Use TNC for Sending")


        # --- APRS Send / Beaconing ---
        self.aprs_status_message_input = QLineEdit(); self.aprs_status_message_input.setPlaceholderText("Manual Status/Pos Comment") 
        self.aprs_send_status_button = QPushButton(f"{ICON_LOCATION} Send Manual Pos/Status") 
        
        self.beacon_text_input = QLineEdit(DEFAULT_BEACON_TEXT)
        self.beacon_text_input.setPlaceholderText("Dedicated Automatic Beacon Text")
        self.beacon_interval_spinbox = QSpinBox()
        self.beacon_interval_spinbox.setRange(1, 1440) 
        self.beacon_interval_spinbox.setValue(DEFAULT_BEACON_INTERVAL_MINUTES)
        self.beacon_interval_spinbox.setSuffix(" min")
        self.beacon_enable_button = QPushButton() 

        self.manual_beacon_interval_spinbox = QSpinBox()
        self.manual_beacon_interval_spinbox.setRange(1, 1440)
        self.manual_beacon_interval_spinbox.setValue(DEFAULT_MANUAL_BEACON_INTERVAL_MINUTES)
        self.manual_beacon_interval_spinbox.setSuffix(" min")
        self.manual_beacon_enable_button = QPushButton()

        # --- APRS DM ---
        self.aprs_dm_recipient_input = QLineEdit(); self.aprs_dm_recipient_input.setPlaceholderText("Recipient Callsign-SSID")
        self.aprs_dm_message_input = QLineEdit(); self.aprs_dm_message_input.setPlaceholderText("Direct Message Text")
        self.aprs_send_dm_button = QPushButton(f"{ICON_MESSAGE} Send Direct Msg")
        
        # --- APRS Log & List ---
        self.aprs_log_text_edit = QTextEdit(); self.aprs_log_text_edit.setReadOnly(True) 
        self.aprs_clear_log_button = QPushButton(f"{ICON_CLEAR} Clear APRS Log")
        self.aprs_log_font_size_spinbox = QSpinBox()
        self.aprs_log_font_size_spinbox.setRange(6, 24); self.aprs_log_font_size_spinbox.setSuffix("pt")
        self.aprs_log_font_size_spinbox.setValue(self.current_aprs_log_font_size)
        self.aprs_log_text_color_button = QPushButton(f"{ICON_COLOR_TEXT} Text Color")
        self.aprs_log_bg_color_button = QPushButton(f"{ICON_COLOR_BG} BG Color")
        self.aprs_station_list_widget = QListWidget()
        self.aprs_clear_station_list_button = QPushButton(f"{ICON_CLEAR} Clear List")
        self.aprs_track_selected_station_button = QPushButton(f"{ICON_MAP} Track on Map")

        # APRS Map UI Elements
        self.aprs_map_view = QWebEngineView()
        self.aprs_map_url_input = QLineEdit(DEFAULT_APRS_MAP_URL)
        self.aprs_map_go_button = QPushButton(f"{ICON_GO} Go")
        self.aprs_map_home_button = QPushButton(f"{ICON_MAP} Default Map")

        # User Guide UI Element
        self.guide_display_area = QTextEdit()
        self.guide_display_area.setReadOnly(True)
        formatted_guide = USER_GUIDE_DOCUMENTATION
        self.guide_display_area.setMarkdown(formatted_guide)


    def _setup_ui_layout(self):
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_v_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_v_layout.addWidget(self.tab_widget, 3)

        # --- APRS Tab (Combined APRS-IS and TNC) ---
        aprs_main_tab_widget = QWidget()
        aprs_main_tab_layout = QVBoxLayout(aprs_main_tab_widget)
        self.tab_widget.addTab(aprs_main_tab_widget, f"{ICON_APRS}/{ICON_TNC} APRS-IS & TNC")

        aprs_top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Panel: Configurations and Sending
        aprs_left_panel = QWidget(); aprs_left_layout = QVBoxLayout(aprs_left_panel)

        # Common APRS Config Group
        common_aprs_config_group = QGroupBox("Common APRS Configuration")
        common_aprs_config_layout = QGridLayout(common_aprs_config_group)
        common_aprs_config_layout.addWidget(QLabel("APRS Callsign-SSID:"), 0, 0); common_aprs_config_layout.addWidget(self.aprs_callsign_ssid_input, 0, 1, 1, 3)
        common_aprs_config_layout.addWidget(QLabel(f"{ICON_LOCATION} Latitude (Dec Deg):"), 1, 0); common_aprs_config_layout.addWidget(self.aprs_latitude_input, 1, 1)
        common_aprs_config_layout.addWidget(QLabel(f"{ICON_LOCATION} Longitude (Dec Deg):"), 1, 2); common_aprs_config_layout.addWidget(self.aprs_longitude_input, 1, 3)
        symbol_layout = QHBoxLayout(); symbol_layout.addWidget(self.aprs_current_symbol_label); symbol_layout.addWidget(self.aprs_select_symbol_button); symbol_layout.addStretch()
        common_aprs_config_layout.addLayout(symbol_layout, 2,0,1,4)
        common_aprs_config_layout.setColumnStretch(1,1); common_aprs_config_layout.setColumnStretch(3,1)
        aprs_left_layout.addWidget(common_aprs_config_group)

        # APRS-IS Config Group
        aprs_is_config_group = QGroupBox("APRS-IS Settings")
        aprs_is_config_layout = QGridLayout(aprs_is_config_group)
        aprs_is_config_layout.addWidget(QLabel("APRS-IS Server:"), 0, 0); aprs_is_config_layout.addWidget(self.aprs_server_input, 0, 1)
        aprs_is_config_layout.addWidget(QLabel("Port:"), 0, 2); aprs_is_config_layout.addWidget(self.aprs_port_input, 0, 3)
        aprs_is_config_layout.addWidget(QLabel("APRS Passcode:"), 1, 0); aprs_is_config_layout.addWidget(self.aprs_passcode_input, 1, 1)
        aprs_is_config_layout.addWidget(QLabel("Filter (optional):"), 1, 2); aprs_is_config_layout.addWidget(self.aprs_filter_input, 1, 3)
        aprs_is_conn_buttons_layout = QHBoxLayout(); aprs_is_conn_buttons_layout.addWidget(self.aprs_connect_button); aprs_is_conn_buttons_layout.addWidget(self.aprs_disconnect_button); aprs_is_conn_buttons_layout.addStretch()
        aprs_is_config_layout.addLayout(aprs_is_conn_buttons_layout, 2,0,1,4)
        aprs_is_config_layout.setColumnStretch(1,1); aprs_is_config_layout.setColumnStretch(3,1)
        aprs_left_layout.addWidget(aprs_is_config_group)
        
        # TNC Config Group
        tnc_config_group = QGroupBox(f"{ICON_TNC} TNC (KISS Mode) Settings")
        tnc_config_layout = QGridLayout(tnc_config_group)
        tnc_port_layout = QHBoxLayout(); tnc_port_layout.addWidget(self.tnc_port_combo, 1); tnc_port_layout.addWidget(self.tnc_refresh_ports_button)
        tnc_config_layout.addWidget(QLabel("Serial Port:"), 0,0); tnc_config_layout.addLayout(tnc_port_layout, 0,1)
        tnc_config_layout.addWidget(QLabel("Baud Rate:"), 0,2); tnc_config_layout.addWidget(self.tnc_baud_combo, 0,3)
        tnc_conn_buttons_layout = QHBoxLayout(); tnc_conn_buttons_layout.addWidget(self.tnc_connect_button); tnc_conn_buttons_layout.addWidget(self.tnc_disconnect_button); tnc_conn_buttons_layout.addStretch()
        tnc_config_layout.addLayout(tnc_conn_buttons_layout, 1,0,1,2)
        tnc_config_layout.addWidget(self.tnc_use_sending_checkbox, 1,2,1,2)
        tnc_config_layout.addWidget(self.tnc_status_label, 2,0,1,4)
        tnc_config_layout.setColumnStretch(1,1); tnc_config_layout.setColumnStretch(3,1)
        aprs_left_layout.addWidget(tnc_config_group)


        # Dedicated Beacon Group
        beacon_group = QGroupBox("Automatic Beacon (Dedicated Text)")
        beacon_layout = QGridLayout(beacon_group)
        beacon_layout.addWidget(QLabel("Beacon Text:"), 0, 0); beacon_layout.addWidget(self.beacon_text_input, 0, 1, 1, 2)
        beacon_layout.addWidget(QLabel("Interval:"), 1, 0); beacon_layout.addWidget(self.beacon_interval_spinbox, 1, 1)
        beacon_layout.addWidget(self.beacon_enable_button, 1, 2)
        beacon_layout.setColumnStretch(1, 1)
        aprs_left_layout.addWidget(beacon_group)

        # Manual Send / DM / Timed Status Group
        aprs_send_group = QGroupBox("Manual Send / Direct Message / Timed Status"); 
        aprs_send_layout = QGridLayout(aprs_send_group)
        aprs_send_layout.addWidget(QLabel("Status/Pos Comment:"), 0, 0); aprs_send_layout.addWidget(self.aprs_status_message_input, 0, 1, 1, 2) 
        aprs_send_layout.addWidget(self.aprs_send_status_button, 0, 3) 
        aprs_send_layout.addWidget(QLabel("Status Beacon Interval:"), 1,0); aprs_send_layout.addWidget(self.manual_beacon_interval_spinbox, 1,1)
        aprs_send_layout.addWidget(self.manual_beacon_enable_button, 1,2,1,2) 
        aprs_send_layout.addWidget(QLabel("DM Recipient:"), 2, 0); aprs_send_layout.addWidget(self.aprs_dm_recipient_input, 2, 1)
        aprs_send_layout.addWidget(QLabel("DM Text:"), 3, 0); aprs_send_layout.addWidget(self.aprs_dm_message_input, 3, 1)
        aprs_send_layout.addWidget(self.aprs_send_dm_button, 3, 2, 1, 2) 
        aprs_send_layout.setColumnStretch(1, 1)
        aprs_left_layout.addWidget(aprs_send_group)
        aprs_left_layout.addStretch()
        
        aprs_top_splitter.addWidget(aprs_left_panel)

        # Right Panel: Logs and Lists
        aprs_right_panel_widget = QWidget()
        aprs_right_panel_layout = QVBoxLayout(aprs_right_panel_widget)
        aprs_log_display_group = QGroupBox("APRS Log (APRS-IS & TNC)"); 
        aprs_log_display_layout = QVBoxLayout(aprs_log_display_group)
        aprs_log_controls_layout = QHBoxLayout()
        aprs_log_controls_layout.addWidget(QLabel(f"{ICON_FONT} Size:"))
        aprs_log_controls_layout.addWidget(self.aprs_log_font_size_spinbox)
        aprs_log_controls_layout.addWidget(self.aprs_log_text_color_button)
        aprs_log_controls_layout.addWidget(self.aprs_log_bg_color_button)
        aprs_log_controls_layout.addStretch()
        aprs_log_controls_layout.addWidget(self.aprs_clear_log_button)
        aprs_log_display_layout.addLayout(aprs_log_controls_layout)
        aprs_log_display_layout.addWidget(self.aprs_log_text_edit, 1) 
        aprs_right_panel_layout.addWidget(aprs_log_display_group, 2) 
        aprs_station_list_group = QGroupBox("Heard APRS Stations"); 
        aprs_station_list_layout = QVBoxLayout(aprs_station_list_group)
        aprs_station_list_layout.addWidget(self.aprs_station_list_widget, 1)
        aprs_station_list_buttons_layout = QHBoxLayout()
        aprs_station_list_buttons_layout.addStretch()
        aprs_station_list_buttons_layout.addWidget(self.aprs_track_selected_station_button)
        aprs_station_list_buttons_layout.addWidget(self.aprs_clear_station_list_button)
        aprs_station_list_layout.addLayout(aprs_station_list_buttons_layout)
        aprs_right_panel_layout.addWidget(aprs_station_list_group, 1)
        aprs_top_splitter.addWidget(aprs_right_panel_widget)
        
        aprs_top_splitter.setSizes([520, 480]) 
        aprs_main_tab_layout.addWidget(aprs_top_splitter)


        # --- APRS Map Tab ---
        aprs_map_tab_widget = QWidget(); aprs_map_tab_widget.setObjectName("aprsMapTabWidget") 
        aprs_map_layout = QVBoxLayout(aprs_map_tab_widget)
        self.tab_widget.addTab(aprs_map_tab_widget, f"{ICON_MAP} APRS Map")
        aprs_map_nav_layout = QHBoxLayout(); aprs_map_nav_layout.addWidget(QLabel("URL/Callsign:")); aprs_map_nav_layout.addWidget(self.aprs_map_url_input, 1)
        aprs_map_nav_layout.addWidget(self.aprs_map_go_button); aprs_map_nav_layout.addWidget(self.aprs_map_home_button)
        aprs_map_layout.addLayout(aprs_map_nav_layout); aprs_map_layout.addWidget(self.aprs_map_view, 1)

        # --- User Guide Tab ---
        guide_tab_widget = QWidget()
        guide_layout = QVBoxLayout(guide_tab_widget)
        guide_layout.addWidget(self.guide_display_area)
        self.tab_widget.addTab(guide_tab_widget, f"{ICON_GUIDE} User Guide")


        # --- Log Panel (Common Activity Log) ---
        log_panel_widget = QFrame(); log_panel_widget.setFrameShape(QFrame.Shape.StyledPanel)
        log_panel_layout = QVBoxLayout(log_panel_widget)
        log_panel_layout.addWidget(QLabel(f"{ICON_LOG} Activity Log:")); log_panel_layout.addWidget(self.log_text_edit,1) 
        main_v_layout.addWidget(log_panel_widget, 1) 


    def _connect_signals_slots(self):
        # APRS-IS Connections
        self.aprs_connect_button.clicked.connect(self.on_aprs_connect_clicked)
        self.aprs_disconnect_button.clicked.connect(self.on_aprs_disconnect_clicked)
        self.aprs_manager.aprs_connected.connect(self.on_aprs_is_connected_event) 
        self.aprs_manager.aprs_disconnected.connect(self.on_aprs_is_disconnected_event) 
        self.aprs_manager.aprs_packet_received.connect(self.on_aprs_packet_received_from_is) 
        self.aprs_manager.aprs_status_update.connect(self.on_aprs_status_update) 
        self.aprs_manager.aprs_direct_message_received.connect(self.handle_incoming_aprs_dm)
        self.aprs_manager.aprs_station_list_updated.connect(self.update_aprs_station_list_ui)

        # TNC Connections (Signals from TNCManager already connected in __init__)
        self.tnc_connect_button.clicked.connect(self.on_tnc_connect_clicked)
        self.tnc_disconnect_button.clicked.connect(self.on_tnc_disconnect_clicked)
        self.tnc_refresh_ports_button.clicked.connect(self.populate_serial_ports)
        self.tnc_port_combo.currentIndexChanged.connect(self.on_tnc_port_selection_changed)
        self.tnc_baud_combo.currentTextChanged.connect(self.on_tnc_baud_rate_changed)
        self.tnc_use_sending_checkbox.stateChanged.connect(self.on_tnc_use_sending_changed)

        # APRS Send/DM Buttons
        self.aprs_send_status_button.clicked.connect(self.on_aprs_send_status_clicked)
        self.aprs_send_dm_button.clicked.connect(self.on_aprs_send_dm_clicked)
        
        # APRS Beacons
        self.beacon_enable_button.clicked.connect(self.on_beacon_enable_clicked)
        self.beacon_interval_spinbox.valueChanged.connect(self.on_beacon_interval_changed)
        self.beacon_text_input.textChanged.connect(self.on_beacon_text_changed) 
        self.beacon_timer.timeout.connect(self.send_automatic_beacon)

        self.manual_beacon_enable_button.clicked.connect(self.on_manual_beacon_enable_clicked)
        self.manual_beacon_interval_spinbox.valueChanged.connect(self.on_manual_beacon_interval_changed)
        self.manual_beacon_timer.timeout.connect(self.send_manual_periodic_beacon)


        # APRS Log Display Controls
        self.aprs_clear_log_button.clicked.connect(self.on_aprs_clear_log_clicked) 
        self.aprs_log_font_size_spinbox.valueChanged.connect(self.on_aprs_log_font_size_changed)
        self.aprs_log_text_color_button.clicked.connect(self.on_aprs_log_text_color_clicked)
        self.aprs_log_bg_color_button.clicked.connect(self.on_aprs_log_bg_color_clicked)
        self.aprs_select_symbol_button.clicked.connect(self.on_aprs_select_symbol_button_clicked)


        # APRS Station List Controls
        self.aprs_clear_station_list_button.clicked.connect(self.on_aprs_clear_station_list_clicked)
        self.aprs_track_selected_station_button.clicked.connect(self.on_aprs_track_selected_station_clicked)
        self.aprs_station_list_widget.itemClicked.connect(self.on_aprs_station_item_clicked_for_details) 
        self.aprs_station_list_widget.itemDoubleClicked.connect(self.on_aprs_station_item_double_clicked_for_map) 
        self.aprs_station_list_widget.currentItemChanged.connect(self.on_aprs_station_selection_changed)


        # APRS Map Connections
        self.aprs_map_go_button.clicked.connect(self.on_aprs_map_go_clicked)
        self.aprs_map_home_button.clicked.connect(self.on_aprs_map_home_clicked)
        self.aprs_map_url_input.returnPressed.connect(self.on_aprs_map_go_clicked)
        self.tab_widget.currentChanged.connect(self.on_tab_changed) 

    # --- TNC Methods ---
    def populate_serial_ports(self):
        self.tnc_port_combo.clear()
        ports = TNCManager.list_available_ports() 
        if not ports:
            self.tnc_port_combo.addItem("No Ports Found")
            self.tnc_port_combo.setEnabled(False)
            self.log_message("No serial ports found.", "tnc")
        else:
            self.tnc_port_combo.setEnabled(True)
            for port_info in ports:
                self.tnc_port_combo.addItem(port_info.portName(), port_info) 
            self.log_message(f"Available serial ports: {[p.portName() for p in ports]}", "tnc")
        
        if self.selected_tnc_port: 
            index = self.tnc_port_combo.findText(self.selected_tnc_port)
            if index != -1:
                self.tnc_port_combo.setCurrentIndex(index)
            elif self.tnc_port_combo.count() > 0 and self.tnc_port_combo.itemText(0) != "No Ports Found":
                self.selected_tnc_port = self.tnc_port_combo.currentText() 
        elif self.tnc_port_combo.count() > 0 and self.tnc_port_combo.itemText(0) != "No Ports Found":
             self.selected_tnc_port = self.tnc_port_combo.currentText() 

        self._update_ui_state()


    @Slot(int)
    def on_tnc_port_selection_changed(self, index):
        if index >= 0 and self.tnc_port_combo.currentText() != "No Ports Found":
            self.selected_tnc_port = self.tnc_port_combo.currentText()
            self.log_message(f"TNC port selected: {self.selected_tnc_port}", "tnc")
            self.save_settings()
        else:
            self.selected_tnc_port = "" 
        self._update_ui_state() 

    @Slot(str)
    def on_tnc_baud_rate_changed(self, baud_rate_str):
        try:
            self.selected_tnc_baud_rate = int(baud_rate_str)
            self.log_message(f"TNC baud rate set to: {self.selected_tnc_baud_rate}", "tnc")
            self.save_settings()
        except ValueError:
            self.log_message(f"Invalid TNC baud rate input: {baud_rate_str}", "error")

    @Slot(int)
    def on_tnc_use_sending_changed(self, state):
        self.use_tnc_for_sending = bool(state == Qt.CheckState.Checked.value)
        self.log_message(f"Use TNC for sending set to: {self.use_tnc_for_sending}", "tnc")
        self.save_settings()
        self._update_ui_state() 

    @Slot()
    def on_tnc_connect_clicked(self):
        port_name = self.tnc_port_combo.currentText()
        if not port_name or port_name == "No Ports Found":
            QMessageBox.warning(self, "TNC Error", "Please select a valid serial port.")
            return
        
        try:
            baud_rate = int(self.tnc_baud_combo.currentText())
        except ValueError:
            QMessageBox.warning(self, "TNC Error", "Invalid baud rate selected.")
            return

        self.tnc_manager.set_port_config(port_name, baud_rate)
        QMetaObject.invokeMethod(self.tnc_manager, "connect_tnc", Qt.ConnectionType.QueuedConnection)
        self.tnc_status_label.setText(f"TNC Status: Connecting to {port_name}...")
        self.tnc_status_label.setStyleSheet("color: orange;")
        self._update_ui_state()

    @Slot()
    def on_tnc_disconnect_clicked(self):
        QMetaObject.invokeMethod(self.tnc_manager, "disconnect_tnc", Qt.ConnectionType.QueuedConnection)

    @Slot()
    def on_tnc_connected_event(self):
        self.log_message(f"TNC connected successfully on {self.tnc_manager.port_name}.", "tnc")
        self.statusBar().showMessage(f"TNC Connected: {self.tnc_manager.port_name}", 5000)
        self._update_tnc_status_label()
        self._update_ui_state()
        
        if self.use_tnc_for_sending:
            if self.is_beacon_enabled:
                self._start_beacon_timer()
                self.log_message("Dedicated beacon (re)started for TNC.", "beacon")
                self.send_automatic_beacon(is_initial=True)
            if self.is_manual_beacon_enabled:
                self._start_manual_beacon_timer()
                self.log_message("Timed Status/POS beacon (re)started for TNC.", "beacon")
                self.send_manual_periodic_beacon(is_initial=True)


    @Slot()
    def on_tnc_disconnected_event(self):
        self.log_message("TNC disconnected.", "tnc")
        self.statusBar().showMessage("TNC Disconnected.", 5000)
        if self.beacon_timer.isActive() and self.use_tnc_for_sending:
            self._stop_beacon_timer()
            self.log_message("Dedicated beacon timer stopped (TNC source).", "beacon")
        if self.manual_beacon_timer.isActive() and self.use_tnc_for_sending:
            self._stop_manual_beacon_timer()
            self.log_message("Timed Status/POS beacon timer stopped (TNC source).", "beacon")
        self._update_tnc_status_label()
        self._update_ui_state()

    @Slot(str)
    def on_tnc_error(self, error_message):
        self.log_message(f"TNC Error: {error_message}", "error")
        self.statusBar().showMessage(f"TNC Error: {error_message[:50]}...", 7000)
        self._update_tnc_status_label() 
        self._update_ui_state()

    @Slot(str)
    def on_aprs_packet_received_from_tnc(self, aprs_packet_str):
        self.log_message(f"APRS PKT via TNC: {aprs_packet_str}", "aprs")
        self.aprs_log_text_edit.append(f"[TNC] {aprs_packet_str}") 
        parts = aprs_packet_str.split('>', 1)
        if len(parts) > 1:
            sender_call = parts[0].strip()
            packet_body_after_source = parts[1].strip() # This is DEST,PATH:BODY
            if sender_call and sender_call != self.aprs_callsign_ssid_input.text().strip():
                self.aprs_manager._update_heard_station(sender_call, packet_body_after_source) 
            
            # Check for DMs to us, using the full packet_body_after_source
            info_field_start = packet_body_after_source.find(':')
            if info_field_start != -1:
                aprs_info_field = packet_body_after_source[info_field_start+1:]
                if aprs_info_field.startswith(":") : 
                    dm_parts = aprs_info_field.split(':', 2) 
                    if len(dm_parts) >= 3: 
                        recipient_from_packet = dm_parts[1].strip().upper()
                        my_call = self.aprs_callsign_ssid_input.text().strip().upper()
                        if recipient_from_packet == my_call:
                            message_text = dm_parts[2]
                            msg_id_start = message_text.rfind('{')
                            if msg_id_start != -1: message_text = message_text[:msg_id_start].strip()
                            self.handle_incoming_aprs_dm(sender_call, message_text)


    def _update_tnc_status_label(self):
        if self.tnc_manager.is_tnc_connected():
            self.tnc_status_label.setText(f"TNC Status: Connected to {self.tnc_manager.port_name} @ {self.tnc_manager.baud_rate} baud")
            self.tnc_status_label.setStyleSheet("color: green;")
        else:
            self.tnc_status_label.setText("TNC Status: Disconnected")
            self.tnc_status_label.setStyleSheet("")


    # --- Dedicated Beacon Methods --- 
    def _update_beacon_button_text(self):
        if self.is_beacon_enabled:
            self.beacon_enable_button.setText(f"{ICON_BEACON_ON} Disable Ded. Beacon")
            self.beacon_enable_button.setStyleSheet("background-color: lightgreen;")
        else:
            self.beacon_enable_button.setText(f"{ICON_BEACON_OFF} Enable Ded. Beacon")
            self.beacon_enable_button.setStyleSheet("") 

    def _start_beacon_timer(self):
        if self.beacon_interval_minutes > 0:
            self.beacon_timer.start(self.beacon_interval_minutes * 60 * 1000)
            self.log_message(f"Dedicated beacon timer started. Interval: {self.beacon_interval_minutes} minutes.", "beacon")

    def _stop_beacon_timer(self):
        self.beacon_timer.stop()
        self.log_message("Dedicated beacon timer stopped.", "beacon")

    @Slot()
    def on_beacon_enable_clicked(self): 
        can_operate_beacon = (self.aprs_manager.is_connected and not self.use_tnc_for_sending) or \
                             (self.tnc_manager.is_tnc_connected() and self.use_tnc_for_sending)
        
        if not can_operate_beacon:
            QMessageBox.warning(self, "Beacon Error", "Connect to APRS-IS or TNC (and select it) before enabling the dedicated beacon.")
            return

        self.is_beacon_enabled = not self.is_beacon_enabled
        self._update_beacon_button_text()
        self.save_settings() 

        if self.is_beacon_enabled:
            self.beacon_text = self.beacon_text_input.text() 
            self.beacon_interval_minutes = self.beacon_interval_spinbox.value()
            self._start_beacon_timer()
            self.log_message("Dedicated automatic beacon enabled. Sending initial beacon.", "beacon")
            self.send_automatic_beacon(is_initial=True)
        else:
            self._stop_beacon_timer()
            self.log_message("Dedicated automatic beacon disabled.", "beacon")
        self._update_ui_state()


    @Slot(int)
    def on_beacon_interval_changed(self, minutes): 
        self.beacon_interval_minutes = minutes
        self.log_message(f"Dedicated beacon interval changed to {minutes} minutes.", "beacon")
        if self.is_beacon_enabled and self.beacon_timer.isActive():
            self._stop_beacon_timer()
            self._start_beacon_timer()
        self.save_settings() 

    @Slot(str)
    def on_beacon_text_changed(self, text): 
        self.beacon_text = text

    @Slot()
    def send_automatic_beacon(self, is_initial=False): 
        if not self.is_beacon_enabled and not is_initial: 
            self.log_message("Dedicated beacon timer fired, but beacon is now disabled. Skipping.", "beacon")
            return

        is_aprs_is_selected_for_send = not self.use_tnc_for_sending
        is_tnc_selected_for_send = self.use_tnc_for_sending

        if is_aprs_is_selected_for_send and not self.aprs_manager.is_connected:
            self.log_message("Cannot send dedicated beacon via APRS-IS: Not connected.", "beacon")
            if self.is_beacon_enabled: self.is_beacon_enabled = False; self._stop_beacon_timer(); self._update_beacon_button_text()
            return
        if is_tnc_selected_for_send and not self.tnc_manager.is_tnc_connected():
            self.log_message("Cannot send dedicated beacon via TNC: Not connected.", "beacon")
            if self.is_beacon_enabled: self.is_beacon_enabled = False; self._stop_beacon_timer(); self._update_beacon_button_text()
            return
        
        if is_aprs_is_selected_for_send and self.aprs_passcode_input.text().strip() == "-1":
            self.log_message("Cannot send dedicated beacon via APRS-IS: Logged in for RX only.", "beacon")
            if self.is_beacon_enabled: self.is_beacon_enabled = False; self._stop_beacon_timer(); self._update_beacon_button_text()
            return

        beacon_comment_to_send = self.beacon_text_input.text().strip() 
        lat_str = self.aprs_latitude_input.text().strip()
        lon_str = self.aprs_longitude_input.text().strip()
        callsign_ssid = self.aprs_callsign_ssid_input.text().strip()
        if not callsign_ssid:
            self.log_message("Cannot send beacon: Callsign-SSID not set.", "error")
            return
        self.aprs_manager.callsign_ssid = callsign_ssid 


        if not beacon_comment_to_send and (not lat_str or not lon_str):
            self.log_message("Dedicated beacon not sent: Beacon text is empty and no position available.", "beacon")
            return
        
        path = "TCPIP*" if is_aprs_is_selected_for_send else "WIDE1-1,WIDE2-1" 
        
        packet_to_send = self.aprs_manager.construct_aprs_position_or_status_packet(
            beacon_comment_to_send, lat_str, lon_str, 
            path=path, 
            symbol_table=self.current_aprs_symbol_table, 
            symbol_char=self.current_aprs_symbol_char
        )
        if not packet_to_send:
            self.log_message("Failed to construct dedicated beacon packet.", "error")
            return

        self.log_message(f"Sending dedicated beacon: '{beacon_comment_to_send}' via {'APRS-IS' if is_aprs_is_selected_for_send else 'TNC'}", "beacon")
        
        success = False
        if is_aprs_is_selected_for_send:
            success = self.aprs_manager.send_aprs_packet_string_to_is(packet_to_send)
        elif is_tnc_selected_for_send:
            QMetaObject.invokeMethod(self.tnc_manager, "send_aprs_packet_via_tnc", Qt.ConnectionType.QueuedConnection, Q_ARG(str, packet_to_send))
            success = True 
            
        if success and is_aprs_is_selected_for_send: 
            self.log_message("Dedicated beacon sent successfully.", "aprs_tx")
        elif not success and is_aprs_is_selected_for_send:
            self.log_message("Failed to send dedicated beacon via APRS-IS.", "error")


    # --- Manual Status/POS Timed Beacon Methods --- 
    def _update_manual_beacon_button_text(self):
        if self.is_manual_beacon_enabled:
            self.manual_beacon_enable_button.setText(f"{ICON_STATUS_BEACON_ON} Disable Status Beacon")
            self.manual_beacon_enable_button.setStyleSheet("background-color: lightblue;")
        else:
            self.manual_beacon_enable_button.setText(f"{ICON_STATUS_BEACON_OFF} Enable Status Beacon")
            self.manual_beacon_enable_button.setStyleSheet("")

    def _start_manual_beacon_timer(self):
        if self.manual_beacon_interval_minutes > 0:
            self.manual_beacon_timer.start(self.manual_beacon_interval_minutes * 60 * 1000)
            self.log_message(f"Timed Status/POS beacon timer started. Interval: {self.manual_beacon_interval_minutes} minutes.", "beacon")

    def _stop_manual_beacon_timer(self):
        self.manual_beacon_timer.stop()
        self.log_message("Timed Status/POS beacon timer stopped.", "beacon")

    @Slot()
    def on_manual_beacon_enable_clicked(self):
        can_operate_beacon = (self.aprs_manager.is_connected and not self.use_tnc_for_sending) or \
                             (self.tnc_manager.is_tnc_connected() and self.use_tnc_for_sending)
        if not can_operate_beacon:
            QMessageBox.warning(self, "Beacon Error", "Connect to APRS-IS or TNC (and select it) before enabling the Status/POS beacon.")
            return

        self.is_manual_beacon_enabled = not self.is_manual_beacon_enabled
        self._update_manual_beacon_button_text()
        self.save_settings()

        if self.is_manual_beacon_enabled:
            self.manual_beacon_interval_minutes = self.manual_beacon_interval_spinbox.value()
            self._start_manual_beacon_timer()
            self.log_message("Timed Status/POS beacon enabled. Sending initial beacon.", "beacon")
            self.send_manual_periodic_beacon(is_initial=True)
        else:
            self._stop_manual_beacon_timer()
            self.log_message("Timed Status/POS beacon disabled.", "beacon")
        self._update_ui_state()

    @Slot(int)
    def on_manual_beacon_interval_changed(self, minutes):
        self.manual_beacon_interval_minutes = minutes
        self.log_message(f"Timed Status/POS beacon interval changed to {minutes} minutes.", "beacon")
        if self.is_manual_beacon_enabled and self.manual_beacon_timer.isActive():
            self._stop_manual_beacon_timer()
            self._start_manual_beacon_timer()
        self.save_settings()

    @Slot()
    def send_manual_periodic_beacon(self, is_initial=False):
        if not self.is_manual_beacon_enabled and not is_initial:
            self.log_message("Timed Status/POS beacon timer fired, but beacon is now disabled. Skipping.", "beacon")
            return
        
        is_aprs_is_selected_for_send = not self.use_tnc_for_sending
        is_tnc_selected_for_send = self.use_tnc_for_sending

        if is_aprs_is_selected_for_send and not self.aprs_manager.is_connected:
            self.log_message("Cannot send timed Status/POS beacon via APRS-IS: Not connected.", "beacon")
            if self.is_manual_beacon_enabled: self.is_manual_beacon_enabled = False; self._stop_manual_beacon_timer(); self._update_manual_beacon_button_text()
            return
        if is_tnc_selected_for_send and not self.tnc_manager.is_tnc_connected():
            self.log_message("Cannot send timed Status/POS beacon via TNC: Not connected.", "beacon")
            if self.is_manual_beacon_enabled: self.is_manual_beacon_enabled = False; self._stop_manual_beacon_timer(); self._update_manual_beacon_button_text()
            return
        
        if is_aprs_is_selected_for_send and self.aprs_passcode_input.text().strip() == "-1":
            self.log_message("Cannot send timed Status/POS beacon via APRS-IS: Logged in for RX only.", "beacon")
            if self.is_manual_beacon_enabled: self.is_manual_beacon_enabled = False; self._stop_manual_beacon_timer(); self._update_manual_beacon_button_text()
            return

        beacon_comment_to_send = self.aprs_status_message_input.text().strip() 
        lat_str = self.aprs_latitude_input.text().strip()
        lon_str = self.aprs_longitude_input.text().strip()
        callsign_ssid = self.aprs_callsign_ssid_input.text().strip()
        if not callsign_ssid:
            self.log_message("Cannot send beacon: Callsign-SSID not set.", "error")
            return
        self.aprs_manager.callsign_ssid = callsign_ssid

        if not beacon_comment_to_send and (not lat_str or not lon_str):
            self.log_message("Timed Status/POS beacon not sent: Status/POS comment is empty and no position available.", "beacon")
            return

        path = "TCPIP*" if is_aprs_is_selected_for_send else "WIDE1-1,WIDE2-1"
        packet_to_send = self.aprs_manager.construct_aprs_position_or_status_packet(
            beacon_comment_to_send, lat_str, lon_str,
            path=path,
            symbol_table=self.current_aprs_symbol_table,
            symbol_char=self.current_aprs_symbol_char
        )
        if not packet_to_send:
            self.log_message("Failed to construct timed Status/POS beacon packet.", "error")
            return
            
        self.log_message(f"Sending timed Status/POS beacon: '{beacon_comment_to_send}' via {'APRS-IS' if is_aprs_is_selected_for_send else 'TNC'}", "beacon")
        
        success = False
        if is_aprs_is_selected_for_send:
            success = self.aprs_manager.send_aprs_packet_string_to_is(packet_to_send)
        elif is_tnc_selected_for_send:
            QMetaObject.invokeMethod(self.tnc_manager, "send_aprs_packet_via_tnc", Qt.ConnectionType.QueuedConnection, Q_ARG(str, packet_to_send))
            success = True 
            
        if success and is_aprs_is_selected_for_send:
            self.log_message("Timed Status/POS beacon sent successfully.", "aprs_tx")
        elif not success and is_aprs_is_selected_for_send:
            self.log_message("Failed to send timed Status/POS beacon via APRS-IS.", "error")


    # --- APRS Log Display Customization Slots ---
    @Slot(int)
    def on_aprs_log_font_size_changed(self, size):
        self.current_aprs_log_font_size = size
        self._apply_aprs_log_style()
        self.save_settings()

    @Slot()
    def on_aprs_log_text_color_clicked(self):
        color = QColorDialog.getColor(QColor(self.current_aprs_log_text_color), self, "Select APRS Log Text Color")
        if color.isValid():
            self.current_aprs_log_text_color = color.name()
            self._apply_aprs_log_style()
            self.save_settings()

    @Slot()
    def on_aprs_log_bg_color_clicked(self):
        color = QColorDialog.getColor(QColor(self.current_aprs_log_bg_color), self, "Select APRS Log Background Color")
        if color.isValid():
            self.current_aprs_log_bg_color = color.name()
            self._apply_aprs_log_style()
            self.save_settings()

    def _apply_aprs_log_style(self):
        if hasattr(self, 'aprs_log_text_edit'): 
            style = (
                "QTextEdit {{"
                "  background-color: {bg_color};"
                "  color: {text_color};"
                "  font-family: 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;" 
                "  font-size: {font_size}pt;"
                "  border: 1px solid #4A4A70;" 
                "  padding: 5px;"
                "}}"
            ).format(
                bg_color=self.current_aprs_log_bg_color,
                text_color=self.current_aprs_log_text_color,
                font_size=self.current_aprs_log_font_size
            )
            self.aprs_log_text_edit.setStyleSheet(style)

    # --- APRS Station List Slots ---
    @Slot(list)
    def update_aprs_station_list_ui(self, stations_data):
        current_selection_callsign = None
        if self.aprs_station_list_widget.currentItem():
            current_selection_callsign = self.aprs_station_list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
        
        self.aprs_station_list_widget.clear()
        restored_item = None
        for station_data_dict in stations_data:
            display_string = station_data_dict.get("display_string", "Error: No display string")
            callsign = station_data_dict.get("callsign", "N/A") 
            item = QListWidgetItem(display_string)
            item.setData(Qt.ItemDataRole.UserRole, callsign) 
            self.aprs_station_list_widget.addItem(item)
            if callsign == current_selection_callsign:
                restored_item = item
        
        if restored_item:
            self.aprs_station_list_widget.setCurrentItem(restored_item)
        self.on_aprs_station_selection_changed(self.aprs_station_list_widget.currentItem(), None) 

    @Slot()
    def on_aprs_clear_station_list_clicked(self):
        self.aprs_manager.clear_heard_stations() 
        self.log_message("APRS heard station list cleared.", "aprs")

    @Slot()
    def on_aprs_track_selected_station_clicked(self):
        selected_item = self.aprs_station_list_widget.currentItem()
        if selected_item:
            callsign = selected_item.data(Qt.ItemDataRole.UserRole) 
            if callsign:
                self.aprs_map_url_input.setText(f"{DEFAULT_APRS_MAP_URL}/#!call={callsign}")
                self.load_aprs_map_url()
                for i in range(self.tab_widget.count()):
                    if self.tab_widget.widget(i).objectName() == "aprsMapTabWidget":
                        self.tab_widget.setCurrentIndex(i)
                        break
                self.log_message(f"Tracking APRS station {callsign} on map.", "aprs")
        else:
            QMessageBox.information(self, "No Station Selected", "Please select a station from the list to track.")

    @Slot(QListWidgetItem)
    def on_aprs_station_item_double_clicked_for_map(self, item): 
        if item: 
            self.on_aprs_track_selected_station_clicked()

    @Slot(QListWidgetItem)
    def on_aprs_station_item_clicked_for_details(self, item):
        if item:
            callsign = item.data(Qt.ItemDataRole.UserRole)
            if callsign and callsign in self.aprs_manager.heard_stations:
                station_data = self.aprs_manager.heard_stations[callsign]
                if self.station_detail_dialog is None or not self.station_detail_dialog.isVisible():
                    self.station_detail_dialog = StationDetailDialog(callsign, station_data, self)
                    self.station_detail_dialog.show() 
                else:
                    self.station_detail_dialog.close()
                    self.station_detail_dialog = StationDetailDialog(callsign, station_data, self)
                    self.station_detail_dialog.exec() 

            else:
                self.log_message(f"Could not find detailed data for station: {callsign}", "warning")


    @Slot(QListWidgetItem, QListWidgetItem)
    def on_aprs_station_selection_changed(self, current, previous):
        self.aprs_track_selected_station_button.setEnabled(current is not None and (self.aprs_manager.is_connected or self.tnc_manager.is_tnc_connected()))

    # --- APRS Symbol Picker Slot ---
    @Slot()
    def on_aprs_select_symbol_button_clicked(self):
        dialog = APRSSymbolPickerDialog(self.current_aprs_symbol_table, self.current_aprs_symbol_char, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_aprs_symbol_table, self.current_aprs_symbol_char = dialog.get_selected_symbol()
            self._update_current_aprs_symbol_label()
            self.save_settings()
            self.log_message(f"APRS symbol set to: {self.current_aprs_symbol_table}{self.current_aprs_symbol_char}", "info")

    def _update_current_aprs_symbol_label(self):
        if hasattr(self, 'aprs_current_symbol_label'):
            self.aprs_current_symbol_label.setText(f"Symbol: {self.current_aprs_symbol_table}{self.current_aprs_symbol_char}")


    # --- APRS-IS Slots ---
    @Slot()
    def on_aprs_connect_clicked(self): # APRS-IS Connect
        server = self.aprs_server_input.text().strip()
        port_str = self.aprs_port_input.text().strip()
        callsign_ssid = self.aprs_callsign_ssid_input.text().strip() 
        passcode = self.aprs_passcode_input.text().strip() 
        aprs_filter = self.aprs_filter_input.text().strip()

        if not server or not port_str or not callsign_ssid or passcode == "": 
            QMessageBox.warning(self, "APRS-IS Config Error", "APRS Server, Port, Callsign-SSID, and Passcode are required for APRS-IS.")
            return
        try:
            port = int(port_str)
        except ValueError:
            QMessageBox.warning(self, "APRS-IS Config Error", "APRS Port must be a valid number.")
            return
        
        self.aprs_manager.callsign_ssid = callsign_ssid 
        self.log_message(f"Attempting APRS-IS connection to {server}:{port} as {callsign_ssid}", "info")
        self.aprs_manager.connect_to_aprs_is(server, port, callsign_ssid, passcode, aprs_filter if aprs_filter else None)
        self.save_settings() 
        self._update_ui_state()

    @Slot()
    def on_aprs_disconnect_clicked(self): # APRS-IS Disconnect
        if self.is_beacon_enabled and not self.use_tnc_for_sending: 
            self.is_beacon_enabled = False
            self._stop_beacon_timer()
            self._update_beacon_button_text()
            self.log_message("Dedicated automatic beacon disabled due to APRS-IS disconnect.", "beacon")
        if self.is_manual_beacon_enabled and not self.use_tnc_for_sending:
            self.is_manual_beacon_enabled = False
            self._stop_manual_beacon_timer()
            self._update_manual_beacon_button_text()
            self.log_message("Timed Status/POS beacon disabled due to APRS-IS disconnect.", "beacon")
        self.aprs_manager.disconnect_from_aprs_is()
        self._update_ui_state()

    @Slot()
    def on_aprs_send_status_clicked(self): 
        status_text = self.aprs_status_message_input.text().strip() 
        lat_str = self.aprs_latitude_input.text().strip()
        lon_str = self.aprs_longitude_input.text().strip()
        callsign_ssid = self.aprs_callsign_ssid_input.text().strip()
        if not callsign_ssid: QMessageBox.warning(self, "APRS Error", "APRS Callsign-SSID must be set."); return


        if not status_text and (not lat_str or not lon_str) : 
            QMessageBox.warning(self, "APRS Send Error", "Please enter a status message, or both latitude and longitude for a position report.")
            return
        
        is_aprs_is_selected_for_send = not self.use_tnc_for_sending
        is_tnc_selected_for_send = self.use_tnc_for_sending

        if is_aprs_is_selected_for_send:
            if not self.aprs_manager.is_connected:
                QMessageBox.warning(self, "APRS Error", "Not connected to APRS-IS.")
                return
            if self.aprs_passcode_input.text().strip() == "-1":
                QMessageBox.warning(self, "APRS Send Error", "Cannot send data via APRS-IS when logged in for RX only (passcode -1).")
                return
        elif is_tnc_selected_for_send:
            if not self.tnc_manager.is_tnc_connected():
                QMessageBox.warning(self, "APRS Error", "TNC not connected.")
                return
        else: 
             QMessageBox.warning(self, "APRS Error", "No transmission medium selected or connected.")
             return

        path = "TCPIP*" if is_aprs_is_selected_for_send else "WIDE1-1,WIDE2-1" 
        self.aprs_manager.callsign_ssid = callsign_ssid 
        packet_to_send = self.aprs_manager.construct_aprs_position_or_status_packet(
            status_text, lat_str, lon_str, path=path,
            symbol_table=self.current_aprs_symbol_table,
            symbol_char=self.current_aprs_symbol_char
        )
        if not packet_to_send:
            self.log_message("Failed to construct manual status/pos packet.", "error")
            return

        target_medium = "APRS-IS" if is_aprs_is_selected_for_send else "TNC"
        self.log_message(f"Sending manual APRS data via {target_medium}: {packet_to_send}", "aprs_tx")

        success = False
        if is_aprs_is_selected_for_send:
            success = self.aprs_manager.send_aprs_packet_string_to_is(packet_to_send)
        elif is_tnc_selected_for_send:
            QMetaObject.invokeMethod(self.tnc_manager, "send_aprs_packet_via_tnc", Qt.ConnectionType.QueuedConnection, Q_ARG(str, packet_to_send))
            success = True 
            
        if success and is_aprs_is_selected_for_send:
            self.log_message(f"Manual APRS data sent successfully via {target_medium}.", "aprs_tx")
        elif not success and is_aprs_is_selected_for_send:
            self.log_message(f"Failed to send manual APRS data via {target_medium}.", "error")


    @Slot()
    def on_aprs_send_dm_clicked(self):
        recipient = self.aprs_dm_recipient_input.text().strip().upper()
        message = self.aprs_dm_message_input.text().strip()
        callsign_ssid = self.aprs_callsign_ssid_input.text().strip()
        if not callsign_ssid: QMessageBox.warning(self, "APRS Error", "APRS Callsign-SSID must be set."); return


        if not recipient: QMessageBox.warning(self, "APRS DM Error", "Recipient callsign cannot be empty."); return
        if not message: QMessageBox.warning(self, "APRS DM Error", "Message text cannot be empty."); return
        
        is_aprs_is_selected_for_send = not self.use_tnc_for_sending
        is_tnc_selected_for_send = self.use_tnc_for_sending

        if is_aprs_is_selected_for_send:
            if not self.aprs_manager.is_connected: QMessageBox.warning(self, "APRS Error", "Not connected to APRS-IS to send DM."); return
            if self.aprs_passcode_input.text().strip() == "-1": QMessageBox.warning(self, "APRS Send Error", "Cannot send DM via APRS-IS for RX only."); return
        elif is_tnc_selected_for_send:
            if not self.tnc_manager.is_tnc_connected(): QMessageBox.warning(self, "APRS Error", "TNC not connected to send DM."); return
        else: QMessageBox.warning(self, "APRS Error", "No transmission medium selected or connected for DM."); return

        path = "TCPIP*" if is_aprs_is_selected_for_send else "" 
        self.aprs_manager.callsign_ssid = callsign_ssid
        packet_to_send = self.aprs_manager.construct_aprs_direct_message_packet(recipient, message, path=path)
        if not packet_to_send:
            self.log_message("Failed to construct DM packet.", "error")
            return

        target_medium = "APRS-IS" if is_aprs_is_selected_for_send else "TNC"
        self.log_message(f"Sending APRS DM to {recipient} via {target_medium}: {message}", "aprs_tx")
        
        success = False
        if is_aprs_is_selected_for_send:
            success = self.aprs_manager.send_aprs_packet_string_to_is(packet_to_send)
        elif is_tnc_selected_for_send:
            QMetaObject.invokeMethod(self.tnc_manager, "send_aprs_packet_via_tnc", Qt.ConnectionType.QueuedConnection, Q_ARG(str, packet_to_send))
            success = True

        if success and is_aprs_is_selected_for_send:
            self.log_message(f"APRS DM sent successfully to {recipient} via {target_medium}.", "aprs_tx")
            self.aprs_dm_message_input.clear() 
        elif not success and is_aprs_is_selected_for_send:
            self.log_message(f"Failed to send APRS DM to {recipient} via {target_medium}.", "error")
        elif is_tnc_selected_for_send: 
             self.aprs_dm_message_input.clear()


    @Slot()
    def on_aprs_clear_log_clicked(self):
        self.aprs_log_text_edit.clear() 
        self.log_message("APRS data display cleared.", "aprs")


    @Slot()
    def on_aprs_is_connected_event(self): 
        self.log_message("Successfully connected to APRS-IS.", "aprs")
        self.statusBar().showMessage("APRS-IS Connected.", 3000)
        if self.is_beacon_enabled and not self.use_tnc_for_sending: 
            self._start_beacon_timer()
            self.log_message("Dedicated automatic beacon (re)started for APRS-IS.", "beacon")
            self.send_automatic_beacon(is_initial=True) 
        if self.is_manual_beacon_enabled and not self.use_tnc_for_sending:
            self._start_manual_beacon_timer()
            self.log_message("Timed Status/POS beacon (re)started for APRS-IS.", "beacon")
            self.send_manual_periodic_beacon(is_initial=True)
        self._update_ui_state()
        
        callsign = self.aprs_callsign_ssid_input.text().strip()
        if callsign:
            self.aprs_map_url_input.setText(f"{DEFAULT_APRS_MAP_URL}/#!call={callsign}")
            self.load_aprs_map_url()


    @Slot()
    def on_aprs_is_disconnected_event(self): 
        self.log_message("Disconnected from APRS-IS.", "aprs")
        self.statusBar().showMessage("APRS-IS Disconnected.", 3000)
        if self.beacon_timer.isActive() and not self.use_tnc_for_sending: 
            self._stop_beacon_timer()
            self.log_message("Dedicated beacon timer stopped (APRS-IS source).", "beacon")
        if self.manual_beacon_timer.isActive() and not self.use_tnc_for_sending:
            self._stop_manual_beacon_timer()
            self.log_message("Timed Status/POS beacon timer stopped (APRS-IS source).", "beacon")
        self._update_ui_state()

    @Slot(str)
    def on_aprs_packet_received_from_is(self, raw_packet): 
        self.aprs_log_text_edit.append(f"[IS] {raw_packet}") 

    @Slot(str)
    def on_aprs_status_update(self, status_message): 
        self.log_message(f"{status_message}", "aprs") 

    @Slot(str, str)
    def handle_incoming_aprs_dm(self, sender_callsign, message_text): 
        self.log_message(f"Received APRS DM from {sender_callsign}: {message_text}", "aprs_rx_dm")
        if self.aprs_dm_dialog is None:
            self.aprs_dm_dialog = DirectMessageDialog(self)

        self.aprs_dm_dialog.set_message(sender_callsign, message_text)
        if self.aprs_dm_dialog.isHidden(): 
            self.aprs_dm_dialog.show()
        self.aprs_dm_dialog.raise_() 
        self.aprs_dm_dialog.activateWindow() 


    # --- APRS Map Slots ---
    @Slot()
    def on_aprs_map_go_clicked(self):
        self.load_aprs_map_url()

    @Slot()
    def on_aprs_map_home_clicked(self):
        callsign = self.aprs_callsign_ssid_input.text().strip()
        if callsign: 
            self.aprs_map_url_input.setText(f"{DEFAULT_APRS_MAP_URL}/#!call={callsign}")
        else:
            self.aprs_map_url_input.setText(DEFAULT_APRS_MAP_URL)
        self.load_aprs_map_url()

    def load_aprs_map_url(self):
        url_text = self.aprs_map_url_input.text().strip()
        if not url_text:
            url_text = DEFAULT_APRS_MAP_URL
            self.aprs_map_url_input.setText(url_text) 

        if not url_text.startswith("http://") and not url_text.startswith("https://"):
            if len(url_text) > 3 and ('-' in url_text or url_text.isalnum()) : 
                url_to_load = QUrl(f"{DEFAULT_APRS_MAP_URL}/#!call={url_text.upper()}")
            else: 
                url_to_load = QUrl(DEFAULT_APRS_MAP_URL)
        else:
            url_to_load = QUrl(url_text)

        self.log_message(f"Loading APRS Map URL: {url_to_load.toString()}", "info")
        self.aprs_map_view.load(url_to_load)
        self.save_settings() 

    @Slot(int)
    def on_tab_changed(self, index):
        current_tab_widget = self.tab_widget.widget(index)
        if current_tab_widget and current_tab_widget.objectName() == "aprsMapTabWidget":
            if self.aprs_map_view.url().isEmpty() or self.aprs_map_view.url().toString() == "about:blank":
                self.load_aprs_map_url()


    def show_about_dialog(self):
        QMessageBox.about(self, f"About {APPLICATION_NAME} {APP_VERSION}",
                          f"<h3>{APPLICATION_NAME} {APP_VERSION}</h3>"
                          f"<p>APRS Communicator with TNC Support</p>"
                          f"<p>Organization: {ORGANIZATION_NAME}</p>")

    def closeEvent(self, event):
        self.log_message("App closing...", "info"); self.statusBar().showMessage("Closing...", 0)
        if self.beacon_timer.isActive():
            self._stop_beacon_timer() 
        if self.manual_beacon_timer.isActive():
            self._stop_manual_beacon_timer()
        
        if self.tnc_thread.isRunning():
            self.log_message("Requesting TNC manager to disconnect and thread to quit...", "tnc")
            QMetaObject.invokeMethod(self.tnc_manager, "disconnect_tnc", Qt.ConnectionType.BlockingQueuedConnection)
            self.tnc_thread.quit() 
            if not self.tnc_thread.wait(3000): 
                self.log_message("TNC thread did not finish gracefully. Forcing termination.", "warning")
                self.tnc_thread.terminate() 
                self.tnc_thread.wait() 
            else:
                self.log_message("TNC thread finished.", "tnc")
        
        self.save_settings() 
        if self.aprs_manager: self.aprs_manager.disconnect_from_aprs_is()
        if self.aprs_manager and self.aprs_manager.socket.state() != QTcpSocket.SocketState.UnconnectedState:
            self.aprs_manager.socket.waitForDisconnected(200) 
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APPLICATION_NAME) 

    splash_image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
    splash_image_path = os.path.join(splash_image_dir, "splash.png") 
    if not os.path.exists(splash_image_dir):
        try: os.makedirs(splash_image_dir)
        except OSError: pass 
    splash = None
    if os.path.exists(splash_image_path):
        splash_pixmap = QPixmap(splash_image_path)
        if not splash_pixmap.isNull():
            splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
            if splash_pixmap.hasAlphaChannel(): 
                 splash.setMask(splash_pixmap.mask())
            splash.show()
            app.processEvents() 
            time.sleep(2) 
        else:
            print(f"[UI Setup] Warning: Splash image at '{splash_image_path}' could not be loaded.")
    else:
        print(f"[UI Setup] Warning: Splash image not found at '{splash_image_path}'.")

    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
    icon_path = os.path.join(icon_dir, "aprs.png") 
    if not os.path.exists(icon_dir):
        try: os.makedirs(icon_dir)
        except OSError: pass
    if os.path.exists(icon_path): app.setWindowIcon(QIcon(icon_path))
    else: print(f"[UI Setup] Warning: App icon not found at '{icon_path}'.")

    main_window = MainWindow()
    main_window.show()

    if splash:
        splash.finish(main_window) 

    sys.exit(app.exec())
