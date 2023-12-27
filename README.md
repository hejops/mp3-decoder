# mp3-decoder

Building an mp3 decoder in Python. For learning/teaching purposes only.

## Descriptions

- ISO/IEC 11172-3

- [Lagerstrom_MP3_Thesis | PDF](https://www.slideshare.net/KristerLagerstrm/lagerstrommp3thesis)
- [MP3 File Format Specification](http://mpgedit.org/mpgedit/mpeg_format/MP3Format.html)
- [Mp3-Standard-Tutorial](https://www.scribd.com/document/191253204/Mp3-Standard-Tutorial)
- [The AudioFile: Understanding MP3 compression | Ars Technica](https://arstechnica.com/features/2007/10/the-audiofile-understanding-mp3-compression/)
- [lets-build-mp3-decoder.html](http://blog.bjrn.se/2008/10/lets-build-mp3-decoder.html)
- [mp3_theory.pdf](http://www.mp3-tech.org/programmer/docs/mp3_theory.pdf)

## Implementations

- [minimp3 \(C)](https://github.com/lieff/minimp3)
- [pdmp3 \(C)](https://github.com/technosaurus/PDMP3/blob/master/pdmp3.c)
- [mp3vis (TypeScript)](https://github.com/murachue/mp3vis)

## Example mp3 files

- [free test data](https://freetestdata.com/audio-files/mp3/)

# Frame header

- [MPEG Audio Frame Header - CodeProject](https://www.codeproject.com/Articles/8295/MPEG-Audio-Frame-Header#MPEGAudioFrameHeader)
  <!-- mp3_theory 5.1.1 -->

| Bits | Item           | Example |
| ---: | -------------- | ------- |
|   11 | Sync           | FFF     |
|    2 | MPEG Version   |         |
|    2 | MPEG Layer     |         |
|    1 | Protection     |         |
|    4 | Bitrate        |         |
|    2 | Samp. freq.    |         |
|    1 | Padding        |         |
|    1 | Private        |         |
|    2 | Mode           |         |
|    2 | Mode extension |         |
|    1 | Copyright      |         |
|    1 | Original media |         |
|    2 | Emphasis       |         |

# Bit reservoir

- [MP3 Sync Words](https://hydrogenaud.io/index.php?PHPSESSID=3o88ooq6elo28np5puk2k600fn&topic=47020.msg421185#msg421185)
