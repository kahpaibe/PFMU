""" Tools to query freedb servers. """

import re
from typing import Any, Literal, Union

from . import freedblib_info
from .freedb_Objects import AudioAlbum, AudioTrack, AudioTrackGroup


def int_to_hex(i: int, do_show_0x: bool = False) -> str:
    """Converts an integer to a hexadecimal string.

    Args:
        i (int): The integer to convert.
        do_show_0x (bool, optional): If True, the string will start with '0x'. Defaults to False.

    Returns:
        str: The hexadecimal string."""
    if do_show_0x:
        return f"0x{format(i, 'x')}"
    else:
        return format(i, "x")


class Freedb_Query:
    """A query to send to a freedb server."""

    # goal: http://gnudb.gnudb.org/~cddb/cddb.cgi?cmd=cddb+query+0D023E02+2+150+21815+576&hello=emailname+emailhost.com+applicationname+0.1&proto=5

    disc_type = 1  # always 1
    user = ""
    user_email = ""
    host = ""
    app = ""
    version = ""
    protocol = "5"

    def __init__(
        self,
        album: AudioAlbum,
        query_type: Union[Literal["query"], Literal["read"]] = "query",
        category: freedblib_info.FREEDB_CATEGORIES_TYPES = "rock",
        user: str = freedblib_info.DEFAULT_USER,
        user_email: str = freedblib_info.DEFAULT_USER_EMAIL,
        host: str = freedblib_info.DEFAULT_HOST,
        app: str = freedblib_info.DEFAULT_APP,
        version: str = freedblib_info.DEFAULT_VERSION,
        protocol: str = freedblib_info.DEFAULT_PROTOCOL,
    ) -> None:
        """Initialize the query.

        Args:
            album (AudioAlbum): The album to query for.
            category (freedblib_info.FREEDB_CATEGORIES_TYPES, optional, for "read" query type only): The category of the album. Defaults to "rock".
            user (str, optional): The user name. Defaults to DEFAULT_USER.
            user_email (str, optional): The user email. Defaults to DEFAULT_USER_EMAIL.
            host (str, optional): The host. Defaults to DEFAULT_HOST.
            app (str, optional): The app name. Defaults to DEFAULT_APP.
            version (str, optional): The app version. Defaults to DEFAULT_VERSION.
            protocol (int, optional): The protocol version. Defaults to DEFAULT_PROTOCOL.
            query_type (str, Literal["query"] or Literal["read"]). Query type. Defaults to "query".
        """
        self.album = album
        self.user = user
        self.user_email = user_email
        self.host = host
        self.app = app
        self.version = version
        self.protocol = protocol
        self.query_type = query_type
        self.category = category

    def get_query_string(self, url: str) -> str:
        """Generates the query string to send to the server.

        Args:
            url (str): The url of the server.
        """
        # get the disc id
        disc_id = int_to_hex(int(self.album.get_disc_id()), False)

        # get the track count
        track_count = len(self.album.tracks)

        # get the track offsets
        track_offsets = self.album.get_offsets_plus()

        # get album length in seconds
        album_length = track_offsets[-1] // 75

        if self.query_type == "query":
            # for queries
            query_str = f"{url}?cmd=cddb+query+{disc_id}+{track_count}"
            for i in range(len(track_offsets) - 1):
                query_str += f"+{track_offsets[i]}"
            query_str += f"+{album_length}&hello={self.user}+{self.user_email}+{self.app}+{self.version}&proto={self.protocol}"
            return query_str
        elif self.query_type == "read":
            # for reads
            # http://gnudb.gnudb.org/~cddb/cddb.cgi?cmd=cddb+read+rock+12345678&hello=joe+my.host.com+xmcd+2.1&proto=3
            query_str = f"{url}?cmd=cddb+read+{self.category}+{disc_id}"
            query_str += f"&hello={self.user}+{self.host}+{self.app}+{self.version}&proto={self.protocol}"

            return query_str
        else:
            raise ValueError("Invalid query type. Should not happend !")


