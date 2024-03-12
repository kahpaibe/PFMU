""" Library to get a musicbrainz discid from a cd """

from numpy import uint32  # unsigned 32-bit integer

SECTOR_RATE = 75  # 75 sectors per second


def sum_dec_digits(n: int) -> int:
    """Returns the sum of the decimal digits of n. Stands for cddb_sum in CDex.

    Args:
        n (int): The number to sum the digits of. Should be positive."""

    if n < 0:
        raise ValueError(f"n should be positive, got n={n}.")

    total = 0
    while n > 0:
        total += n % 10
        n = n // 10
    return total


def calculate_disc_id(track_sector_indexes_extended: list[int]):
    """Given an album, calculates the CDDB disc id for freedb server queries.

    Args:
        track_sector_indexes_extended (list[int]): The sector indexes for the tracks on the CD, plus the lead-out index. (The lead-out index is the last index on the CD, plus 1.)
    """
    # init
    t = uint32(0)
    n = uint32(0)
    numtracks = (
        len(track_sector_indexes_extended) - 1
    )  # the number of tracks, removing the lead-out index

    # computation. See https://fr.wikipedia.org/wiki/DiscId
    for i in range(numtracks):
        dwSectors = track_sector_indexes_extended[i]
        n += sum_dec_digits(dwSectors // SECTOR_RATE)

        dwSectorsNext = track_sector_indexes_extended[i + 1]
        t += dwSectorsNext // SECTOR_RATE - dwSectors // SECTOR_RATE

    dwRet: uint32 = (n % 0xFF) << 24 | t << 8 | (uint32)(numtracks)

    return dwRet
