import math
from record import Record

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

TRACK_RADIUS = [
    28.65,
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
    57.4,
]


class PhysicalRecord(Record):
    def __init__(self, beats_count, record):
        super().__init__(beats_count)
        self.title = record.title
        self._partition = [
            [False for x in range(beats_count)] for y in range(Record.TRACKS_COUNT)
        ]
        for track_index in range(Record.TONES_COUNT):
            track = record.get_track(track_index)
            if track_index < 7:
                self._partition[track_index] = track.copy()
            elif track_index == 7:
                self.__split_track(7, 8, track)
            elif track_index == 8:
                self.__split_track(9, 10, track)
            elif track_index == 9:
                self.__split_track(11, 12, track)
            elif track_index == 10:
                self.__split_track(13, 14, track)
            elif track_index == 11:
                self.__split_track(15, 16, track)
            elif track_index == 12:
                self.__split_track(17, 18, track)
            elif track_index > 12:
                self._partition[track_index + 6] = track.copy()

    def __split_track(self, first_track_number, second_track_number, beats):
        on_second_track = False
        for beat_index in range(len(beats)):
            if beats[beat_index] == True:
                track_number = (
                    second_track_number if on_second_track else first_track_number
                )
                self.set_note(beat_index, track_number, True)
                on_second_track = not on_second_track


class Pin:
    def __init__(self, inner, outer, is_second_side, beat_count):
        self.__inner = inner
        self.__outer = outer
        self.__is_second_side = is_second_side
        self.__beat_count = beat_count
        self.__angle = None

    def set_angle(self, track, note):
        HEAD_OFFSET = 2
        note_angle = 2 * math.pi / self.__beat_count

        radius = TRACK_RADIUS[track]
        angle = note_angle * note
        angle -= HEAD_OFFSET / radius
        angle = angle * 180 / math.pi

        if self.__is_second_side:
            angle = 360 - angle

        self.__angle = angle

    def to_str(self):
        is_second_side_str = "1" if self.__is_second_side else "0"
        return "pin({},{},{},{});".format(
            self.__inner, self.__outer, self.__angle, is_second_side_str
        )


def pins_to_str(pins, indent):
    pin_str = ""
    for pin in pins:
        pin_str += indent + pin.to_str() + "\n"
    return pin_str


def get_pins(physical_record, is_second_side):
    pins = []
    OVERLAP = 0.2

    for track_index in range(Record.TRACKS_COUNT):
        inner = (
            TRACK_RADIUS[track_index] - 0.5 - (OVERLAP if track_index % 2 == 0 else 0)
        )
        outer = inner + 1 + OVERLAP
        for note_index in range(physical_record.beats_count):
            if physical_record.has_note(note_index, track_index):
                pin = Pin(inner, outer, is_second_side, physical_record.beats_count)
                pin.set_angle(track_index, note_index)
                pins.append(pin)
    return pins


def to_scad(version, date_time, thickness, record, record_bis=None):
    with open("res/fisher-price-template.scad", "r") as content_file:
        content = content_file.read()
        content = content.replace("{VERSION}", version)
        content = content.replace("{DATE_TIME}", date_time)
        content = content.replace("{THICKNESS}", str(thickness))
        content = content.replace("{SECOND_SIDE}", "0" if record_bis is None else "1")

        indent = "\t" * 2
        physical_record = PhysicalRecord(Record.MAX_BEAT, record)
        pins = get_pins(physical_record, False)
        pin_str = pins_to_str(pins, indent)

        if physical_record.title is not None:
            pin_str += (
                "\n" + indent + 'title("{}",{});\n\n'.format(physical_record.title, "0")
            )

        if record_bis is not None:
            physical_record_bis = PhysicalRecord(Record.MAX_BEAT, record_bis)
            pins_bis = get_pins(physical_record_bis, True)
            pin_str += pins_to_str(pins_bis, indent)

            if physical_record_bis.title is not None:
                pin_str += (
                    "\n"
                    + indent
                    + 'title("{}",{});\n\n'.format(physical_record_bis.title, "1")
                )

        content = content.replace("{NOTES}", pin_str)

        return content
