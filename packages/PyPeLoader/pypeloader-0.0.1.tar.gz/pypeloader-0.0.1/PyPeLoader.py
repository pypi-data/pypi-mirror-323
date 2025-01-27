#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements a basic PE loader in python (can load simple
#    executable like calc.exe, net1.exe, little malwares...)
#    Copyright (C) 2025  PyPeLoader

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements a basic PE loader in python (can load simple
executable like calc.exe, net1.exe, little malwares...)
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements a basic PE loader in python (can load simple
executable like calc.exe, net1.exe, little malwares...)
"""
__url__ = "https://github.com/mauricelambert/PyPeLoader"

__all__ = [
    "main",
    "load",
    "load_headers",
    "load_in_memory",
    "load_imports",
    "load_relocations",
]

__license__ = "GPL-3.0 License"
__copyright__ = """
PyPeLoader  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from typing import Union, Tuple, Iterable
from sys import argv, executable, exit
from dataclasses import dataclass
from _io import _BufferedIOBase
from ctypes import wintypes
import ctypes


class IMAGE_DOS_HEADER(ctypes.Structure):
    _fields_ = [
        ("e_magic", ctypes.c_uint16),
        ("e_cblp", ctypes.c_uint16),
        ("e_cp", ctypes.c_uint16),
        ("e_crlc", ctypes.c_uint16),
        ("e_cparhdr", ctypes.c_uint16),
        ("e_minalloc", ctypes.c_uint16),
        ("e_maxalloc", ctypes.c_uint16),
        ("e_ss", ctypes.c_uint16),
        ("e_sp", ctypes.c_uint16),
        ("e_csum", ctypes.c_uint16),
        ("e_ip", ctypes.c_uint16),
        ("e_cs", ctypes.c_uint16),
        ("e_lfarlc", ctypes.c_uint16),
        ("e_ovno", ctypes.c_uint16),
        ("e_res", ctypes.c_uint16 * 4),
        ("e_oemid", ctypes.c_uint16),
        ("e_oeminfo", ctypes.c_uint16),
        ("e_res2", ctypes.c_uint16 * 10),
        ("e_lfanew", ctypes.c_uint32),
    ]


class IMAGE_FILE_HEADER(ctypes.Structure):
    _fields_ = [
        ("Machine", ctypes.c_uint16),
        ("NumberOfSections", ctypes.c_uint16),
        ("TimeDateStamp", ctypes.c_uint32),
        ("PointerToSymbolTable", ctypes.c_uint32),
        ("NumberOfSymbols", ctypes.c_uint32),
        ("SizeOfOptionalHeader", ctypes.c_uint16),
        ("Characteristics", ctypes.c_uint16),
    ]


class IMAGE_DATA_DIRECTORY(ctypes.Structure):
    _fields_ = [("VirtualAddress", ctypes.c_uint32), ("Size", ctypes.c_uint32)]


class IMAGE_OPTIONAL_HEADER32(ctypes.Structure):
    _fields_ = [
        ("Magic", ctypes.c_uint16),
        ("MajorLinkerVersion", ctypes.c_uint8),
        ("MinorLinkerVersion", ctypes.c_uint8),
        ("SizeOfCode", ctypes.c_uint32),
        ("SizeOfInitializedData", ctypes.c_uint32),
        ("SizeOfUninitializedData", ctypes.c_uint32),
        ("AddressOfEntryPoint", ctypes.c_uint32),
        ("BaseOfCode", ctypes.c_uint32),
        ("BaseOfData", ctypes.c_uint32),
        ("ImageBase", ctypes.c_uint32),
        ("SectionAlignment", ctypes.c_uint32),
        ("FileAlignment", ctypes.c_uint32),
        ("MajorOperatingSystemVersion", ctypes.c_uint16),
        ("MinorOperatingSystemVersion", ctypes.c_uint16),
        ("MajorImageVersion", ctypes.c_uint16),
        ("MinorImageVersion", ctypes.c_uint16),
        ("MajorSubsystemVersion", ctypes.c_uint16),
        ("MinorSubsystemVersion", ctypes.c_uint16),
        ("Win32VersionValue", ctypes.c_uint32),
        ("SizeOfImage", ctypes.c_uint32),
        ("SizeOfHeaders", ctypes.c_uint32),
        ("CheckSum", ctypes.c_uint32),
        ("Subsystem", ctypes.c_uint16),
        ("DllCharacteristics", ctypes.c_uint16),
        ("SizeOfStackReserve", ctypes.c_uint32),
        ("SizeOfStackCommit", ctypes.c_uint32),
        ("SizeOfHeapReserve", ctypes.c_uint32),
        ("SizeOfHeapCommit", ctypes.c_uint32),
        ("LoaderFlags", ctypes.c_uint32),
        ("NumberOfRvaAndSizes", ctypes.c_uint32),
        ("DataDirectory", IMAGE_DATA_DIRECTORY * 16),
    ]


