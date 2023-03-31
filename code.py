# Badge of Authenticity
# Coded by Donovan except where noted for Adafruit fonts and libraries.
# A prototype design for UVic CSc 485E
# Base design was done for Adafruit ESP-32 TFT using CircuitPython and Adafruit libraries
# Except the CircuitPython libraries in the import and lib folders, which were from Adarfuit and released under MIT license

# Imports
import time
import board
from displayio import OnDiskBitmap, TileGrid, Group
import board
import digitalio
import touchio
import busio
import terminalio
from adafruit_display_text import label
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
from adafruit_pn532.i2c import PN532_I2C


######################
# Global Variables

# Default image and details for slideshow here.
checkpoints = [["GerbilCON 2023", "GerbilCON.bmp", "Art by TofuPixel"]]

# Fake loading details from RFID match taken from local drive_mode.
# This needs to be expanded functionally in future work.
cardInputs  = { '8524115710': ["Prod IG", "Kusanagi.bmp", "wW3oM0dQ2fW4kN7t"],
                '1958495150': ["First Comics", "Shatter.bmp", "tX1tU6rK6cX3qL5p"],
                '18824211750': ["TofuPixel", "ramen.bmp", "xC3sB0kQ5aX3tD7gY7"]
                }

speed       = 2

######################
# Setup

# fonts 
font_file = "fonts/LeagueSpartan-Bold-16.bdf"
font      = bitmap_font.load_font(font_file)

# touch capacity
touchPins       = [
                    touchio.TouchIn(board.D8),
                    touchio.TouchIn(board.D14),
                    touchio.TouchIn(board.D10),
                    touchio.TouchIn(board.D9),
                    touchio.TouchIn(board.D1),
                    touchio.TouchIn(board.D2)
                ]
for touchPin in touchPins:
    touchPin.threshold = 10000

# RFID reader
i2c = busio.I2C(board.SCL, board.SDA)
reset_pin             = digitalio.DigitalInOut(board.D5)
req_pin               = digitalio.DigitalInOut(board.D6)
pn532                 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)
ic, ver, rev, support = pn532.firmware_version
lastUID               = 0x00000000
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()


   
def showImage(imgName):
    main_group = Group()
    show_img = OnDiskBitmap("images/" + imgName)
    show_img = OnDiskBitmap("images/" + imgName)
    tile_grid = TileGrid(bitmap=show_img, pixel_shader=show_img.pixel_shader)
    main_group.append(tile_grid)
    board.DISPLAY.show(main_group)
    tile_grid.x = board.DISPLAY.width // 2 - show_img.width // 2

def showText(text1, colour1, text2="", colour2="0x000000"):
    main_group = Group()
    # Top text
    scale = 2
    text_area = label.Label(font, text=text1, scale=scale, color=colour1)
    text_area.x = 10
    text_area.y = 40
    main_group.append(text_area)
    # Bottom text
    scale = 1
    text_area2 = label.Label(font, text=text2, scale=scale, color=colour2)
    text_area2.x = 90
    text_area2.y = 80
    main_group.append(text_area2)
    board.DISPLAY.show(main_group)

def checkReaders(seconds):
    for wait in range(seconds * 4):
        RFIDreader()
        touchReader()
        time.sleep(.25)

# Values are hardcoded here for prototype use and should be expanded in future work to be dynamic.
# Should also show the valid pass number IDS as well.
def showID():
    global speed
    showText("GerbilCON", 0xFF0000, "2023", 0x0000FF)
    checkReaders(speed)
    showText("Donovan", 0xFF4444, "He/Him", 0x22ff22)
    checkReaders(speed)

def slideshow():
    global checkpoints, speed
    showID()
    for item in checkpoints:
        showImage(item[1])
        checkReaders(speed)

def showTokens():
    main_group = Group()
    global checkpoints
    text = ""
    
    for token in checkpoints:
        text += token[0] + ": " + token[2] + "\n"
    scale = 1
    text_area = bitmap_label.Label(terminalio.FONT, text=text, scale=scale, color=0xFFFFFF)
#    text_area = label.Label(terminalio.font, text=text, scale=scale, color=0xFFFFFF)
    text_area.x = 0
    text_area.y = 10
    main_group.append(text_area)
    board.DISPLAY.show(main_group)
    for pin in touchPins:
        if pin.value:
            time.sleep(1)

def touchReader():
    for pin in touchPins:
        if pin.value:
            showTokens()
    return
    
def RFIDreader():
    global lastUID, checkpoints, cardInputs, speed
    uid = pn532.read_passive_target(timeout=0.5)

    # Return if nothing new
    if (uid is None) or (uid == lastUID):
        return 
    
    # Do things if new
    UIDstr = ''.join(str(i) for i in uid)
    print(UIDstr)
    lastUID = uid
    
    if UIDstr in cardInputs:
        checkpoints.append(cardInputs[UIDstr])
        showText(checkpoints[-1][0], 0xFFFFFF, "ADDED", 0x22FF22)
        time.sleep(speed)
        showImage(checkpoints[-1][1])
        time.sleep(speed)

    else:
        showText("NOT", 0xFF0000, "RECOGNIZED", 0xFF00FF)
        time.sleep(speed)

    
def main():
    while True:
        slideshow()
    
if __name__ == "__main__":
    main()