class Freedb_Query_Generator:
    """Quickly generates a Freedb_Query by saving user informations."""

    disc_type = 1  # always 1
    user = ""
    user_email = ""
    host = ""
    app = ""
    version = ""
    protocol = "5"

    def __init__(
        self,
        query_type: Union[Literal["query"], Literal["read"]] = "query",
        category: freedblib_info.FREEDB_CATEGORIES_TYPES = "rock",
        user: str = freedblib_info.DEFAULT_USER,
        user_email: str = freedblib_info.DEFAULT_USER_EMAIL,
        host: str = freedblib_info.DEFAULT_HOST,
        app: str = freedblib_info.DEFAULT_APP,
        version: str = freedblib_info.DEFAULT_VERSION,
        protocol: str = freedblib_info.DEFAULT_PROTOCOL,
    ) -> None:
        """Initialize the query generator.

        Args: Like a query, without the album
            user (str, optional): The user name. Defaults to DEFAULT_USER.
            user_email (str, optional): The user email. Defaults to DEFAULT_USER_EMAIL.
            host (str, optional): The host. Defaults to DEFAULT_HOST.
            app (str, optional): The app name. Defaults to DEFAULT_APP.
            version (str, optional): The app version. Defaults to DEFAULT_VERSION.
            protocol (str, optional): The protocol version. Defaults to DEFAULT_PROTOCOL.
        """
        self.user = user
        self.user_email = user_email
        self.host = host
        self.app = app
        self.version = version
        self.protocol = protocol
        self.query_type: Literal["query"] | Literal["read"] = query_type
        self.category: freedblib_info.FREEDB_CATEGORIES_TYPES = category

    def generate_query(self, album: AudioAlbum) -> Freedb_Query:
        """Generates a Freedb_Query with the given album.

        Args:
            album (AudioAlbum): The album to query for.

        Returns:
            Freedb_Query: The generated query."""
        return Freedb_Query(
            album,
            query_type=self.query_type,
            category=self.category,
            user=self.user,
            user_email=self.user_email,
            host=self.host,
            app=self.app,
            version=self.version,
            protocol=self.protocol,
        )


class Freedb_Query_Query_Reader:
    """A class to read the result of a "query"-type query."""

    re_quadruplets = re.compile(
        r"("
        + freedblib_info.FREEDB_CATEGORIES_REGEX_PREGROUP
        + r") ([0-9a-fA-F]{8}) ([^\/]+?) / ([^\/]+)$"
    )

    def __init__(self) -> None:
        """"""
        pass

    def get_header_error_code(self, query_result: list[bytes]) -> tuple[str, str]:
        """Parses the query result to get the header and error code.

        Args:
            query_result (list[bytes]): The result of the query, such as result.readlines().

        Returns:
            str: The error code.
        """
        # get the header and error code
        header = query_result[0].decode("utf-8")
        error_code = header.split(" ")[0]
        return header, error_code

    def get_query_quadruplets(
        self, query_result: list[bytes]
    ) -> tuple[str, list[tuple[str, str, str, str]]] | list[None]:
        """Parses the query result to get the query triplets.

        Args:
            query_result (list[bytes]): The result of the query, such as result.readlines().

        Returns:
            tuple[str,list[tuple[str, str, str]]]
                str, return code
                tuple[str,str,str,str], the quadruplets triplets. Empty if none.

            A quadruplets is a list of 4 strings: [category, disc_id, artist, album_name]
        """
        # get the header and error code
        header, error_code = self.get_header_error_code(query_result)

        # get release quadruplets
        quadruplets: list[tuple[str, str, str, str]] = []
        for i in range(1, len(query_result) - 1):
            line = query_result[i].decode("utf-8").replace("\r", "").replace("\n", "")

            match = self.re_quadruplets.match(line)
            if match:
                category: str = match.group(1)
                discid: str = match.group(2)
                artist: str = match.group(3)
                album: str = match.group(4)
                quadruplets.append((category, discid, artist, album))

        return error_code, quadruplets


