import Keyboard
import HIDInput

BTYE_INDEX_RED_DRUM = 43
BTYE_INDEX_YELLOW_DRUM = 45
BTYE_INDEX_BLUE_DRUM = 44
BTYE_INDEX_GREEN_DRUM = 46

BTYE_INDEX_GREEN_CYMBAL = 49
BTYE_INDEX_BLUE_CYMBAL = 48
BTYE_INDEX_YELLOW_CYMBAL = 47

BTYE_INDEX_ANALOG = 6
BTYE_INDEX_DPAD = 5

BTYE_VALUE_RED_DRUM = 11
BTYE_VALUE_YELLOW_DRUM = 115
BTYE_VALUE_BLUE_DRUM = 91
BTYE_VALUE_GREEN_DRUM = 195

BTYE_VALUE_GREEN_CYMBAL = 119
BTYE_VALUE_BLUE_CYMBAL = 62
BTYE_VALUE_YELLOW_CYMBAL = 129

BTYE_VALUE_SHARE = 16
BTYE_VALUE_OPTIONS = 32
BTYE_VALUE_RIGHT_PADDLE = 1

BTYE_VALUE_TRIANGLE = 136
BTYE_VALUE_CIRCLE = 72
BTYE_VALUE_CROSS = 40
BTYE_VALUE_SQUARE = 24

mapping = {
    BTYE_INDEX_GREEN_CYMBAL : Keyboard.VK_X,
    BTYE_INDEX_BLUE_CYMBAL  : Keyboard.VK_A,
    BTYE_INDEX_YELLOW_CYMBAL: Keyboard.VK_J,
    BTYE_INDEX_RED_DRUM     : Keyboard.VK_C,
    
    # wierd bug: pressing VK_Volume_Down also trigger high tom, however we assume it is acceptable
    BTYE_INDEX_YELLOW_DRUM  : Keyboard.VK_F,
    
    # wierd bug: pressing VK_Volume_Up also trigger middle tom, however we assume it is acceptable
    BTYE_INDEX_BLUE_DRUM    : Keyboard.VK_G,

    BTYE_INDEX_GREEN_DRUM   : Keyboard.VK_N,
    
    # Bass Drum, Option, Share
    BTYE_INDEX_ANALOG       : None,

    # Special logic needed to find out whether it is d-pad or pad/cymbal
    BTYE_INDEX_DPAD         : None
}

analog_mapping = {
    
    BTYE_VALUE_OPTIONS:       Keyboard.VK_Volume_Up,    
    BTYE_VALUE_SHARE:         Keyboard.VK_Volume_Down,
    BTYE_VALUE_RIGHT_PADDLE:  Keyboard.VK_SPACE,

    BTYE_VALUE_TRIANGLE:      Keyboard.VK_ONE,          # Self define system key
    BTYE_VALUE_CIRCLE:        Keyboard.VK_TWO,          # Self define system key
    BTYE_VALUE_CROSS:         Keyboard.VK_ESCAPE,
    BTYE_VALUE_SQUARE:        Keyboard.VK_BACK
}

mapping_keys_list = list(mapping)
mapping_isHit_list = [ 0 ] * len(mapping)

analog_mapping_keys_list = list(analog_mapping)
analog_mapping_isHit = 0

dPadCheckList = [  BTYE_INDEX_GREEN_CYMBAL, BTYE_INDEX_BLUE_CYMBAL, BTYE_INDEX_YELLOW_CYMBAL, BTYE_INDEX_RED_DRUM, BTYE_INDEX_YELLOW_DRUM, BTYE_INDEX_BLUE_DRUM, BTYE_INDEX_GREEN_DRUM]

def PressKey(keycode):
    Keyboard.PressKeyOnce(keycode)

def sample_handler(data):

    global isHit, mapping

    # print('Raw data: ', end=', ')
    # for d in data:
    #     print(format(d, 'x').zfill(2), end=', ')
    # print()

    # print(mapping_keys_list)
    # print(mapping_isHit_list)

    for index, byte_offset in enumerate(mapping):

        keycode = mapping[byte_offset]

        if byte_offset > len(data):
            print(f"list index out of range({len(data)}): {byte_offset}")
            return

        detection = data[byte_offset]

        if byte_offset == BTYE_INDEX_ANALOG or byte_offset == BTYE_INDEX_DPAD:
            
            # In case: (byte_offset == BTYE_INDEX_DPAD)
            # We cannot simply determine currently it is trigger by durm pad or d-pad
            # 
            # data from drum pad:
            # 01, 80, 80, 80, 80, 88, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 0c, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 26, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 3e, 80, f6, ee, 
            #
            # data from pressing d-pad:
            # 01, 80, 80, 80, 80, 88, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 0c, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, ec, 4c, 77, a9, 
            #
            # So in order to determine which is it, we only treat is as dpad if the volumes of every pad/cymbal is all zero.
            # It may be not triggered when user hits the drum pad and press the d-pad at the same time. However we think it is acceptable.
            if byte_offset == BTYE_INDEX_DPAD and detection in analog_mapping:
                summedVal = sum( [ data[i] for i in dPadCheckList ])
                if summedVal > 0:
                    continue

            if mapping_isHit_list[index] != detection and detection in analog_mapping:
                keycode = analog_mapping[detection]
                PressKey(keycode)
            
            mapping_isHit_list[index] = detection
    
        elif detection > 0 and mapping_isHit_list[index] != detection:
            PressKey(keycode)
            mapping_isHit_list[index] = detection
        
        elif detection == 0:
            mapping_isHit_list[index] = detection
    

if __name__ == '__main__':
    # first be kind with local encodings
    import sys
    if sys.version_info >= (3,):
        # as is, don't handle unicodes
        unicode = str
        raw_input = input
    else:
        # allow to show encoded strings
        import codecs
        sys.stdout = codecs.getwriter('mbcs')(sys.stdout)
    
    device = HIDInput.Choose_HID_Device()

    if device:
        # Loop to capture device input
        HIDInput.Device_Loop(device, sample_handler)