import math
import const
from document import Document

# Variable to replace in the scad template are:
# VERSION     : The version of the software used
# DATE_TIME   : Formated as 'DD MMM YYYY HH:MM'
# SECOND_SIDE : Boolean indicating the the disc has a second side
# THICKNESS : Thickness of the disc
# NOTES
# each note is a call to the pin function which takes four parameters:
# inner (Float)
# outer (Float)
# angle degrees (Float)
# second side (Boolean)

class Expanded_document(Document):
    def __init__(self, length_x, length_y, document):
        super().__init__(length_x, length_y)
        self.title = document.title

        for i in range(document.length_y):
            beats = document.partition[i]
            if i < 7:
                self.partition[i] = beats.copy()
            elif i == 7:
                self.__split_track(7, 8, beats)
            elif i == 8:
                self.__split_track(9, 10, beats)
            elif i == 9:
                self.__split_track(11, 12, beats)
            elif i == 10:
                self.__split_track(13, 14, beats)
            elif i == 11:
                self.__split_track(15, 16, beats)
            elif i == 12:
                self.__split_track(17, 18, beats)
            elif i > 12:
                self.partition[i + 6] = beats.copy()

    def __split_track(self, first_track_number, second_track_number, beats):
        on_second_track = False
        for beat_index in range(len(beats)):
            if beats[beat_index] == True:
                track_number = second_track_number if on_second_track else first_track_number
                self.partition[track_number][beat_index] = True
                on_second_track = not on_second_track

TRACK_RADIUS = [28.65,
                29.65,
                31.39,
                32.39,
                34.21,
                35.21,
                36.925,
                37.925,
                39.725,
                40.725,
                42.5,
                43.5,
                45.325,
                46.325,
                48.055,
                49.055,
                50.815,
                51.815,
                53.61,
                54.61,
                56.4,
                57.4]
OVERLAP = 0.2
HEAD_OFFSET = 2

def __note_angle_degrees(track, note, is_second_side):
    beat_count = 86
    note_angle = 2 * math.pi / beat_count

    radius = TRACK_RADIUS[track]
    angle = note_angle * note
    angle -= (HEAD_OFFSET / radius)
    angle = angle * 180 / math.pi

    if is_second_side:
        angle = 360 - angle

    return angle

def get_pins(e_document, is_second_side):
    pins = []
    is_second_side_str = '1' if is_second_side else '0'
    for track_index in range(e_document.length_y):
        inner = TRACK_RADIUS[track_index] - 0.5 - (OVERLAP if track_index %2 == 0 else 0)
        outer = inner + 1 + OVERLAP
        for note_index in range(e_document.length_x):
            if e_document.has_note(note_index, track_index):
                angle = __note_angle_degrees(track_index, note_index, is_second_side)
                pins.append([inner, outer, angle, is_second_side_str])
    return pins

def pins_to_str(pins, title=None, is_second_side=None):
    pin_str = ''
    indent = '\t'*2
    for pin in pins:
        pin_str += indent+'pin({},{},{},{});\n'.format(pin[0], pin[1], pin[2], pin[3])
    if title is not None:
        second_side_str = '1' if is_second_side else '0'
        pin_str += '\n'+indent+'title("{}",{});\n\n'.format(title, second_side_str)
    return pin_str

def to_scad(version, date_time, thickness, document, document_bis=None):
    with open('res/FisherPriceTemplate.scad', 'r') as content_file:
        content = content_file.read()
        content = content.replace('{VERSION}', version)
        content = content.replace('{DATE_TIME}', date_time)
        content = content.replace('{THICKNESS}', str(thickness))
        content = content.replace('{SECOND_SIDE}', '0' if document_bis is None else '1')

        e_document = Expanded_document(86, 22, document)
        pins = get_pins(e_document, False)

        pin_str = pins_to_str(pins, e_document.title, False)

        if document_bis is not None:
            e_document_bis = Expanded_document(86, 22, document)
            pins_bis = get_pins(e_document_bis, True)
            pin_str += pins_to_str(pins_bis, e_document_bis.title, True)

        content = content.replace('{NOTES}', pin_str)

        return content
