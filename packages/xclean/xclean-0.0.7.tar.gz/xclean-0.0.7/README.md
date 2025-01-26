# xclean

File de-duplication utility.

Scan files in main to record main files to compare against.

Scan files in target to find files that are duplicates of those in main.

By default it just lists the duplicates.

## Removing duplicates

Specify --remove to actually remove the duplicate files.

## Archiving duplicates

Specify --archive-to to archive the duplicate files to another location.

## Archiving new files

Specify --archive-new to archive any new files to another location.

## Trashing duplicates

Specify --trash to move the duplicate files to the trash.

## Reset the database

Reset the database content of main files by specifying --clean.

## Compare XMP files as well

To compare the file and associated XMP file specify the --xmp option as well.

## Compare AAE files as well

To compare the file and associated AAE file specify the --aae option as well.

## Scanning specific file types

To scan files of specific types use the --include and --exclude options.

## Prompt before changing

To answer a prompt before changing a file specify --prompt

## Installation

### Using pypi

    pip install xclean

### Using github

    pip install https://github.com/bbc6502/xclean/archive/refs/heads/main.zip

## Usage

    usage: xclean [-h] [-m MAIN] [-t TARGET] [-a ARCHIVE_TO] [-n ARCHIVE_NEW] [-i [EXTENSIONS ...]] [-x [EXTENSIONS ...]] [--unprotect] [--remove] [--trash] [--clean] [--prompt]

    options:
      -h, --help            show this help message and exit
      -m MAIN, --main MAIN
                            Directory where master files reside
      -t TARGET, --target TARGET
                            Directory where duplicate files may reside
      -a ARCHIVE_TO, --archive-to ARCHIVE_TO
                            Archive duplicates to folder
      -n ARCHIVE_NEW, --archive-new ARCHIVE_NEW
                            Archive new files to folder
      -i [EXTENSIONS ...], --include [EXTENSIONS ...]
                            Include Extensions
      -x [EXTENSIONS ...], --exclude [EXTENSIONS ...]
                            Exclude Extensions
      --unprotect           Unprotect main files
      --remove              Remove duplicate files
      --trash               Trash duplicate files
      --clean               Clean database
      --xmp                 Include XMP files in checks for duplicates
      --aae                 Include AAE files in checks for duplicates
