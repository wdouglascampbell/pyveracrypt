import ctypes
import win32file
import winioctlcon

def VC_IOCTL(CODE):
    return winioctlcon.CTL_CODE(winioctlcon.FILE_DEVICE_UNKNOWN,
            0x800 + CODE, winioctlcon.METHOD_BUFFERED,
            winioctlcon.FILE_ANY_ACCESS)

VC_IOCTL_GET_MOUNTED_VOLUMES = VC_IOCTL(6)
VC_IOCTL_GET_VOLUME_PROPERTIES = VC_IOCTL(7)
VC_IOCTL_GET_BOOT_ENCRYPTION_STATUS = VC_IOCTL(18)
VC_IOCTL_GET_BOOT_DRIVE_VOLUME_PROPERTIES = VC_IOCTL(22)
VC_IOCTL_EMERGENCY_CLEAR_KEYS = VC_IOCTL(41)

PROP_VOL_TYPE_NORMAL = 0
PROP_VOL_TYPE_HIDDEN = 1
PROP_VOL_TYPE_OUTER = 2                      # Outer/normal (hidden volume protected)
PROP_VOL_TYPE_OUTER_VOL_WRITE_PREVENTED = 3  # Outer/normal (hidden volume protected AND write already prevented)
PROP_VOL_TYPE_SYSTEM = 4
PROP_NBR_VOLUME_TYPES = 5

SYSENC_FULL = 0
SYSENC_PARTIAL = 1
SYSENC_NONE = 2

MAX_PATH = 260
VOLUME_LABEL_LENGTH = 33 # 32 + null
VOLUME_ID_SIZE = 32
VERACRYPT_DRIVER_STR = r'\\.\VeraCrypt'

class BootEncryptionStatus(ctypes.Structure):
    _pack_ = 1
    _fields_ = (
        ('DeviceFilterActive', ctypes.c_int),
        ('BootLoaderVersion', ctypes.c_ushort),
        ('DriveMounted', ctypes.c_int),
        ('VolumeHeaderPresent', ctypes.c_int),
        ('DriveEncrypted', ctypes.c_int),
        ('BootDriveLength', ctypes.c_longlong),
        ('ConfiguredEncryptedAreaStart', ctypes.c_int64),
        ('ConfiguredEncryptedAreaEnd', ctypes.c_int64),
        ('EncryptedAreaStart', ctypes.c_int64),
        ('EncryptedAreaEnd', ctypes.c_int64),
        ('VolumeHeaderSaltCrc32', ctypes.c_uint),
        ('SetupInProgress', ctypes.c_int),
        ('SetupMode', ctypes.c_uint),
        ('TransformWaitingForIdle', ctypes.c_int),
        ('HibernationPreventionCount', ctypes.c_uint),
        ('HiddenSystem', ctypes.c_int),
        ('HiddenSystemPartitionStart', ctypes.c_int64),
        ('HiddenSysLeakProtectionCount', ctypes.c_uint))

class MOUNT_LIST_STRUCT(ctypes.Structure):
    _pack_ = 1
    _fields_ = (
        ('ulMountedDrives', ctypes.c_uint32),        # Bitfield of all mounted drive letters
        ('wszVolume', ctypes.c_wchar * 260 * 26),    # Volume names of mounted volumes
        ('wszLabel', ctypes.c_wchar * 33 * 26),      # Labels of mounted volumes
        ('volumeID', ctypes.c_wchar * 32 * 26),      # IDs of mounted volumes
        ('diskLength', ctypes.c_uint64 * 26),
        ('ea', ctypes.c_int * 26),
        ('volumeType', ctypes.c_int * 26),           # Volume type (e.g. PROP_VOL_TYPE_OUTER, PROP_VOL_TYPE_OUTER_VOL_WRITE_PREVENTED, etc.)
        ('truecryptMode', ctypes.c_int * 26))

class VOLUME_PROPERTIES_STRUCT(ctypes.Structure):
    _pack_ = 1
    _fields_ = (
        ('driveNo', ctypes.c_int),
        ('uniqueId', ctypes.c_int),
        ('wszVolume', ctypes.c_wchar * MAX_PATH),
        ('diskLength', ctypes.c_uint64),
        ('ea', ctypes.c_int),
        ('mode', ctypes.c_int),
        ('pkcs5', ctypes.c_int),
        ('pkcs5Iterations', ctypes.c_int),
        ('hiddenVolume', ctypes.c_int),
        ('readOnly', ctypes.c_int),
        ('removable', ctypes.c_int),
        ('partitionInInactiveSysEncScope', ctypes.c_int),
        ('volFormatVersion', ctypes.c_uint32),
        ('totalBytesRead', ctypes.c_uint64),
        ('totalBytesWritten', ctypes.c_uint64),
        ('hiddenVolProtection', ctypes.c_int),
        ('volFormatVersion', ctypes.c_int),
        ('volumePim', ctypes.c_int),
        ('wszLabel', ctypes.c_wchar * VOLUME_LABEL_LENGTH),
        ('bDriverSetLabel', ctypes.c_int),
        ('volumeID', ctypes.c_char * VOLUME_ID_SIZE),
        ('mountDisabled', ctypes.c_int))

def ListVeraCryptMounts():
    mlist = MOUNT_LIST_STRUCT()

    hDevice = win32file.CreateFile(VERACRYPT_DRIVER_STR, 0, 0, None,
        win32file.OPEN_EXISTING, 0, None)

    try:
        win32file.DeviceIoControl(hDevice,
            VC_IOCTL_GET_MOUNTED_VOLUMES, None, mlist)
    finally:
        hDevice.close()

    return mlist

def GetVeraCryptVolumeProperties(driveNo):
    prop = VOLUME_PROPERTIES_STRUCT(driveNo = driveNo)

    hDevice = win32file.CreateFile(VERACRYPT_DRIVER_STR, 0, 0, None,
        win32file.OPEN_EXISTING, 0, None)
    try:
        win32file.DeviceIoControl(hDevice,
            VC_IOCTL_GET_VOLUME_PROPERTIES, prop, prop)
    except pywintypes.error as e:
        print "Call to VeraCrypt driver (GET_VOLUME_PROPERTIES) failed with error '%s'" % str(e[2])
    finally:
        hDevice.close()

    return prop

def GetSystemEncryptionState():
    status = BootEncryptionStatus()

    hDevice = win32file.CreateFile(VERACRYPT_DRIVER_STR, 0, 0, None,
        win32file.OPEN_EXISTING, 0, None)
    try:
        win32file.DeviceIoControl(hDevice,
            VC_IOCTL_GET_BOOT_ENCRYPTION_STATUS, None, status)
    except pywintypes.error as e:
        print "Call to VeraCrypt driver (GET_BOOT_ENCRYPTION_STATUS) failed with error '%s'" % str(e[2])
    finally:
        hDevice.close()

    if status.DriveMounted or status.DriveEncrypted:
        if (not status.SetupInProgress
                and status.ConfiguredEncryptedAreaEnd != 0
                and status.ConfiguredEncryptedAreaEnd != -1
                and status.ConfiguredEncryptedAreaStart == status.EncryptedAreaStart
                and status.ConfiguredEncryptedAreaEnd == status.EncryptedAreaEnd):
            return SYSENC_FULL

        if (status.EncryptedAreaEnd < 0
                or status.EncryptedAreaStart < 0
                or status.EncryptedAreaEnd <= status.EncryptedAreaStart):
            return SYSENC_NONE

        return SYSENC_PARTIAL
    else:
        return SYSENC_NONE



