import sys
from os.path import join

from SCons.Script import (
    COMMAND_LINE_TARGETS,
    AlwaysBuild,
    Builder,
    Default,
    DefaultEnvironment,
)


# resolve environment
env = DefaultEnvironment()
board = env.BoardConfig()
platform = env.PioPlatform()


# use arm-none-eabi-* binaries
env.Replace(
    AR="arm-none-eabi-gcc-ar",
    AS="arm-none-eabi-as",
    CC="arm-none-eabi-gcc",
    CXX="arm-none-eabi-g++",
    GDB="arm-none-eabi-gdb",
    OBJCOPY="arm-none-eabi-objcopy",
    RANLIB="arm-none-eabi-ranlib",
    SIZETOOL="arm-none-eabi-size",

    ARFLAGS=["rc"],
    
    SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
    SIZEPRINTCMD="$SIZETOOL -B -d $SOURCES",
    
    # note: size regexprs are defined in framework build, as they
    # depend on the linker script used

    PROGSUFFIX=".elf",

    UPLOADER=join("$PIOPACKAGES_DIR", "tool-bar", "uploader"),
    UPLOADCMD="$UPLOADER $SOURCES"
)

# configure builder
env.Append(
    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                "$OBJCOPY",
                "-O",
                "binary",
                "$SOURCES",
                "$TARGET"
            ]), "Building $TARGET"),
            suffix=".bin"
        )
    ),

    LINKFLAGS=[
        # don't care about RWX sections, we're running from flash anyway
        "-Wl,--no-warn-rwx-segment",
    ],
)


# # Allow user to override via pre:script
# if env.get("PROGNAME", "program") == "program":
#     env.Replace(PROGNAME="firmware")

# if not env.get("PIOFRAMEWORK"):
#     sys.stderr.write("Error: PIOFRAMEWORK is not defined")
#     env.Exit(1)


#
# Target: Build executable and linkable firmware
#
target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_firm = join("$BUILD_DIR", "${PROGNAME}.hex")
else:
    target_elf = env.BuildProgram()
    target_firm = env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    #env.Depends(target_firm, "checkprogsize") #todo checkprogsize

AlwaysBuild(env.Alias("nobuild", target_firm))
target_buildprog = env.Alias("buildprog", target_firm, target_firm)


#
# Target: Print binary size
#
target_size = env.AddPlatformTarget(
    "size",
    target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"),
    "Program Size",
    "Calculate program size",
)


#
# Target: Upload by default .bin file
#

upload_protocol = env.subst("$UPLOAD_PROTOCOL")
debug_tools = board.get("debug.tools", {})
upload_actions = []

if upload_protocol in debug_tools:
    # upload using pyOCD
    pyocd_target = board.get("debug.pyocd_target")
    assert pyocd_target, (
        f"Missed pyOCD target for upload to {board.id}"
    )

    offset_address = board.get("upload.offset_address", 0)
    if isinstance(offset_address, str):
        offset_address = int(offset_address, 16) if offset_address.startswith("0x") else int(offset_address)

    maximum_size = board.get("upload.maximum_size", 32 * 1024)

    assert isinstance(offset_address, int)
    assert isinstance(maximum_size, int)

    # if maximum_size > (4 * 1024):
    #     # flash size > 4K
    #     raise ValueError(f"Flash size {maximum_size} is too large for any HC32L110 target!")
    
    # get pyocd tool path
    pyocd_path = join(platform.get_package_dir("tool-pyocd"), "pyocd.py")

    # build upload command
    pyocd_load_cmd = " ".join([
        "$PYTHONEXE", pyocd_path,
        "load",
        "--no-wait",
        "--target", pyocd_target,
        "--base-address", f"0x{offset_address:x}",
        "$SOURCE"  
    ])

    upload_actions = [
        env.VerboseAction(pyocd_load_cmd, "Uploading $SOURCE")
    ]
elif upload_protocol == "custom":
    # custom upload tool
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]
else:
    sys.stderr.write(f"Warning! Unknown upload protocol {upload_protocol}!\n")

AlwaysBuild(env.Alias("upload", target_firm, upload_actions))


#
# Setup default targets
#
Default([target_buildprog, target_size])
