import Keyboard
import HIDInput
from multiprocessing import Process

BTYE_INDEX_RED_DRUM = 43
BTYE_INDEX_YELLOW_DRUM = 45
BTYE_INDEX_BLUE_DRUM = 44
BTYE_INDEX_GREEN_DRUM = 46

BTYE_INDEX_GREEN_CYMBAL = 49
BTYE_INDEX_BLUE_CYMBAL = 48
BTYE_INDEX_YELLOW_CYMBAL = 47

BTYE_INDEX_RIGHT_PADDLE = 6

mapping = [ 
    [ BTYE_INDEX_GREEN_CYMBAL, Keyboard.VK_X ],
    [ BTYE_INDEX_BLUE_CYMBAL, Keyboard.VK_A ],
    [ BTYE_INDEX_YELLOW_CYMBAL, Keyboard.VK_J ],
    [ BTYE_INDEX_RED_DRUM, Keyboard.VK_C ],
    [ BTYE_INDEX_YELLOW_DRUM, Keyboard.VK_F],
    [ BTYE_INDEX_BLUE_DRUM, Keyboard.VK_B],
    [ BTYE_INDEX_GREEN_DRUM, Keyboard.VK_N ],
    [ BTYE_INDEX_RIGHT_PADDLE, Keyboard.VK_SPACE ]
    ]

isHit = [ False ] * len(mapping)

def PressKey(keycode):
    
    Keyboard.PressKeyOnce(keycode)

    # Suppose to fork a process to avoid waiting when calling time.sleep()
    # However we might need process pool to decrease the latency that
    # a process instantiate and executes
    # For now, direct call Keyboard.PressKeyOnce() provides lower latency

    # p = Process(target=Keyboard.PressKeyOnce, args=(keycode,))
    # p.start()
    

def sample_handler(data):

    global isHit, mapping

    # print('Raw data: ', end=', ')
    # for d in data:
    #     print(format(d, 'x').zfill(2), end=', ')
    # print()

    for index in range(0, len(mapping)):

        byte_offset = mapping[index][0]
        keycode = mapping[index][1]

        if byte_offset > len(data):
            print(f"list index out of range({len(data)}): {byte_offset}")
            pass

        detection = data[byte_offset]

        if detection > 0 and isHit[index] == False:
            PressKey(keycode)
            isHit[index] = True
        
        elif detection == 0:
            isHit[index] = False

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