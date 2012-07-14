Arduino Scons (alternative)
===========================

An alternative way of building arduino sketches with scons.

This project is designed to be:

- Flexible. Custom libraries? Multiple builds for different boards uploaded to the correct ports from one script? No problem.
- Easy to understand. No source munging. No automatic library detection. No magic.

Installation
------------

This can either be installed system-wide, or per-project. Either way,
`arduino.py` should be installed in `$SITE_SCONS/site_tools`, where
`$SITE_SCONS` is one of the directories listed in the scons man page under the
`--site-dir` flag.

On Linux the following directories are appropriate:

- `/usr/share/scons/site_scons`
- `$HOME/.scons/site_scons`
- `./site_scons`

Installing into `$HOME/.scons/site_scons` can be accomplished by running
`./install.py`.

Usage
-----

This script does not do any munging of your source files, so you may need reorder your functions (or add function prototypes), and add `#include <Arduino.h>`. Your sketch should be in a `cpp` file, rather than an `ino` file.

A script to compile and upload a basic sketch might look something like this:

```python
env = Environment(tools=["default", "arduino"])
env.ConfigureBoard("atmega328")
core = env.ArduinoCore()

sketch = env.Sketch("blink", ["blink.cpp", core])
env.Upload(sketch)
```

See the `examples` directory  for more examples.

API
---

Installing the tool into an environment gives it the following methods:

### env.ConfigureBoard(board_name)

This sets defaults for a whole bunch of environment variables (described below), based on the board name. The supported boards and their settings can be found in `$ARDUINO_HOME/hardware/arduino/boards.txt`.

### env.ArduinoCore()

Compile the arduino core library into a static library.

### env.ArduinoLibrary(name)

Compile a standard arduino library into a static library, and add it to the include path.

### env.ArduinoLibrary(name, path)

Compile an arduino library in a given directory into a static library, and add it to the include path.

### env.Sketch(name, sources)

Uses.`env.Program` and `env.Hex` to compile a list of sources (either source files or libraries) into a hex file (named name.hex) for uploading.

### env.Upload(hex_file, name="upload")

Adds an alias (named upload by default) which uploads the given hex file to an arduino connected to `$UPLOAD_PORT`. Strange things happen if this is called multiple times with the same name; either add an alias which defers to multiple upload targets, or use `env.UploadAll()`.

### env.UploadAll(name="upload")

Add an alias which defers to all upload targets in `$ALL_UPLOADS`, which is updated by `env.Upload`.

Variables
---------

#### BOARD

The name of the board passed to `env.ConfigureBoard`.

#### F_CPU

CPU frequency in Hz.

#### MCU

MCU string passed to gcc and avrdude.

#### VARIANT

Board variant.

#### VARIANT_DIR

Directory for the above variant.

#### CORE

Core name for this board; always "arduino".

#### CORE_DIR

Directory of the core library for this board.

#### BUILD_DIR

The directory to build in, by default `build/$BOARD`.

#### AVRDUDE

The avrdude binary to use.

#### AVRDUDEFLAGS

Flags to pass to avrdude.

#### AVRDUDECMD

The full avrdude command line.

#### UPLOAD_PROTOCOL

The upload protocol to use with avrdude.

#### UPLOAD_SPEED

Upload speed for this board.

#### UPLOAD_PORT

USB port to upload to, by default `/dev/ttyUSB0`.

### Standard Variables

The following variables have their standard meanings, and are set by `env.ConfigureBoard`:

- [CC](http://www.scons.org/doc/production/HTML/scons-user/a4916.html#cv-CC)
- [CCFLAGS](http://www.scons.org/doc/production/HTML/scons-user/a4916.html#cv-CCFLAGS)
- [CFLAGS](http://www.scons.org/doc/production/HTML/scons-user/a4916.html#cv-CFLAGS)
- [CPPPATH](http://www.scons.org/doc/production/HTML/scons-user/a4916.html#cv-CPPPATH)
- [CXX](http://www.scons.org/doc/production/HTML/scons-user/a4916.html#cv-CXX)
- [LINKFLAGS](http://www.scons.org/doc/production/HTML/scons-user/a4916.html#cv-LINKFLAGS)

About
=====

MIT licensed; see `LICENSE`.

