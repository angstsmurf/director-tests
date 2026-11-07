
Build Instructions
==================

Building this DLL requires a DOS/Windows 3.1 environment. DOSBox is recommended.

Install Director for Windows 4.0.4 and Microsoft Visual C++ 1.52.

Copy this folder into the C:\DIRECTOR\XOBJDEV directory.

From a DOS prompt, run the following: 

C:\MSVC\BIN\MSVCVARS.BAT
cd C:\DIRECTOR\XOBJDEV\UNITTEST
nmake

This will produce an XObject file, UNITTEST.DLL.


Building with Open Watcom
-------------------------

The DLL can also be built on a modern host with Open Watcom v2, which
includes a 16-bit Windows target. With WATCOM set to the install directory
and the matching binary directory (e.g. binl64, binnt64 or armo64) on PATH:

::

    export INCLUDE=$WATCOM/h/win:$WATCOM/h
    wcc -bt=windows -zW -ml -bd -zu -ox -s -w3 -i=<Director>/XOBJDEV/INCLUDE \
        -dMSW -d_WINDOWS -d_WINDLL UNITTEST.C -fo=unittest.obj
    wrc -r -bt=windows UNITTEST.RC -fo=unittest.res
    wlink @$WATCOM/<bindir>/wlink.lnk @unittest.lnk

where unittest.lnk contains:

::

    system windows_dll initinstance memory
    name UNITTEST.DLL
    file unittest.obj
    option description 'ScummVM UnitTest XObject'
    option modname=UNITTEST
    option heapsize=1024
    option resource=unittest.res
    export _UNITTEST_MNEW.3, _UNITTEST_MDISPOSE.4, _UNITTEST_MISREALDIRECTOR.5, _UNITTEST_MSCREENSHOT.6, _UNITTEST_MMOVEMOUSE.7, _UNITTEST_MLEFTMOUSEDOWN.8, _UNITTEST_MLEFTMOUSEUP.9, _UNITTEST_MKEYPRESS.10

The XObject.h header is the one shipped in Director 4's XOBJDEV/INCLUDE.
