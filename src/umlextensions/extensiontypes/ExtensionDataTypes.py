
from typing import NewType

ExtensionName        = NewType('ExtensionName', str)
FormatName           = NewType('FormatName', str)
FileSuffix           = NewType('FileSuffix', str)
ExtensionDescription = NewType('ExtensionDescription', str)

Author  = NewType('Author', str)
Version = NewType('Version', str)

UNSPECIFIED_NAME:        FormatName           = FormatName('Unspecified Extension Name')
UNSPECIFIED_FILE_SUFFIX: FileSuffix           = FileSuffix('*')
UNSPECIFIED_DESCRIPTION: ExtensionDescription = ExtensionDescription('Unspecified Extension Description')
