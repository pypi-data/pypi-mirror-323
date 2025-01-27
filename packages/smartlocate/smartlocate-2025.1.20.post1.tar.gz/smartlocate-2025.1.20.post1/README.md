# smartlocate - Intelligent File Indexer

smartlocate is a tool for Linux that uses YOLO and many other AI tools (no GPU required! Everything is done locally) to detect objects in images, describe images and creates a database of detected objects, image descriptions, text contents and so on, and makes them searchable. This database is stored locally and allows you to search for specific objects in images. smartlocate uses an SQLite database to efficiently store and search data.

If the parameter `--ocr` is set while indexing, all images are also OCRed and the found text is searchable. You can set the language with `--lang_ocr tr` for example. Default is `["de", "en"]`.

If the parameter `--describe` is set while indexing, the model `Salesforce/blip-image-captioning-large` will be used to generate descriptions of images automatically, which also then can be searched.

## Quickstart

```bash
# Install the tool
python3 -mvenv ~/smartlocate/
source ~/smartlocate/bin/activate
pip install smartlocate

# Index files (Using all possible indexing methods)
smartlocate ~/Documents --index

# Index files (using OCR, face-recognition, qr-code detection)
smartlocate ~/Documents --index --ocr --face_recognition --qrcodes

# Index files (Using all possible indexing methods), run hourly (won't work with new faces)
smartlocate ~/Documents --index --run_hourly

# Search for cats
smartlocate "cat"

# Search for cat in /home/username/Documents
smartlocate cat /home/username/Documents

# Search for "cat and dog" (order doesn't matter) in /home/username/Documents
smartlocate cat and dog /home/username/Documents

# Search for "cat and dog" (exactly in that order) in /home/username/Documents
smartlocate "cat and dog" /home/username/Documents --exact

# Help
smartlocate --help
```

## Screenshots

### Indexing

This shows the indexing process, with `--face_recognition` enabled. This means it asks for a name the first time a face is shown, but later on, it detects it automatically and can associate the face with a name, making it easily searchable.

<p align="center">
<img src="https://raw.githubusercontent.com/NormanTUD/smartlocate/refs/heads/main/images/index.gif" alt="Indexing" width="1046"/>
</p>

### Face recognition while indexing

While indexing, with `--face_recognition`, faces are recognized. If the face cannot be automatically determined, it will ask you for the name of the person. For later images, this person will (most probably) be automatically detected again without any intervention.

<p align="center">
<img src="https://raw.githubusercontent.com/NormanTUD/smartlocate/refs/heads/main/images/face_recognition.gif" alt="Face Recognition" width="1046"/>
</p>

If you don't want to wait manually for a long time, you can run smartlocate with `--dont_ask_new_faces`. This will skip images where person are found, but cannot be determined. This way, you can run it through a whole folder over night without manual intervention, and then run it again after it's done without that option, so that you get asked for all new faces. This way, you don't get longer waiting periods before entering names again.

## Searching

### Images of cats and dogs

These images were not manually labelled. Those labels were found by AI!

<p align="center">
<img src="https://raw.githubusercontent.com/NormanTUD/smartlocate/refs/heads/main/images/dog.gif" alt="Search: Dog" width="1046"/>
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/NormanTUD/smartlocate/refs/heads/main/images/cat.gif" alt="Search: Cat" width="1046"/>
</p>

### Searching through Documents

This is a search on OCR'ed documents.

<p align="center">
<img src="https://raw.githubusercontent.com/NormanTUD/smartlocate/refs/heads/main/images/ocr.gif" alt="OCR" width="1046"/>
</p>

## Features

- Easy to install and use.
- Object detection in images using YOLO.
- OCR is done via easyocr, when `--ocr` was set during indexing. Allows you to use `%` as a wildcard.
- Qr-Code-Detection and indexing.
- Documents are converted with pandoc. Allowed document types are: `['.doc', '.docx', '.pptx', '.ppt', '.odp', '.odt', '.md', '.txt', '.pdf']`. Use `--documents` while indexing for finding documents.
- Stores detected objects in a local SQLite database (`~/.smartlocate_db`).
- Fast searching for specific objects in images.
- Supports Sixel graphics for visualizing results.
- Automatic face recognition (use `--face_recognition` while indexing). It will ask you (hopefully only once) per person what their name is, so it can recognize them later on automatically. You only have to label a person once (or a few times, when the images are VERY different), and after being labelled once, it will auto-detect them in other images as well.

