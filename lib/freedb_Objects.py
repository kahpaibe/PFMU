""" Declares the classes for objects related to pyfreedbutil. """

from numpy import uint32  # unsigned 32-bit integer

from . import discid_lib


# general purpose functions
def format_number_length(number: int, length: int, allow_overflow: bool = True) -> str:
    """Format a number and append 0s to get the given length.

    Args:
        number (int): The number to format.
        length (int): The length of the formatted number.
        allow_overflow (bool): Whether to allow numbers larger than the length."""

    if length <= 0:
        raise ValueError("Length must be more than 1")
    if not allow_overflow and number >= 10 ** (length):
        raise ValueError(f"Number {number} is too large for the length {length}")
    n = str(number)
    s = "0" * (length - len(n)) + n
    return s


def format_track_length(length_seconds: int) -> str:
    """Format a track length in seconds to a string in the format "hh:mm:ss or mm:ss.

    Args:
        length_seconds (int): The length of the track in seconds."""
    hc = length_seconds // 3600
    mc = (length_seconds % 3600) // 60
    sc = length_seconds % 60

    if hc != 0:
        return f"{hc}:{format_number_length(mc,2)}:{format_number_length(sc,2)}"
    else:
        return f"{format_number_length(mc,2)}:{format_number_length(sc,2)}"


class AudioTrack:
    """An audio track."""

    # Fields
    frame_count: int = 0
    artist: str = ""
    title: str = ""

    # init
    def __init__(self, frame_count: int = 0, artist: str = "", title: str = "") -> None:
        self.frame_count = frame_count
        self.artist = artist
        self.title = title

    # Methods
    def __str__(self) -> str:
        s = ""
        if len(self.artist) > 0:
            s += self.artist
        if len(self.title) > 0:
            if s != "":
                s += " - "
            s += self.title
        if self.frame_count >= 0:
            if s != "":
                s += " - "
            track_length = self.frame_count * 75  # convert to seconds
            s += format_track_length(track_length)

        return s


class AudioTrackGroup:
    """Collection of several tracks"""

    # Fields
    tracks: list[AudioTrack] = []

    # init
    def __init__(self, tracks: list[AudioTrack] = []) -> None:
        self.tracks = tracks  # may be constructed from a list of tracks

    # Methods
    def __str__(self) -> str:
        if not self.tracks:
            return "Empty AudioTrackGroup"

        s = ""
        for track_id in range(len(self.tracks)):
            track_number = track_id + 1
            s += f"{format_number_length(track_number,2)}: {self.tracks[track_id]}\n"

        return s

    def get_offsets_plus(self, lead_in: int = 150) -> list[int]:
        """Get the offsets of the tracks, including the lead_out.

        Args:
            lead_in (int, optional): The lead-in of the CD, in frames. Defaults to 150 frames.
        """
        if not self.tracks:
            raise ValueError("The AudioTrackGroup has no tracks.")
        else:
            current_offset = lead_in
            offsets = [current_offset]
            for i in range(0, len(self.tracks)):
                current_offset += self.tracks[i].frame_count
                offsets.append(current_offset)
            return offsets


class AudioAlbum(AudioTrackGroup):
    """An audio album, which is a collection of tracks with a title and an artist."""

    # Fields
    tracks: list[AudioTrack] = []
    title: str = ""
    artist: str = ""

    def __init__(
        self,
        tracks: list[AudioTrack] = [],
        audio_track_group: AudioTrackGroup = AudioTrackGroup(),
        title: str = "",
        artists: str = "",
        year: str = "",
        genre: str = "",
    ) -> None:
        """Initialize the AudioAlbum. Construct from a list of tracks or from an AudioTrackGroup.

        Args:
            tracks (list[AudioTrack]): The tracks of the album. -> To construct from a list of tracks.
            audio_track_group (AudioTrackGroup): The tracks of the album. -> To construct from an AudioTrackGroup.
            title (str): The title of the album.
            artists (str): The artist of the album.
            year (str): The year of the album.
            genre (str): The genre of the album."""
        if tracks:
            super().__init__(tracks=tracks)  # construct form tracks
        else:
            super().__init__(audio_track_group.tracks)  # construct form AudioTrackGroup
        self.title = title
        self.artist = artists
        self.year = year
        self.genre = genre

    # Methods
    def __str__(self) -> str:

        if self.artist:
            s = f"{self.artist} - {self.title}\n"
        else:
            s = f"*{self.title}\n"

        if not self.tracks:
            return f"{s}  Empty AudioCD"

        for track_id in range(len(self.tracks)):
            track_number = track_id + 1
            s += f"{format_number_length(track_number,2)}: {self.tracks[track_id]}\n"

        return s

    def get_disc_id(self) -> uint32:
        """Calculates the disc id for the album, which is used to query the freedb server. Decimal representation of the disc id is returned."""
        if not self.tracks:
            raise ValueError("The album has no tracks.")
        else:
            current_frame = 150
            track_frame_indexes_plus = [2 * discid_lib.FRAME_RATE]  # lead-in
            for i in range(len(self.tracks)):
                current_frame += self.tracks[i].frame_count
                track_frame_indexes_plus.append(current_frame)

            return discid_lib.calculate_disc_id(track_frame_indexes_plus)

    def get_hex_disc_id(self, do_show_0x: bool = False) -> str:
        """Calculates the disc id for the album, which is used to query the freedb server. Hexadecimal representation of the disc id is returned."""

        if do_show_0x:
            return f"0x{format(self.get_disc_id(), 'x')}"
        else:
            return format(self.get_disc_id(), "x")


# # test
# track_1 = AudioTrack(21814 - 150)
# track_2 = AudioTrack(43219 - 21814)

# album = AudioAlbum([track_1, track_2], title="Test Album", artists="Test Artist")
# print((album.get_offsets_plus()))