class Freedb_Query_Read_Reader:
    """A class to read the result of a "read"-type query."""

    re_releases = re.compile(r"")
    re_DISCID = re.compile(r"^DISCID=(?P<DiscId>.*)")
    re_DTITLE = re.compile(r"^DTITLE=(?P<DiscTitle>.*)")
    re_DYEAR = re.compile(r"^DYEAR=(?P<DiscYear>.*)")
    re_DGENRE = re.compile(r"^DGENRE=(?P<DiscGenre>.*)")
    re_TTITLE = re.compile(r"^TTITLE(?P<TrackNum>[^=]*)=(?P<TrackTitle>.*)")

    re_INLINE_TRACK_ARTIST = re.compile(r"^(?P<TrackArtist>.*) / (?P<TrackTitle>.*)$")

    def __init__(self) -> None:
        """"""
        pass

    def get_header_error_code(self, query_result: list[bytes]) -> tuple[str, str]:
        """Parses the query result to get the header and error code.

        Args:
            query_result (list[bytes]): The result of the query, such as result.readlines().

        Returns:
            str: The error code.
        """
        # get the header and error code
        header = query_result[0].decode("utf-8")
        error_code = header.split(" ")[0]
        return header, error_code

    def get_read_releases(
        self, query_result: list[bytes], encoding="utf-8"
    ) -> tuple[str, AudioAlbum]:
        """Parses the "read"-query result to get releases metadata.

        Args:
            query_result (list[bytes]): The result of the query, such as result.readlines().
            encoding (str, optional): The encoding of the query result. Defaults to "utf-8".

        Returns:
            tuple[str, AudioAlbum]
                str, return code
                AudioAlbum, the album metadata. Empty if none.
        """
        # get the header and error code
        header, error_code = self.get_header_error_code(query_result)

        # parse lines, get releases metadata

        # release_index = ( # unused: for now, I havent found a read with mutliple releases, may not exist
        #     -1
        # )  # goes up by 1 for each release, the first release is at index 0

        release: dict[str, str] = {
            "DISCID": "",
            "DTITLE": "",
            "DYEAR": "",
            "DGENRE": "",
        }
        tracklist: list[tuple[str, str]] = []  # (track_artist, track_title), "" if none
        for i in range(1, len(query_result) - 1):
            line = query_result[i].decode(encoding).replace("\r", "").replace("\n", "")

            match = self.re_DISCID.match(line)
            if match:
                disc_id: str = match.group("DiscId")
                release["DISCID"] = disc_id

            match = self.re_DTITLE.match(line)
            if match:
                disc_title: str = match.group("DiscTitle")
                release["DTITLE"] = disc_title

            match = self.re_DYEAR.match(line)
            if match:
                disc_year: str = match.group("DiscYear")
                release["DYEAR"] = disc_year

            match = self.re_DGENRE.match(line)
            if match:
                disc_genre: str = match.group("DiscGenre")
                release["DGENRE"] = disc_genre

            match = self.re_TTITLE.match(line)
            if match:
                track_num: str = match.group("TrackNum")
                track_title: str = match.group("TrackTitle")

                # test if inline track artist
                inline_match = self.re_INLINE_TRACK_ARTIST.match(track_title)
                if inline_match:  # if artist found
                    track_artist: str = inline_match.group("TrackArtist")
                    track_title: str = inline_match.group("TrackTitle")
                else:  # artist not found
                    track_artist = ""

                tracklist.append((track_artist, track_title))
        # create the corresponding album, without the track offsets
        tracks: list[AudioTrack] = []
        for i in range(len(tracklist)):
            track = AudioTrack(artist=tracklist[i][0], title=tracklist[i][1])
            tracks.append(track)
        album = AudioAlbum(
            tracks=tracks,
            title=release["DTITLE"],
            year=release["DYEAR"],
            genre=release["DGENRE"],
        )
        return error_code, album


class Freedb_Server:
    """A class to query a freedb server."""

    pass

    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    # }

    # url = "http://gnudb.gnudb.org/~cddb/cddb.cgi?cmd=cddb+read+soundtrack+e5109c10&hello=emailname+emailhost.com+applicationname+0.1&proto=6"
    # req = request.Request(url, headers=headers)
    # # print(f"url={url}")
    # with request.urlopen(url=req) as response:
    #     data = response.readlines()

    # print(data)