## Installation

### Get latest official release

This will get the latest officially released version from <a href="https://pypi.org/project/smartlocate">pypi</a>.

```
python3 -mvenv ~/smartlocate/
source ~/smartlocate/bin/activate
pip3 install smartlocate
```

### Run latest version

1. Clone the repository:

```bash
   git clone --depth 1 https://github.com/NormanTUD/smartlocate.git
```

2. Navigate to the directory and run the following command to install the tool:

```bash
cd smartlocate
./smartlocate --index --dir ~/Pictures
```

smartlocate will automatically install all necessary dependencies, and YOLO is already included. This is done on first execution, which may take some time. But this only has to be done once!

## Usage

### Indexing Images

To index images in a specific directory, run the following command:

```bash
smartlocate --dir /path/to/images --index
```

YOLO and an image description AI will be used to detect objects in images, and pandoc is used for indexing all kinds of documents, and the results will be stored in the database.

You need to re-run the index every time new images are added or changed.

### Searching for Objects

To search for a specific object (e.g., "cat"), run the following command:

```bash
smartlocate cat
```

The tool will search the indexed images for the object and display the results.

## Options

- `--index`: Indexes images in the specified directory.
- `--size SIZE`: Specifies the size to which images should be resized when indexing. Default is 400.
- `--dir DIR`: Specifies the directory to search or index.
- `--debug`: Enables debug mode to output detailed logs.
- `--no_sixel`: Hide Sixel graphics.
- `--qrcodes`: Enable indexing of qr-codes/search only qr-codes
- `--describe`: Saves descriptions of images (generated by AI) as well and makes them searchable
- `--exact`: Searches exactly what is entered, without splitting
- `--ocr`: Enable OCR.
- `--documents`: Enable documents.
- `--lang_ocr`: OCR languages, default: de, en. Accepts multiple languages.
- `--delete_non_existing_files`: Deletes non-existing files from the database.
- `--shuffle_index`: Shuffles the list of files before indexing.
- `--model MODEL`: Specifies the YOLO model for object detection.
- `--threshold THRESHOLD`: Sets the confidence threshold for object detection (0-1).
- `--dbfile DBFILE`: Specifies the path to the SQLite database file.
- `--exclude PATH`: Excludes a path from indexing/searching. Can be used multiple times.
- `--dont_ask_new_faces`: Don't ask for new faces (useful for automatically tagging all photos that can be tagged automatically).

## Example Commands

### Indexing images in a directory:

```bash
smartlocate --dir /home/user/images --index
```

### Search for images containing the object "cat":

```bash
smartlocate cat
```

### Indexing:

Indexing with YOLO, Description and OCR:

```bash
smartlocate --dir /home/user/images --index
```

## Database

The results of image indexing are stored in the SQLite database `~/.smartlocate_db`. This database contains information about detected
objects in the images. The index must be re-run whenever new images are added or changes are made.

## Manage single images

Simply run `smartlocate /path/to/an/image/file.jpg` to see an overview of the image file's data and modify it.

## Requirements

- Python 3.x
- All python-dependencies will be automatically installed when the tool is first run.

## Ideas

Future ideas would be to expand this to other formats than images as well. Imagine you could say:

```bash
smartlocate "text about cats"
```

and get all `.txt`, `.md`, `.docx`, `.tex` and so on files in which something about cats is written. Currently, document indexing is only done via a full-text search.

Same for videos and audio files. If someone wants to do it, feel free to contribute!

## Troubleshooting

### The SQlite3-file is too large

When the sqlite3-file is too large, you can vacuum it:

```bash
smartlocate --vacuum
```

This will not delete any data, but just free up claimed, but yet unreleased space.

## License

Licensed under GPL2.
