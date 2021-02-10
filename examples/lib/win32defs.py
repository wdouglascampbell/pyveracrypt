import ctypes
from ctypes import wintypes
import pywintypes
import win32file
import win32con
import winioctlcon

ERROR_FILE_NOT_FOUND = 2
ERROR_NO_MORE_FILES = 18

class GUID(ctypes.Structure):
    _fields_ = (
        ('Data1', ctypes.c_ulong),
        ('Data2', ctypes.c_ushort),
        ('Data3', ctypes.c_ushort),
        ('Data4', ctypes.c_ubyte * 8))

class PARTITION_INFORMATION_MBR(ctypes.Structure):
    _fields_ = (
        ('PartitionType', ctypes.c_char),
        ('BootIndicator', ctypes.c_int),
        ('RecognizedPartition', ctypes.c_int),
        ('HiddenSectors', ctypes.c_long),
        ('PartitionId', GUID))

class PARTITION_INFORMATION_GPT(ctypes.Structure):
    _fields_ = (
        ('PartitionType', GUID),
        ('PartitionId', GUID),
        ('Attributes', ctypes.c_ulonglong),
        ('Name', ctypes.c_wchar * 36))

class DUMMYUNIONNAME(ctypes.Union):
    _fields_ = (
        ('Mbr', PARTITION_INFORMATION_MBR),
        ('Gpt', PARTITION_INFORMATION_GPT))
                
class PARTITION_INFORMATION_EX(ctypes.Structure):
    _fields_ = (
        ('PartitionStyle', ctypes.c_uint),
        ('StartingOffset', ctypes.c_longlong),
        ('PartitionLength', ctypes.c_longlong),
        ('PartitionNumber', ctypes.c_ulong),
        ('RewritePartition', ctypes.c_byte),
        ('IsServicePartition', ctypes.c_byte),
        ('PartitionInformation', DUMMYUNIONNAME))

class DISK_EXTENT(ctypes.Structure):
    _fields_ = (
                ('DiskNumber', ctypes.c_ulong),
                ('StartingOffset', ctypes.c_longlong),
                ('ExtentLength', ctypes.c_longlong))

"""
# Doug's Original Version
ANYSIZE_ARRAY = 1

class VOLUME_DISK_EXTENTS(ctypes.Structure):
    _fields_ = (
                ('NumberOfDiskExtents', ctypes.c_ulong),
                ('Extents', DISK_EXTENT * ANYSIZE_ARRAY))
"""


ANYSIZE_ARRAY = 1

class VOLUME_DISK_EXTENTS(ctypes.Structure):
    _fields_ = (('NumberOfDiskExtents', ctypes.c_ulong),
                ('_Extents', DISK_EXTENT * ANYSIZE_ARRAY))

    @property
    def Extents(self):
        offset = type(self)._Extents.offset
        array_t = DISK_EXTENT * self.NumberOfDiskExtents
        return array_t.from_buffer(self, offset)

    def resize(self):
        if self.NumberOfDiskExtents < 1:
            self.NumberOfDiskExtents = 1
        offset = type(self)._Extents.offset
        array_size = ctypes.sizeof(DISK_EXTENT) * self.NumberOfDiskExtents
        ctypes.resize(self, offset + array_size)

def get_partition_disk_offset(diskNumber, partitionNumber):
    offset = None
    length = None

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.FindFirstVolumeW.restype = wintypes.HANDLE
    kernel32.FindNextVolumeW.argtypes = (wintypes.HANDLE,
                                         wintypes.LPWSTR,
                                         wintypes.DWORD)
    kernel32.FindVolumeClose.argtypes = (wintypes.HANDLE,)

    extents = VOLUME_DISK_EXTENTS()
    partition_information_ex = PARTITION_INFORMATION_EX()
    buf = ctypes.create_unicode_buffer(260)
    hfind = kernel32.FindFirstVolumeW(buf, len(buf))
    if hfind == win32file.INVALID_HANDLE_VALUE:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        while True:
            # Strip the trailing backslash that is appended to buf.
            # The trailing backslash is the mountpoint of the filesystem
            # that mounts the volume device, but we only want the GUID
            # device name.
            try:
                hVolume = win32file.CreateFile(buf.value[:-1], 0, 0, None,
                    win32con.OPEN_EXISTING, 0,  None)

                try:
                    win32file.DeviceIoControl(
                        hVolume, winioctlcon.IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS,
                        None, extents, None)
                    
                    try:
                        win32file.DeviceIoControl(hVolume,winioctlcon.IOCTL_DISK_GET_PARTITION_INFO_EX, None, partition_information_ex, None)
                        if extents.Extents[0].DiskNumber == diskNumber and partition_information_ex.PartitionNumber == long(partitionNumber):
                            offset = partition_information_ex.StartingOffset
                            length = partition_information_ex.PartitionLength
                            break
                    except pywintypes.error as e:
                        # This is unlikely to occur since rarely do people use
                        # more than one disk in a volume.
                        if e[0] == wintypes.ERROR_MORE_DATA:
                            partition_information_ex.resize()
                            win32file.DeviceIoControl(hVolume,winioctlcon.IOCTL_DISK_GET_PARTITION_INFO_EX, None, partition_information_ex, None)
                            if extents.Extents[0].DiskNumber == int(diskNumber) and partition_information_ex.PartitionNumber == partitionNumber:
                                offset = partition_information_ex.StartingOffset
                                length = partition_information_ex.ExtentLength
                                break
                        else:
                            raise ctypes.WinError(e[0])
                except pywintypes.error as e:
                    # Volumes like a VeraCrypt volume or a CDROM do not have
                    # disk extents.
                    pass
            except pywintypes.error as e:
                # This usually occurs when the GUID device name refers to a
                # volume that no longer exists. For example, a VeraCrypt
                # volume that has been unmounted.
                if e[0] != ERROR_FILE_NOT_FOUND:
                    raise ctypes.WinError(e[0])
                pass
            
            if not kernel32.FindNextVolumeW(hfind, buf, len(buf)):
                error = ctypes.get_last_error()
                if error != ERROR_NO_MORE_FILES:
                    raise ctypes.WinError(error)
                break
    finally:
        kernel32.FindVolumeClose(hfind)

    return offset, length
