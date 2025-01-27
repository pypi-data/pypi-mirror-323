# Whisper UI

A simple GUI to transcribe audio using OpenAI's Whisper models.

## Installation

Whisper-UI requires Python.

If you are not familiar with Python, be sure to install from [python.org](https://www.python.org/). Be sure to confirm the following:

- If you see a checkbox about adding Python to your PATH, be sure to check it.
- You should install Python version 3.11.0 or higher.
- If you see a checkbox about installing `tkinter`, `tk`, or `tcl`, be sure to check it. `tkinter` is required for this program to run.

After installation, it is simple to confirm that everything went well:

- Open a terminal window or command prompt.
- Enter `python --version`. If `python` is unrecognized, then Python has not been added to your PATH (or is not installed).
- If the output is not "Python 3.11.0" (or some higher version like 3.11.1 or 3.12.0), your version is too low.
- Enter `python -c "import tkinter"`. If nothing happens, you are all set. If you see some error, `tkinter` was not installed with your Python distribution.

Whisper relies on a popular open-source audio/video converter called `ffmpeg`. You must install this as well. Here is a [Windows tutorial](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/), as well as [a good StackExchange post for Mac](https://superuser.com/questions/624561/install-ffmpeg-on-os-x).

### Windows

Download `Whisper UI.cmd` from this repository. Place it wherever you like on your computer. You can launch the program by running this file.

### Mac/Linux

Download `Whisper UI.sh` from this repository. Place it wherever you like on your computer. You can launch the program by running this file.

## Interface

### Menu bar

#### File menu

- "Open file" - select an audio file from your computer to transcribe.
- "Open audio directory" - select a folder from your computer containing audio files to transcribe. Avoid choosing a directory containing non-audio files.
- "Choose output directory" - select a folder from your computer to write transcriptions to.

#### Download models

A list of available models can be viewed here. A checkmark indicates you have already downloaded the model, while a download symbol is shown otherwise. Simply click on a model to initiate the download process.

#### Debug

If the UI is glitching at all, try navigating here and clicking "Reload window."

### Console

Most of the window is occupied by the console, which will display information as you adjust settings and run transcription. The  "clear output" button at the bottom of the console can be used to erase all the information on screen.

### Controls

#### Input files

The first text box allows you to entire a Unix-style pathname pattern to find audio files you want to transcribe. You can enter an absolute or relative path to a file on your computer, or select multiple files by entering an asterisk (*) somewhere in the path. The asterisk can stand for (match) any folder or file name, and even partial folder and filenames. For instance, if you have a folder called `audio_files` which contains `sample1.mp3` and `sample2.mp3`, you can grab both of them at once by writing `audio_files/*.mp3` (or `audio_files/*` if there are no other files in the folder). You can fill this box by typing or by going to "File" > "Open file" or "File" > "Open audio directory."

Once you have entered a path, you can click "List files" to display a list of all files that were found.

If you are ready to transcribe, you can hit "Transcribe."

#### Output files

The second textbox allows you to specify the folder where you want to put the transcripts. You can enter a path to any folder. If you enter a path to a folder that doesn't exist, that folder will be created. You can click "Set output directory" to confirm the existence of the chosen folder. You can fill this box by typing or by going to "File" > "Choose output directory."

The three checkboxes below the second textbox allow you to control which kinds of output you want.

- Check "Output plain transcript txt?" to get a plain `.txt` file containing the transcribed text.
- Check "Output segmentation file?" to get a `.seg` file showing the "segments" of your audio file (lengths of speech with breaks between them). By default, this file is a tab-separated values, with each line containing the speech occurring in a segment, the start time, and the end time.
- Check "Output full JSON output?" to get the full `.json` output of Whisper, which also includes a detected language code if no language is specified.

"Template formatting options..." allows you to modify the format of the plain `.txt` file and the way each line in the `.seg` file are formatted. If you modify these, be sure to click "Save" to save your choices.

##### Formatting the `.txt` output

- "Template for full transcript" allows you to decide how to format the transcript. By default, this field contains only the symbol `<<<TEXT>>>`.
- "Symbol to replace with full transcript" allows you to decide what symbol in the above template is replaced with the transcript.
- Example: If you want the transcript to be repeated a second time with an ellipsis between, you would enter `<<<TEXT>>>...<<<TEXT>>>` into the "Template for full transcript" field.

##### Formatting the `.seg` output

- "Template for each segment" allows you to decide how to format the lines of the `.seg` file. By default, this field contains the pattern `<<<SEG>>>\t<<<START>>>\t<<<END>>>`. This formatting will write the speech segment's text, then the start time, and finally the end time, with `tab` characters in between.
- "Symbol to replace with segment in each line" allows you to decide what symbol in the above template is replaced with a speech segment in each line of the `.seg` file.
- "Symbol to replace with start time in each line" works just like the segment symbol, but is replaced by the start time of the segment.
- "Symbol to replace with end time in each line" works just like the segment symbol, but is replaced by the end time of the segment.

#### Whisper options

"Currently selected Whisper model" displays the current model you are using. Any model having the `.en` suffix is a monolingual English model, and should not be used for other languages. All other models are multilingual. In general, models further down the list will be more accurate, but slower to run. They may also require more memory than your computer has. It is quite safe to attempt to use any model you like, but be advised that you may need to switch to a smaller one if a larger one fails.

"Currently selected Whisper language" displays the language Whisper will use to condition its output. You can set it to "NONE" if you prefer that Whisper automatically detect the spoken language. This may also be preferable for code-switched speech, but be advised that code-switched data in general is fairly hard to find in order to train speech models on it. As such, Whisper may handle code-switching rather poorly. Note that Whisper will generally struggle with low-resource languages.

Check "Translate to English?" if you would like the transcript of your non-English audio to be output in English. Note that Whisper will generally struggle to translate from low-resource languages.
