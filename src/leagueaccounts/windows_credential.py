"""
Direct Windows Credential Manager access via ctypes.
No third-party dependencies — works in both dev and PyInstaller exe.
"""
import ctypes
import ctypes.wintypes

advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)

CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2


class _FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', ctypes.wintypes.DWORD),
                ('dwHighDateTime', ctypes.wintypes.DWORD)]


class _CREDENTIAL_ATTRIBUTE(ctypes.Structure):
    _fields_ = [('Keyword', ctypes.wintypes.LPWSTR),
                ('Flags', ctypes.wintypes.DWORD),
                ('ValueSize', ctypes.wintypes.DWORD),
                ('Value', ctypes.POINTER(ctypes.c_byte))]


class _CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', ctypes.wintypes.DWORD),
        ('Type', ctypes.wintypes.DWORD),
        ('TargetName', ctypes.wintypes.LPWSTR),
        ('Comment', ctypes.wintypes.LPWSTR),
        ('LastWritten', _FILETIME),
        ('CredentialBlobSize', ctypes.wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', ctypes.wintypes.DWORD),
        ('AttributeCount', ctypes.wintypes.DWORD),
        ('Attributes', ctypes.POINTER(_CREDENTIAL_ATTRIBUTE)),
        ('TargetAlias', ctypes.wintypes.LPWSTR),
        ('UserName', ctypes.wintypes.LPWSTR),
    ]


def _target_name(service, username):
    return f'{username}@{service}'


def get_password(service, username):
    target = _target_name(service, username)
    cred_ptr = ctypes.POINTER(_CREDENTIAL)()
    if not advapi32.CredReadW(target, CRED_TYPE_GENERIC, 0, ctypes.byref(cred_ptr)):
        return None
    try:
        blob = cred_ptr.contents.CredentialBlob
        size = cred_ptr.contents.CredentialBlobSize
        raw = bytes(blob[i] for i in range(size))
        return raw.decode('utf-16-le')
    finally:
        advapi32.CredFree(cred_ptr)


def set_password(service, username, password):
    target = _target_name(service, username)
    blob = password.encode('utf-16-le')
    blob_type = ctypes.c_byte * len(blob)
    cred = _CREDENTIAL(
        Type=CRED_TYPE_GENERIC,
        TargetName=target,
        UserName=username,
        CredentialBlobSize=len(blob),
        CredentialBlob=blob_type(*blob),
        Persist=CRED_PERSIST_LOCAL_MACHINE,
    )
    if not advapi32.CredWriteW(ctypes.byref(cred), 0):
        raise ctypes.WinError(ctypes.get_last_error())


def delete_password(service, username):
    target = _target_name(service, username)
    advapi32.CredDeleteW(target, CRED_TYPE_GENERIC, 0)
