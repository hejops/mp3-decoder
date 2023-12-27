import os

from decode import get_bits
from decode import MP3Stream

_dir = os.path.dirname(__file__)


def test_get_bits():
    assert get_bits(b"\xff") == [1] * 8
    assert get_bits(b"\xff\xfb\x90D") == [
        int(x) for x in "11111111111110111001000001000100"
    ]


# assert as_decimal([0, 1, 1, 1]) == 7
# assert as_decimal([1, 0, 1]) == 5
# assert as_decimal([1, 1, 1, 1]) == 15
# assert as_decimal([1, 1, 1]) == 7
# assert False


def test_stream_bitrate():
    # vbr 205 kb/s
    # 3.996 s
    # 44.1 kHz
    # V1L3 (i.e. supported)

    file = f"{_dir}/Free_Test_Data_100KB_MP3.mp3"
    assert os.path.isfile(file)
    stream = MP3Stream(file)
    assert stream.bitrate == 206