class IMAGE_OPTIONAL_HEADER64(ctypes.Structure):
    _fields_ = [
        ("Magic", ctypes.c_uint16),
        ("MajorLinkerVersion", ctypes.c_uint8),
        ("MinorLinkerVersion", ctypes.c_uint8),
        ("SizeOfCode", ctypes.c_uint32),
        ("SizeOfInitializedData", ctypes.c_uint32),
        ("SizeOfUninitializedData", ctypes.c_uint32),
        ("AddressOfEntryPoint", ctypes.c_uint32),
        ("BaseOfCode", ctypes.c_uint32),
        ("ImageBase", ctypes.c_uint64),
        ("SectionAlignment", ctypes.c_uint32),
        ("FileAlignment", ctypes.c_uint32),
        ("MajorOperatingSystemVersion", ctypes.c_uint16),
        ("MinorOperatingSystemVersion", ctypes.c_uint16),
        ("MajorImageVersion", ctypes.c_uint16),
        ("MinorImageVersion", ctypes.c_uint16),
        ("MajorSubsystemVersion", ctypes.c_uint16),
        ("MinorSubsystemVersion", ctypes.c_uint16),
        ("Win32VersionValue", ctypes.c_uint32),
        ("SizeOfImage", ctypes.c_uint32),
        ("SizeOfHeaders", ctypes.c_uint32),
        ("CheckSum", ctypes.c_uint32),
        ("Subsystem", ctypes.c_uint16),
        ("DllCharacteristics", ctypes.c_uint16),
        ("SizeOfStackReserve", ctypes.c_uint64),
        ("SizeOfStackCommit", ctypes.c_uint64),
        ("SizeOfHeapReserve", ctypes.c_uint64),
        ("SizeOfHeapCommit", ctypes.c_uint64),
        ("LoaderFlags", ctypes.c_uint32),
        ("NumberOfRvaAndSizes", ctypes.c_uint32),
        ("DataDirectory", IMAGE_DATA_DIRECTORY * 16),
    ]


class IMAGE_NT_HEADERS(ctypes.Structure):
    _fields_ = [
        ("Signature", ctypes.c_uint32),
        ("FileHeader", IMAGE_FILE_HEADER),
        ("OptionalHeader", IMAGE_OPTIONAL_HEADER32),
    ]


class IMAGE_SECTION_HEADER(ctypes.Structure):
    _fields_ = [
        ("Name", ctypes.c_char * 8),
        ("Misc", ctypes.c_uint32),
        ("VirtualAddress", ctypes.c_uint32),
        ("SizeOfRawData", ctypes.c_uint32),
        ("PointerToRawData", ctypes.c_uint32),
        ("PointerToRelocations", ctypes.c_uint32),
        ("PointerToLinenumbers", ctypes.c_uint32),
        ("NumberOfRelocations", ctypes.c_uint16),
        ("NumberOfLinenumbers", ctypes.c_uint16),
        ("Characteristics", ctypes.c_uint32),
    ]


class IMAGE_IMPORT_DESCRIPTOR_MISC(ctypes.Union):
    _fields_ = [
        ("Characteristics", ctypes.c_uint32),
        ("OriginalFirstThunk", ctypes.c_uint32),
    ]


class IMAGE_IMPORT_DESCRIPTOR(ctypes.Structure):
    _fields_ = [
        ("Misc", IMAGE_IMPORT_DESCRIPTOR_MISC),
        ("TimeDateStamp", ctypes.c_uint32),
        ("ForwarderChain", ctypes.c_uint32),
        ("Name", ctypes.c_uint32),
        ("FirstThunk", ctypes.c_uint32),
    ]


class IMAGE_IMPORT_BY_NAME(ctypes.Structure):
    _fields_ = [("Hint", ctypes.c_uint16), ("Name", ctypes.c_char * 12)]


class IMAGE_THUNK_DATA_UNION64(ctypes.Union):
    _fields_ = [
        ("Function", ctypes.POINTER(ctypes.c_uint32)),
        ("Ordinal", ctypes.c_uint32),
        ("AddressOfData", ctypes.POINTER(IMAGE_IMPORT_BY_NAME)),
        ("ForwarderString", ctypes.c_uint32),
    ]


