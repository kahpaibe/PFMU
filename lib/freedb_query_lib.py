""" Tools to query freedb servers. """

import re
from typing import Any, Literal, Union

from . import freedblib_info
from .freedb_Objects import AudioAlbum

# samples
# query -> 2: http://gnudb.gnudb.org/~cddb/cddb.cgi?cmd=cddb+query+0D023E02+2+150+21815+576&hello=emailname+emailhost.com+applicationname+0.1&proto=5
# read1:  http://gnudb.gnudb.org/~cddb/cddb.cgi?cmd=cddb+read+soundtrack+0D023E02&hello=emailname+emailhost.com+applicationname+0.1&proto=5
# read2:  http://gnudb.gnudb.org/~cddb  /cddb.cgi?cmd=cddb+read+blues+0D023E02&hello=emailname+emailhost.com+applicationname+0.1&proto=5


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


# QUERY = [FreedbHelper.Commands.CMD_QUERY,
# 		querystring,]
# QUERYSTRING = [ HEXCDDBID, TRACKCOUNT, "+TRACKOFFSET x n", toc.length
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
        category: freedblib_info.FREEDB_CATEGORIES_TYPE = "rock",
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
            category (freedblib_info.FREEDB_CATEGORIES_TYPE, optional, for "read" query type only): The category of the album. Defaults to "rock".
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
        category: freedblib_info.FREEDB_CATEGORIES_TYPE = "rock",
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
        self.category: freedblib_info.FREEDB_CATEGORIES_TYPE = category

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


class Freedb_Server:
    """A class to query a freedb server."""

    pass


class Freedb_Query_Query_Reader:
    """A class to read the result of a "query"-type query."""

    re_get_body: re.Pattern[str]
    re_quadruplets: re.Pattern[str]

    def __init__(self) -> None:
        """"""
        self.re_get_body: re.Pattern[str] = re.compile(
            r"^(\d{1,4})\sFound .+?, list follows \(until terminating `.'\) (.*) \.$"
        )
        self.re_quadruplets = re.compile(
            r"("
            + freedblib_info.FREEDB_CATEGORIES_REGEX_PREGROUP
            + r") ([0-9a-fA-F]{8}) ([^\/]+?) / ([^\/]+?) (?="
            + freedblib_info.FREEDB_CATEGORIES_REGEX_PREGROUP
            + r")"
        )

    def get_query_quadruplets(
        self, query_result: str
    ) -> tuple[str, list[tuple[str, str, str, str]]] | list[None]:
        """Parses the query result to get the query triplets.

        Args:
            query_result (str): The result of the query.

        Returns:
            tuple[str,list[tuple[str, str, str]]]
                str, return code
                tuple[str,str,str,str], the quadruplets triplets. Empty if none.

            A quadruplets is a list of 4 strings: [category, disc_id, artist, album_name]
        """

        # get the body of the query
        match = self.re_get_body.match(query_result.strip())
        if match is None:
            return []
        else:
            response_code = match.group(1)
            body = match.group(2) + " blues"
        # get the triplets

        quadruplets: list[tuple[str, str, str, str]] = self.re_quadruplets.findall(body)

        return response_code, quadruplets


class Freedb_Query_Read_Reader:
    """A class to read the result of a "read"-type query."""

    re_get_body: re.Pattern[str]
    re_tripplets: re.Pattern[str]

    def __init__(self) -> None:
        """"""
        self.re_get_body: re.Pattern[str] = re.compile(
            r"^(\d{1,4})\sFound .+?, list follows \(until terminating `.'\) (.*) \.$"
        )
        self.re_releases = re.compile(r"")

    def get_read_releases(
        self, query_result: str
    ) -> tuple[str, list[list[Any]]] | list[None]:

        return []
