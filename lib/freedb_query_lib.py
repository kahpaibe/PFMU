""" Tools to query freedb servers. """

# Params
CDDB_SERVERS = [
    "http://gnudb.gnudb.org/~cddb/cddb.cgi",
    "http://freedb.freedb.org/~cddb/cddb.cgi",
]

DEFAULT_USER = "pyfreedbutil"
DEFAULT_HOST = "pyfreedbutil_instance1"
DEFAULT_APP = "pyfreedbutil"
DEFAULT_VERSION = "0.0.2"
DEFAULT_PROTOCOL = 5


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

    disc_type = 1  # always 1
    user = ""
    host = ""
    app = ""
    version = ""
    protocol = 5

    def __init__(
        self,
        user: str = DEFAULT_USER,
        host: str = DEFAULT_HOST,
        app: str = DEFAULT_APP,
        version: str = DEFAULT_VERSION,
        protocol: int = DEFAULT_PROTOCOL,
    ) -> None:
        self.user = user
        self.host = host
        self.app = app
        self.version = version
        self.protocol = protocol


class Freedb_Query_Generator:
    """Quickly generates a Freedb_Query by saving user informations."""

    user = ""
    host = ""
    app = ""
    version = ""
    protocol = 5

    def __init__(
        self,
        user: str = DEFAULT_USER,
        host: str = DEFAULT_HOST,
        app: str = DEFAULT_APP,
        version: str = DEFAULT_VERSION,
        protocol: int = DEFAULT_PROTOCOL,
    ) -> None:
        self.user = user
        self.host = host
        self.app = app
        self.version = version
        self.protocol = protocol

    def generate_query(self) -> Freedb_Query:
        """Generates a Freedb_Query with the stored informations.

        Returns:
            Freedb_Query: The generated query."""
        return Freedb_Query(self.user, self.host, self.app, self.version, self.protocol)

    def get_query_url(self, freedb_server_url: str):
        """Generates the url to send the query to the server.

        Args:
            freedb_server_url (str): The url of the server.

        Returns:
            str: The generated url."""
        return f"{freedb_server_url}?cmd=cddb+query+E512640F+15+150+23780+56867+73962+96577+124515+141320+156755+178960+204585+236400+259287+289755+315007+338777+4710&hello={self.user}+{self.host}+{self.app}+{self.version}&proto={self.protocol}"


class Freedb_Server:
    """A class to query a freedb server."""

    freedb_server_url = ""

    def __init__(self, freedb_server: str) -> None:
        self.freedb_server_url = freedb_server

    def query(self, query: Freedb_Query) -> str:
        """Send a query to the server.

        Args:
            query (freedb_query): The query to send.

        Returns:
            str: The response from the server."""
        return "response"  # TODO


# example url http://gnudb.gnudb.org/~cddb/cddb.cgi?cmd=cddb+query+E512640F+15+150+23780+56867+73962+96577+124515+141320+156755+178960+204585+236400+259287+289755+315007+338777+4710&hello=LeoG+DESKTOP-MI21S05+PythonCddbServer+1.1.0&proto=5
# if discid:
#     self.track_offset = map(int, discid.split()[2:-1])
#     self.disc_length = int(discid.split()[-1:][0]) * 75
#     query = urllib.parse.quote_plus(discid.rstrip())
#     url = "%s?cmd=cddb+query+%s&hello=%s+%s+%s+%s&proto=%d" % (
#         self.cddbServer,
#         query,
#         self.user,
#         self.host,
#         self.app,
#         self.version,
#         self.protocol,
#     )
#     res = urllib.request.urlopen(url)
#     print(f"url={url}")
#     header = res.readline().decode("latin-1").rstrip()