class IMAGE_THUNK_DATA_UNION32(ctypes.Union):
    _fields_ = [
        ("Function", ctypes.c_uint32),
        ("Ordinal", ctypes.c_uint32),
        ("AddressOfData", ctypes.c_uint32),
        ("ForwarderString", ctypes.c_uint32),
    ]


class IMAGE_THUNK_DATA64(ctypes.Structure):
    _fields_ = [("u1", IMAGE_THUNK_DATA_UNION64)]


class IMAGE_THUNK_DATA32(ctypes.Structure):
    _fields_ = [("u1", IMAGE_THUNK_DATA_UNION32)]


class IMAGE_BASE_RELOCATION(ctypes.Structure):
    _fields_ = [
        ("VirtualAddress", ctypes.c_uint32),
        ("SizeOfBlock", ctypes.c_uint32),
    ]


@dataclass
class PeHeaders:
    dos: IMAGE_DOS_HEADER
    nt: IMAGE_NT_HEADERS
    file: IMAGE_FILE_HEADER
    optional: Union[IMAGE_OPTIONAL_HEADER32, IMAGE_OPTIONAL_HEADER64]
    sections: IMAGE_SECTION_HEADER * 1
    arch: int


IMAGE_REL_BASED_ABSOLUTE = 0
IMAGE_REL_BASED_HIGH = 1
IMAGE_REL_BASED_LOW = 2
IMAGE_REL_BASED_HIGHLOW = 3
IMAGE_REL_BASED_HIGHADJ = 4
IMAGE_REL_BASED_MIPS_JMPADDR = 5
IMAGE_REL_BASED_ARM_MOV32 = 5
IMAGE_REL_BASED_RISCV_HIGH20 = 5
IMAGE_REL_BASED_THUMB_MOV32 = 7
IMAGE_REL_BASED_RISCV_LOW12I = 7
IMAGE_REL_BASED_RISCV_LOW12S = 8
IMAGE_REL_BASED_LOONGARCH32_MARK_LA = 8
IMAGE_REL_BASED_LOONGARCH64_MARK_LA = 8
IMAGE_REL_BASED_MIPS_JMPADDR16 = 9
IMAGE_REL_BASED_DIR64 = 10

IMAGE_DIRECTORY_ENTRY_IMPORT = 0x01
IMAGE_DIRECTORY_ENTRY_BASERELOC = 0x05

MEM_RESERVE = 0x2000
MEM_COMMIT = 0x1000

PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08

PAGE_GUARD = 0x100
PAGE_NOCACHE = 0x200
PAGE_WRITECOMBINE = 0x400

kernel32 = ctypes.windll.kernel32

VirtualAlloc = kernel32.VirtualAlloc
VirtualAlloc.restype = ctypes.c_void_p
VirtualAlloc.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_ulong,
    ctypes.c_ulong,
]

VirtualProtect = kernel32.VirtualProtect
VirtualProtect.restype = ctypes.c_bool
VirtualProtect.argtypes = [
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ulong),
]

LoadLibraryA = kernel32.LoadLibraryA
LoadLibraryA.restype = wintypes.HMODULE
LoadLibraryA.argtypes = [wintypes.LPCSTR]

GetProcAddress = kernel32.GetProcAddress
GetProcAddress.restype = ctypes.c_void_p
GetProcAddress.argtypes = [wintypes.HMODULE, wintypes.LPCSTR]


def load_struct_from_bytes(struct: type, data: bytes) -> ctypes.Structure:
    """
    This function returns a ctypes structure
    build from bytes sent in arguments.
    """

    instance = struct()
    ctypes.memmove(ctypes.pointer(instance), data, ctypes.sizeof(instance))
    return instance


def load_struct_from_file(
    struct: type, file: _BufferedIOBase
) -> ctypes.Structure:
    """
    This function returns a ctypes structure
    build from memory address sent in arguments.
    """

    return load_struct_from_bytes(struct, file.read(ctypes.sizeof(struct)))


def get_data_from_memory(position: int, size: int) -> bytes:
    """
    This function returns bytes from memory address and size.
    """

    buffer = (ctypes.c_byte * size)()
    ctypes.memmove(buffer, position, size)
    return bytes(buffer)


