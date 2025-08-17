# BookMan

Automatically reads books from Jonathan Basile's online implementation of Jorge Luis Borge's classic short story "The Library of Babel" (http://libraryofbabel.info). Bookman chooses a hex at random and then scans through all the books contained within, looking for evidence of actual, readable English language.

## Features
- Outputs any findings to an easily parseable SQLite database.
- Multi-threading support
- Uses a word-counting heuristic to pre-assess text segments, ensuring that the LLM only gets called when there's a high chance that something's been found.
- Leverages your own Ollama server (not included) for fast, private local processing.
- Easy-to-tweak plaintext configuration file.

## Dependencies
- Access to a working Ollama server: You can use pretty much any language model you want, but it must be running on an Ollama server which you have API access to. I recommend you use a locally-hosted server for optimal performance.
- Ollama Python module: Can be installed via PIP or whatever your favorite package manager is.
- SQLite3
- Soft Requirement: a *nix operating system. By default, BookMan leverages /usr/share/dict/words as its reference dictionary. If you want to run this program on Windows then you'll need to download your own word list and point to it in the config file.

## How to Install
1. Download this repository
2. Ensure you have all the dependencies listed above
3. Open up bookman.conf in a text editor and set the address of your Ollama server (llmHost) as well as your choice of language model (llmModel). While you're there, tweak any other settings that you'd like.
4. Run bookman.py and enjoy!

## The Configuration File
Below is an explanation of each of the config file options:

- loglevel : The level of verbosity for the program log. Right now, INFO is the only level supported.

- logfile : The location and name of the log file (default bookman.log).

- dbfile : The location and name of the SQLite database file (default bookman.db).

- testfile : The location and name of the "test book" (default testbook.txt). As the name implies, the "Test Book" is only used when you put the program in a special testing mode - it won't be used during normal operation.

- dictfile : The location and name of the word list to be used as BookMan's reference dictionary. By default, the standard *nix wordlist at /usr/share/dict/words is used. If you are running on Windows or another OS which doesn't use the above, then you need to download your own word list and set its location here. 

- seglength : How long of a text segment (in number of characters) BookMan analyzes at one time. Default is 40.

- wordCount : The minimum number of CONSECUTIVE English words a given text segment needs to have in order to trigger a finding. Default is 5. Protip: I've noticed that if you set it to 3 or less you tend to get a lot of false positives.

- cCount : The total number of processing threads to use (in other words, how many books the program will try to read simultaneously). Set to 0 to have BookMan auto-detect the thread count based on how many logical CPUs your computer has. Default is 0. 

- llmHost : The address and port number of your Ollama server. Default is localhost:11434.

- llmModel : The language model you wish to use to assess candidate text segments. Default is gemma2 just because it's my personal favorite, but you'll need to set it to whatever model you have/prefer.

- llmPrompt : The prompt that's fed to the language model (along with the candidate text segment) to explain to the model what it's being asked to do. I recommend you don't mess with this unless you're very comfortable with prompt engineering.


## How to View the Results
In addition to scrolling log output on the screen (and also bookman.log), BookMan writes its findings to an SQLite3 database. Unfortunately, right now the only way to access the contents of that database is to open it up manually using sqlite's command line utility. I'm working on a proper tool for perusing the database but I haven't written it yet. 

The database contains two tables:
- stats, which contains a single row of data storing the total number of books read along with your computer's average reading speed (in minutes-per-book).
- passages, which contains BookMan's actual findings. This includes the exact address of the book in question, the page number the passage was found on, the contents of the passage, its Word Count score, and a boolean flag showing whether or not the LLM confirmed the finding.

## Special Credits
BookMan wouldn't exist without the following people:

- Jorge Luis Borge, who wrote the original Library of Babel short story.

- Jonathan Basile, who made the Library of Babel a reality via software.

- Victor Barros, who created the "Pybel" API that allows us to download books from the Library. See https://github.com/victor-cortez/Library-of-Babel-Python-API for Victor's original source code.

- Reddit user u/Silly_King3635, who came up with the original idea for BookMan (sorry, don't know their real name!)