#!/usr/bin/env python3
"""
MP3 decoder (prototype)

"""
import enum
import os
from typing import Literal
from typing import Sequence

# import numpy as np

Bit = Literal[0, 1]

# docstring guidelines: first line must be imperative (first word is the verb),
# the rest should be descriptive. if docstring is 1-line, omit the period
#
# class docstrings are descriptive


# enums should be used for categoricals (or any non-numerical data), as they
# allow easy renaming and relatively easy indexing (compared to dict)
class MPEGVersion(enum.Enum):
    MPEG1 = (1, 1)
    MPEG2 = (1, 0)
    MPEG2_5 = (0, 0)
    RESERVED = (0, 1)


class MPEGLayer(enum.Enum):
    I = (1, 1)
    II = (1, 0)
    III = (0, 1)
    RESERVED = (0, 0)


BITRATES: list[int] = [
    # kilobits (1000, not 1024) per second
    0,  # free
    32,
    40,
    48,
    56,
    64,
    80,
    96,
    112,
    128,
    160,
    192,
    224,
    256,
    320,
    0,  # reserved
]

SAMPLING_RATES: list[int] = [
    44100,
    48000,
    32000,
    0,  # reserved
]


def get_bit_slice(
    bits: list[Bit],
    i: int,
    n: int,
) -> tuple[Bit, ...]:
    return tuple(bits[i : i + n])


def get_bits(byte_chunk: bytes) -> list[Bit]:
    """Decompose <byte_chunk> of len n to a list of n*8 bits"""
    bits = []
    for byte in byte_chunk:
        for bit in reversed(range(8)):
            x = (byte >> bit) & 1
            bits.append(x)
    # assert len(bits) == len(byte_chunk) * 8
    return bits


def as_decimal(bits: Sequence[Bit]) -> int:
    _sum = 0
    for i, bit in enumerate(reversed(bits)):
        _sum += bit * 2**i
    return _sum


