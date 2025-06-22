### fat-recon

A utility for extracting deletes files from FAT12, FAT16, and FAT32 filesystems without mounting the drive. This tool reads the filesystem structure directly from the raw device or disk image, making it useful for data recovery, forensic analysis, or working with corrupted filesystems that cannot be mounted normally.

### Features

- Direct filesystem access - Reads FAT filesystems without requiring mount operations
- Multiple FAT support - Works with FAT12, FAT16, and FAT32 variants
- Cross-platform - Supports Windows, Linux, and macOS
- Selective extraction - Extract specific files or entire directory trees
- Preserve metadata - Maintains original timestamps and file attributes
- Damaged filesystem support - Can often recover files from partially corrupted drives
- Multiple input sources - Works with physical drives, disk images, and USB devices

### Installation

To install, first create a virtual environment for python:

```
python -m venv test-env
cd test-env
source bin/activate
```

After doing so, clone the repository and install the libraries:

```
git clone https://github.com/Nightfire390/fat-recon
cd fat-recon
```

### Usage

After installing the libraries, simply run:
```
python ./main.py
```

### License

This project is licensed under the MIT License - see the LICENSE file for details.