def read_array_structure_until_0(
    position: int, structure: type
) -> Iterable[Tuple[ctypes.Structure]]:
    """
    This function generator yields ctypes structures from memory
    until last element contains only NULL bytes.
    """

    size = ctypes.sizeof(structure)
    index = 0
    data = get_data_from_memory(position, size)
    while data != (b"\0" * size):
        instance = load_struct_from_bytes(structure, data)
        yield index, instance
        index += 1
        data = get_data_from_memory(position + index * size, size)


def load_headers(file: _BufferedIOBase) -> PeHeaders:
    """
    This function returns all PE headers structure from file.
    """

    dos_header = load_struct_from_file(IMAGE_DOS_HEADER, file)
    file.seek(dos_header.e_lfanew)
    nt_headers = load_struct_from_file(IMAGE_NT_HEADERS, file)
    file_header = nt_headers.FileHeader

    if file_header.Machine == 0x014C:  # IMAGE_FILE_MACHINE_I386
        optional_header = nt_headers.OptionalHeader
        arch = 32
    elif file_header.Machine == 0x8664:  # IMAGE_FILE_MACHINE_AMD64
        file.seek(ctypes.sizeof(IMAGE_OPTIONAL_HEADER32) * -1, 1)
        optional_header = load_struct_from_file(IMAGE_OPTIONAL_HEADER64, file)
        arch = 64

    section_headers = load_struct_from_file(
        (IMAGE_SECTION_HEADER * file_header.NumberOfSections), file
    )

    return PeHeaders(
        dos_header,
        nt_headers,
        file_header,
        optional_header,
        section_headers,
        arch,
    )


def load_in_memory(file: _BufferedIOBase, pe_headers: PeHeaders) -> int:
    """
    This function loads the PE program in memory
    using the file and all PE headers.
    """

    ImageBase = VirtualAlloc(
        None,
        pe_headers.optional.SizeOfImage,
        MEM_RESERVE | MEM_COMMIT,
        PAGE_READWRITE,
    )
    old_permissions = wintypes.DWORD(0)

    file.seek(0)
    ctypes.memmove(
        ImageBase,
        file.read(pe_headers.optional.SizeOfHeaders),
        pe_headers.optional.SizeOfHeaders,
    )
    result = VirtualProtect(
        ImageBase,
        pe_headers.optional.SizeOfHeaders,
        PAGE_READONLY,
        ctypes.byref(old_permissions),
    )

    for section in pe_headers.sections:
        position = ImageBase + section.VirtualAddress
        if section.SizeOfRawData > 0:
            file.seek(section.PointerToRawData)
            ctypes.memmove(
                position,
                file.read(section.SizeOfRawData),
                section.SizeOfRawData,
            )
        else:
            ctypes.memset(position, 0, section.Misc)

        if (
            section.Characteristics & 0xE0000000 == 0xE0000000
        ):  # IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ | IMAGE_SCN_MEM_WRITE
            new_permissions = PAGE_EXECUTE_READWRITE
        elif (
            section.Characteristics & 0x60000000 == 0x60000000
        ):  # IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ
            new_permissions = PAGE_EXECUTE_READ
        elif (
            section.Characteristics & 0xC0000000 == 0xC0000000
        ):  # IMAGE_SCN_MEM_READ | IMAGE_SCN_MEM_WRITE
            new_permissions = PAGE_READWRITE
        elif (
            section.Characteristics & 0x40000000 == 0x40000000
        ):  # IMAGE_SCN_MEM_READ
            new_permissions = PAGE_READONLY

        old_permissions = wintypes.DWORD(0)
        result = VirtualProtect(
            position,
            section.Misc,
            new_permissions,
            ctypes.byref(old_permissions),
        )

    return ImageBase


def get_functions(
    ImageBase: int, position: int, struct: type
) -> Iterable[Tuple[int, wintypes.LPCSTR]]:
    """
    This function loads the PE program in memory
    using the file and all PE headers.
    """

    size_import_name = ctypes.sizeof(IMAGE_IMPORT_BY_NAME)

    for index, thunk_data in read_array_structure_until_0(
        ImageBase + position, struct
    ):
        address = thunk_data.u1.Ordinal
        if not (address & 0x80000000):
            data = get_data_from_memory(ImageBase + address, size_import_name)
            import_by_name = load_struct_from_bytes(IMAGE_IMPORT_BY_NAME, data)
            address = ImageBase + address + IMAGE_IMPORT_BY_NAME.Name.offset
        yield index, wintypes.LPCSTR(address)


