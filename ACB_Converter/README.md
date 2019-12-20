# ACB Coverter

## Introduction

**acb_to_mp3** uses [DereTore](https://github.com/OpenCGSS/DereTore) to extract acb files and to convert the extracted hca files to wav.
Usually the bitrate of the wav files is quite low, so the sound won't become worse by compressing it as mp3 via [lame](https://lame.sourceforge.io/).

## Usage

### direct

You can simply open the script and input the source and destination folder by hand.

### CLI

Another way is to use something like this:

```
python acb_to_mp3.py <source> <destination>
```

### import

The best way for automation would be simply importing either the convert_folder or the acb_to_mp3 function.

```
convert_folder(source_folder, destination_folder)

acb_to_mp3(source_file, destionation_folder)
```