class MP3Frame:
    """Initialised with information from a fully parsed header frame. An
    MP3Frame has no concept of its position (index) in the MP3Stream.

    Audio is encoded in the frequency domain and must be transformed into the
    time domain for playback.

    """

    def __init__(
        self,
        bitrate: int,
        padded: bool,
        sampling_rate: int,
        samples_per_frame: int = 384,
    ):
        self.bitrate = bitrate
        self.padded = padded
        self.samples_per_frame = samples_per_frame
        self.sampling_rate = sampling_rate

        assert self.sampling_rate
        self.frame_size: int = (
            (self.samples_per_frame // 8 * self.bitrate * 1000) // self.sampling_rate
        ) + self.padded
        # self.frame_size: int = (
        #     (self.samples_per_frame // 8 * self.bitrate) // self.sampling_rate
        # ) + self.padded

        self.main_bytes = None

    def __repr__(self) -> str:
        return f"""{self.__class__.__name__}
    Samples per frame: {self.samples_per_frame}
    Bitrate: {self.bitrate}
    Sampling rate: {self.sampling_rate}
    Padded: {self.padded}
    Frame size: {self.frame_size}"""

    def add_main(self, main_bytes: bytes):
        ...


class MP3Stream:
    """Object representing an mp3 stream containing one or more MP3Frames"""

    def __init__(self, file: str = ""):
        self.file = file
        self.frame_idxs: list[int] = []
        self.frames: dict[int, MP3Frame] = {}

        if os.path.isfile(self.file):
            self.read_bytes()

        self.bitrate = self.get_bitrate()

    def __len__(self) -> int:
        return len(self.frames)

    def get_bitrate(self) -> int:
        if not self.frames:
            return 0
        return sum(f.bitrate for f in self.frames.values()) // len(self)

    def parse_header_frame(self, header_bytes: bytes) -> MP3Frame | None:
        """Parse 32 header bits in sequence, return None on the first error.

        The first 12 bits are assumed to be all 1 (fixed sync word). The
        remainder of the 20 bits, after parsing, are then declared as args to
        construct an MP3Frame. For an exceptionally detailed breakdown of the
        header frame, refer to:

        https://www.codeproject.com/Articles/8295/MPEG-Audio-Frame-Header#MPEGAudioFrameHeader

        Only MPEG version 1, layer III is supported.

        An example of a header frame would be (in hex): 'ff fb c0 44'

        http://gabriel.mp3-tech.org/mp3infotag.html
        http://www.mp3-tech.org/programmer/frame_header.html
        https://hydrogenaud.io/index.php/topic,47020.msg422197.html#msg422197

        """

        bits = get_bits(header_bytes)

        # sync word
        if bits[:11] != [1] * 11:
            return None

        try:
            mpeg_ver = MPEGVersion(get_bit_slice(bits, 11, 2))
            mpeg_layer = MPEGLayer(get_bit_slice(bits, 13, 2))
        except ValueError:
            return None

        if not (mpeg_ver is MPEGVersion.MPEG1 and mpeg_layer is MPEGLayer.III):
            return None

        # assert False

        bitrate = BITRATES[as_decimal(get_bit_slice(bits, 16, 4))]
        if not bitrate:
            return None
        # print(bitrate)

        sampling_rate = SAMPLING_RATES[as_decimal(get_bit_slice(bits, 20, 2))]
        if not sampling_rate:
            return None

        frame = MP3Frame(
            bitrate=bitrate,
            padded=bits[22] == 1,
            sampling_rate=sampling_rate,
        )
        # print(bits[15])  # assumed to be 1 (no CRC)
        print(frame)
        return frame

        # # the remaining bits (copyright, original, emphasis) are ignored for now
        #
        # # private = bits[23] == 1
        # channel_bits = get_bit_slice(bits, 24, 2)
        # mode_ext = get_bit_slice(bits, 26, 2)  # only for joint_stereo
        #
        # assert False

    def read_bytes(self):
        """Iterate through all bytes of the MP3 stream, constructing MP3Frames
        where valid.

        Every complete frame begins with an 8-byte (32-bit) header frame. In
        many cases (but not all), the header frame begins with the 3-byte
        (12-bit) sequence 'FFF', which consists of 11 bits for the sync word
        (fixed), and the first of 2 bits representing MPEG Version (1 or 2).

        In the uncommon case, the first version bit can be 0 (representing MPEG
        Version 2.5), thus giving 'FFE'. For now, we assume the sync word is
        'FFF' for ease of iteration; Version 2.5 may be addressed with a unit
        test at some point.

        When a valid header frame is found, the parsed information is used to
        construct a bare MP3Frame, which, at this point, will contain only
        header data. The remaining data will be added to the MP3Frame later.

        """

        print(self.file)
        with open(self.file, "rb") as f:
            # for byte in f:
            #     print(byte)  # byte array (?)

            # natively, python always iterates through bytes as int. to do
            # anything useful, ints must be converted to bytes (and then bits),
            # which is clunky
            byte_array = f.read()
            for i, b_int in enumerate(byte_array):
                if b_int != 255:
                    continue

                header_bytes = byte_array[i : i + 4]
                frame = self.parse_header_frame(header_bytes)
                if frame:
                    self.frame_idxs.append(i)
                    self.frames[i] = frame

            # print(frame.count("fffbc044"))  # 323
            # print(frame.count("fffbd044"))  # 572

            # # numpy
            # # don't ever call .tolist(), as it consumes massive amounts of memory
            # by = np.frombuffer(f.read(), dtype="S1")
            # print(by)


stream = MP3Stream("tests/Free_Test_Data_100KB_MP3.mp3")
print(
    stream,
    stream.bitrate,
)

# Goals
# - Get main data of each frame, using frame indices as boundaries
# - Hardcoded Huffman tables (standard 15/32)
# - Read metadata (beginning and/or end, id3 and/or ape)
# - Read single logical frame (decompress, reconstruct, transform; freq -> time)
# - 1-2 channels _ 2 granules _ 576 freq samples
# - Requantise

# - Read and decode all frames

# - Seek to frame
# - Calc duration
# - Calc bitrate
# - Dynamic range
# - Spectrogram
# - Play stream

# Test cases: 8, 32, 128, 256, 320, vbr, flac (reject)