def load_imports(pe_headers: PeHeaders, ImageBase: int) -> None:
    """
    This function loads imports (DLL, libraries), finds the functions addresses
    and write them in the IAT (Import Address Table).
    """

    position = (
        ImageBase
        + pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT
        ].VirtualAddress
    )
    type_ = IMAGE_THUNK_DATA64 if pe_headers.arch == 64 else IMAGE_THUNK_DATA32
    size_thunk = ctypes.sizeof(type_)
    size_pointer = ctypes.sizeof(type_)

    for index, import_descriptor in read_array_structure_until_0(
        position, IMAGE_IMPORT_DESCRIPTOR
    ):
        module = LoadLibraryA(
            wintypes.LPCSTR(ImageBase + import_descriptor.Name)
        )
        if not module:
            raise ImportError(
                "Cannot load the library for import: " + str(index)
            )

        for counter, function in get_functions(
            ImageBase, import_descriptor.Misc.OriginalFirstThunk, type_
        ):
            address = GetProcAddress(module, function)
            function_position = (
                ImageBase + import_descriptor.FirstThunk + size_thunk * counter
            )
            old_permissions = wintypes.DWORD(0)
            result = VirtualProtect(
                function_position,
                size_pointer,
                PAGE_READWRITE,
                ctypes.byref(old_permissions),
            )
            ctypes.memmove(
                function_position,
                address.to_bytes(size_pointer, "little"),
                size_pointer,
            )
            result = VirtualProtect(
                function_position,
                size_pointer,
                old_permissions,
                ctypes.byref(old_permissions),
            )


def load_relocations(pe_headers: PeHeaders, ImageBase: int) -> None:
    """
    This function overwrites the relocations with the difference between image
    base in memory and image base in PE headers.
    """

    delta = ImageBase - pe_headers.optional.ImageBase
    if (
        not pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_BASERELOC
        ].VirtualAddress
        or not delta
    ):
        return None

    type_ = IMAGE_THUNK_DATA64 if pe_headers.arch == 64 else IMAGE_THUNK_DATA32
    size_pointer = ctypes.sizeof(type_)

    position = (
        ImageBase
        + pe_headers.optional.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_BASERELOC
        ].VirtualAddress
    )
    size = ctypes.sizeof(IMAGE_BASE_RELOCATION)
    data = get_data_from_memory(position, size)

    while data != (b"\0" * size):
        base_relocation = load_struct_from_bytes(IMAGE_BASE_RELOCATION, data)
        block_size = (
            base_relocation.SizeOfBlock - ctypes.sizeof(IMAGE_BASE_RELOCATION)
        ) // 2

        for reloc in (ctypes.c_uint16 * block_size).from_address(
            position + size
        ):
            type_ = reloc >> 12
            offset = reloc & 0x0FFF
            address = ImageBase + base_relocation.VirtualAddress + offset

            if (
                type_ == IMAGE_REL_BASED_HIGHLOW
                or type_ == IMAGE_REL_BASED_DIR64
            ):
                static_address = int.from_bytes(
                    get_data_from_memory(address, size_pointer), "little"
                )
                old_permissions = wintypes.DWORD(0)
                result = VirtualProtect(
                    address,
                    size_pointer,
                    PAGE_READWRITE,
                    ctypes.byref(old_permissions),
                )
                ctypes.memmove(
                    address,
                    (static_address + delta).to_bytes(size_pointer, "little"),
                    size_pointer,
                )
                result = VirtualProtect(
                    address,
                    size_pointer,
                    old_permissions,
                    ctypes.byref(old_permissions),
                )

        data = get_data_from_memory(
            position + base_relocation.SizeOfBlock, size
        )
        position += base_relocation.SizeOfBlock


def load(file: _BufferedIOBase) -> None:
    """
    This function does all steps to load and execute the PE program in memory.
    """

    pe_headers = load_headers(file)
    image_base = load_in_memory(file, pe_headers)
    file.close()

    load_imports(pe_headers, image_base)
    load_relocations(pe_headers, image_base)

    function_type = ctypes.CFUNCTYPE(ctypes.c_int)
    function = function_type(
        image_base + pe_headers.optional.AddressOfEntryPoint
    )
    function()


def main() -> int:
    """
    This is the main function to start the program from command line.
    """

    if len(argv) <= 1:
        print(
            'USAGES: "',
            executable,
            '" "',
            argv[0],
            '" <executables path...>',
            sep="",
        )
        return 1

    for path in argv[1:]:
        load(open(path, "rb"))

    return 0


if __name__ == "__main__":
    exit(main())
