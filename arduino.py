from SCons.Script import *
import os
from os.path import join

def exists(env):
    return 1

def generate(env):
    original_env = env
    
    def read_boards_file(f):
        """Read board info from an arduino config file."""
        boards = {}
        
        for line in f:
            if line.strip() and line.strip()[0] != "#":
                key, value = line.strip().split("=", 1)
                boards[tuple(key.split("."))] = value
        
        return boards
    
    @env.AddMethod
    def ConfigureBoard(env, board):
        """Configure this environment for the given board name. Available boards
        are listed in $ARDUINO_HOME/hardware/arduino/boards.txt
        """
        env.SetDefault(
            ARDUINO_HOME = os.environ.get("ARDUINO_HOME", "/usr/share/arduino"))
        
        # Read the boards file.
        try:
            with open(env.subst("$ARDUINO_HOME/hardware/arduino/boards.txt")) as f:
                boards = read_boards_file(f)
        except IOError, e:
            raise Exception(env.subst(
                "ARDUINO_HOME ($ARDUINO_HOME) is not a valid arduino installation."))
        
        # Sensible defaults for variables that aren't defined by default.
        env.SetDefault(
            BOARD       = board,
            F_CPU       = boards[(board, "build", "f_cpu")],
            MCU         = boards[(board, "build", "mcu")],
            VARIANT     = boards[(board, "build", "variant")],
            VARIANT_DIR = "$ARDUINO_HOME/hardware/arduino/variants/$VARIANT",
            CORE        = boards[(board, "build", "core")],
            CORE_DIR    = "$ARDUINO_HOME/hardware/arduino/cores/$CORE",
            AVRDUDE     = "avrdude",
            AVRDUDEFLAGS = "-V -F -c $UPLOAD_PROTOCOL -b $UPLOAD_SPEED "
                           "-p $MCU -P $UPLOAD_PORT".split(),
            AVRDUDECMD = "$AVRDUDE $AVRDUDEFLAGS -U flash:w:$SOURCES",
            UPLOAD_PROTOCOL = boards[(board, "upload", "protocol")],
            UPLOAD_SPEED = boards[(board, "upload", "speed")],
            UPLOAD_PORT = "/dev/ttyUSB0")
        
        # Update variables defined by scons.
        env.Append(
            CCFLAGS = "-ffunction-sections -fdata-sections -fno-exceptions "
                      "-funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums "
                      "-Os -mmcu=$MCU -DARDUINO=100 -DF_CPU=$F_CPU".split(),
            LINKFLAGS = "-mmcu=$MCU -Os -Wl,--gc-sections -lm".split(),
            CFLAGS = "-std=gnu99".split())
        
        # Set binaries to use.
        env.Replace(CC = "avr-gcc", CXX = "avr-g++", LD = "avr-ld",
                    OBJCOPY = "avr-objcopy", AVRDUDE = "avrdude")
        
        # Set up the variant dir for this board.
        env.VariantDir("build/$BOARD/variant", "$VARIANT_DIR")
        env.Append(CPPPATH = ["build/$BOARD/variant"])
        
        return env
    
    @env.AddMethod
    def ArduinoCore(env):
        """Build the arduino core library."""
        env.VariantDir("build/$BOARD/core", "$CORE_DIR")
        env.Append(CPPPATH = ["build/$BOARD/core"])
        return env.Clone().Library("build/$BOARD/core", cxxfiles(env, "build/$BOARD/core"))
    
    def cxxfiles(env, path):
        """Get all c and cpp files in path."""
        return env.Glob(join(path, "**.c")) + env.Glob(join(path, "**.cpp"))
    
    @env.AddMethod
    def ArduinoLibrary(env, name, path=None):
        """Build a library. If path is not given, it is assumed to be a builtin
        arduino library. This adds the path to the inclide path, and builds all c
        and cpp files from path and path/utility into a library.
        """
        full_name = join("build/$BOARD", name)
        path = path or join(env.subst("$ARDUINO_HOME/libraries"), name)
        env.VariantDir(full_name, path)
        env.Append(CPPPATH = full_name)
        
        # Only add the utility directory to the include path while building this library.
        lib_env = env.Clone()
        lib_env.Append(CPPPATH = join(full_name, "utility"))
        return lib_env.Library(full_name, cxxfiles(env, full_name))
    
    @env.AddMethod
    def Sketch(env, name, sources):
        """Build a program from sources, and copy the resulting elf file into a hex
        file for uploading.
        """
        elf = env.Program(name, sources, PROGSUFFIX=".elf")
        return env.Hex(name, elf)
    
    @env.AddMethod
    def Upload(env, source, name="upload"):
        """Add an alias that uploads a given sketch to the arduino connected to
        $UPLOAD_PORT. The alias is by default called 'upload', which must be
        overloaded using the name parameter when defining multiple upload targets.
        """
        def reset(target, source, env):
            """Reset the arduino connected to $UPLOAD_PORT."""
            print "Resetting %s" % env["UPLOAD_PORT"]
            import serial
            import time
            try:
                with serial.Serial(env["UPLOAD_PORT"]) as ser:
                    ser.setDTR(1)
                    time.sleep(0.5)
                    ser.setDTR(0)
            except serial.SerialException, e:
                return str(e)
        
        target = env.Alias(name, source, [reset, "$AVRDUDECMD"])
        AlwaysBuild(target)
        # Hack: The top level environment (that the tools were installed into)
        # knows about all upload aliases, since we usually call this in a
        # cloned environment.
        original_env.Append(ALL_UPLOADS = target)
        env.AppendUnique(ALL_UPLOADS = target)
        return target
    
    @env.AddMethod
    def UploadAll(env, name="upload"):
        """Add an alias that runs all previously defined upload targets with a
        given name."""
        return env.Alias(name, env["ALL_UPLOADS"])
    
    # Use objcopy to build a hex file from an elf file.
    hex_builder = Builder(action="$OBJCOPY -O ihex -R .eeprom $SOURCES $TARGET",
                          suffix=".hex")
    env.Append(BUILDERS = dict(Hex = hex_builder))
