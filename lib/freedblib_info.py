""" Contains information about freedblib """

from typing import Literal, Union

DEFAULT_USER = "emailname"
DEFAULT_USER_EMAIL = "emailhost.com"
DEFAULT_HOST = "pyfreedbutil_instance1"
DEFAULT_APP = "pyfreedbutil"
DEFAULT_VERSION = "0.0.3"
DEFAULT_PROTOCOL = "5"

CDDB_SERVERS = [
    "http://gnudb.gnudb.org/~cddb/cddb.cgi",
    "http://freedb.freedb.org/~cddb/cddb.cgi",
]

FREEDB_CATEGORIES = [
    "blues",
    "classical",
    "country",
    "data",
    "folk",
    "jazz",
    "newage",
    "reggae",
    "rock",
    "soundtrack",
    "misc",
]
FREEDB_CATEGORIES_TYPE = Union[
    Literal["blues"],
    Literal["classical"],
    Literal["country"],
    Literal["data"],
    Literal["folk"],
    Literal["jazz"],
    Literal["newage"],
    Literal["reggae"],
    Literal["rock"],
    Literal["soundtrack"],
    Literal["misc"],
]

FREEDB_CATEGORIES_REGEX_PREGROUP = (
    r"blues|classical|country|data|folk|jazz|newage|reggae|rock|soundtrack|misc"
)
