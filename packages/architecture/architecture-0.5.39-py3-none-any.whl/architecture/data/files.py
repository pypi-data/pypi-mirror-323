from __future__ import annotations

import base64
import hashlib
import logging
import mimetypes
import sys
from enum import Enum
from http.cookiejar import CookieJar
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    BinaryIO,
    Callable,
    Iterable,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypeAlias,
    overload,
)

import msgspec
import requests
from requests import Response
from requests.auth import AuthBase
from requests.models import PreparedRequest
from typing_extensions import Self

from architecture.log import create_logger
from architecture.utils.decorators import ensure_module_installed

if TYPE_CHECKING:
    from _typeshed import SupportsItems, SupportsRead
    from fastapi import UploadFile as FastAPIUploadFile
    from litestar.datastructures import UploadFile as LitestarUploadFile

    _TextMapping: TypeAlias = MutableMapping[str, str]
    _HeadersMapping: TypeAlias = Mapping[str, str | bytes | None]

    _Data: TypeAlias = (
        # used in requests.models.PreparedRequest.prepare_body
        #
        # case: is_stream
        # see requests.adapters.HTTPAdapter.send
        # will be sent directly to http.HTTPConnection.send(...) (through urllib3)
        Iterable[bytes]
        # case: not is_stream
        # will be modified before being sent to urllib3.HTTPConnectionPool.urlopen(body=...)
        # see requests.models.RequestEncodingMixin._encode_params
        # see requests.models.RequestEncodingMixin._encode_files
        # note that keys&values are converted from Any to str by urllib.parse.urlencode
        | str
        | bytes
        | SupportsRead[str | bytes]
        | list[tuple[Any, Any]]
        | tuple[tuple[Any, Any], ...]
        | Mapping[Any, Any]
    )

    _ParamsMappingKeyType: TypeAlias = str | bytes | int | float
    _ParamsMappingValueType: TypeAlias = (
        str | bytes | int | float | Iterable[str | bytes | int | float] | None
    )
    _Params: TypeAlias = (
        SupportsItems[_ParamsMappingKeyType, _ParamsMappingValueType]
        | tuple[_ParamsMappingKeyType, _ParamsMappingValueType]
        | Iterable[tuple[_ParamsMappingKeyType, _ParamsMappingValueType]]
        | str
        | bytes
    )
    _Verify: TypeAlias = bool | str
    _Timeout: TypeAlias = float | tuple[float, float] | tuple[float, None]
    _Cert: TypeAlias = str | tuple[str, str]
    Incomplete: TypeAlias = Any
    _Hook: TypeAlias = Callable[[Response], Any]
    _HooksInput: TypeAlias = Mapping[str, Iterable[_Hook] | _Hook]
    _FileContent: TypeAlias = SupportsRead[str | bytes] | str | bytes
    _FileName: TypeAlias = str | None
    _FileContentType: TypeAlias = str
    _FileSpecTuple2: TypeAlias = tuple[_FileName, _FileContent]
    _FileSpecTuple3: TypeAlias = tuple[_FileName, _FileContent, _FileContentType]
    _FileCustomHeaders: TypeAlias = Mapping[str, str]
    _FileSpecTuple4: TypeAlias = tuple[
        _FileName, _FileContent, _FileContentType, _FileCustomHeaders
    ]
    _FileSpec: TypeAlias = (
        _FileContent | _FileSpecTuple2 | _FileSpecTuple3 | _FileSpecTuple4
    )
    _Files: TypeAlias = Mapping[str, _FileSpec] | Iterable[tuple[str, _FileSpec]]
    _Auth: TypeAlias = (
        tuple[str, str] | AuthBase | Callable[[PreparedRequest], PreparedRequest]
    )

debug_logger = create_logger(__name__, level=logging.DEBUG)


def find_extension(
    *,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    contents: Optional[bytes] = None,
    url: Optional[str] = None,
) -> FileExtension:
    if filename and (ext := get_extension_from_filename(filename)):
        return ext
    if content_type and (ext := get_extension_from_content_type(content_type)):
        return ext
    if contents and (ext := get_extension_agressivelly(contents)):
        return ext
    if url and (ext := get_extension_from_url(url)):
        return ext

    raise ValueError("Unable to determine the file extension.")


def get_extension_from_url(url: str) -> Optional[FileExtension]:
    """Extracts the file extension from a URL."""
    from urllib.parse import urlparse

    parsed_url = urlparse(url)
    path = parsed_url.path
    if not path:
        return None
    name = path.split("/")[-1]
    if "." not in name:
        return None

    return get_extension_from_filename(name)


def get_extension_from_filename(filename: str) -> Optional[FileExtension]:
    ext = filename.split(".")[-1]
    return (
        FileExtension[ext.upper()] if ext.upper() in FileExtension.__members__ else None
    )


def get_extension_agressivelly(contents: bytes) -> Optional[FileExtension]:
    file_signatures: dict[bytes, FileExtension] = {
        b"\x89PNG\r\n\x1a\n": FileExtension.PNG,
        b"\xff\xd8\xff\xe0": FileExtension.JPEG,
        b"\xff\xd8\xff\xe1": FileExtension.JPG,
        b"\xff\xd8\xff\xe8": FileExtension.JPG,
        b"PK\x03\x04": FileExtension.ZIP,
        b"MZ": FileExtension.DOC,
        b"%PDF-": FileExtension.PDF,
        b"<!DOCTYPE HTML": FileExtension.HTML,
        b"{\\rtf1": FileExtension.DOC,
        b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1": FileExtension.DOC,
        b"Rar!": FileExtension.RAR,
        b"<?xml": FileExtension.XML,
        b"GIF87a": FileExtension.GIF,
        b"GIF89a": FileExtension.GIF,
        b"\x49\x49*\x00": FileExtension.TIFF,  # Little-endian TIFF
        b"\x4d\x4d\x00*": FileExtension.TIFF,  # Big-endian TIFF
        b"BM": FileExtension.BMP,
        b"PK\x01\x02": FileExtension.PKT,
        b"\x49\x44\x33": FileExtension.MP3,
        b"\x66\x74\x79\x70": FileExtension.MP4,
    }
    for signature, extension in file_signatures.items():
        if contents.startswith(signature):
            return extension
    return None


def get_extension_from_content_type(content_type: str) -> Optional[FileExtension]:
    content_type_map = {
        # Text types
        "text/plain": FileExtension.TXT,
        "text/html": FileExtension.HTML,
        "text/css": FileExtension.CSS,
        "text/csv": FileExtension.CSV,
        "text/calendar": FileExtension.ICS,
        "text/javascript": FileExtension.JS,
        "text/markdown": FileExtension.MD,
        "text/vcard": FileExtension.VCF,
        "text/xml": FileExtension.XML,
        "text/x-vcard": FileExtension.VCF,
        # Application types
        "application/octet-stream": FileExtension.BIN,
        "application/json": FileExtension.JSON,
        "application/pdf": FileExtension.PDF,
        "application/zip": FileExtension.ZIP,
        "application/x-zip-compressed": FileExtension.ZIP,
        "application/x-rar-compressed": FileExtension.RAR,
        "application/x-tar": FileExtension.TAR,
        "application/x-bzip": FileExtension.BZ,
        "application/x-bzip2": FileExtension.BZ2,
        "application/x-7z-compressed": FileExtension.SEVENZ,
        "application/x-msdownload": FileExtension.EXE,
        "application/x-shockwave-flash": FileExtension.SWF,
        "application/xhtml+xml": FileExtension.XHTML,
        "application/xml": FileExtension.XML,
        "application/atom+xml": FileExtension.ATOM,
        "application/rss+xml": FileExtension.RSS,
        "application/x-latex": FileExtension.LATEX,
        "application/x-httpd-php": FileExtension.PHP,
        "application/postscript": FileExtension.PS,
        "application/sql": FileExtension.SQL,
        "application/x-dvi": FileExtension.DVI,
        "application/x-tex": FileExtension.TEX,
        "application/msword": FileExtension.DOC,
        "application/vnd.ms-excel": FileExtension.XLS,
        "application/vnd.ms-powerpoint": FileExtension.PPT,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileExtension.DOCX,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileExtension.XLSX,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileExtension.PPTX,
        "application/vnd.oasis.opendocument.text": FileExtension.ODT,
        "application/vnd.android.package-archive": FileExtension.APK,
        "application/java-archive": FileExtension.JAR,
        "application/x-debian-package": FileExtension.DEB,
        "application/x-redhat-package-manager": FileExtension.RPM,
        # Image types
        "image/jpeg": FileExtension.JPG,
        "image/png": FileExtension.PNG,
        "image/gif": FileExtension.GIF,
        "image/bmp": FileExtension.BMP,
        "image/tiff": FileExtension.TIFF,
        "image/svg+xml": FileExtension.SVG,
        "image/webp": FileExtension.WEBP,
        "image/x-icon": FileExtension.ICO,
        "image/vnd.djvu": FileExtension.DJVU,
        "image/x-ms-bmp": FileExtension.BMP,
        # Audio types
        "audio/mpeg": FileExtension.MP3,
        "audio/ogg": FileExtension.OGG,
        "audio/wav": FileExtension.WAV,
        "audio/webm": FileExtension.WEBA,
        "audio/aac": FileExtension.AAC,
        "audio/midi": FileExtension.MID,
        "audio/x-wav": FileExtension.WAV,
        "audio/x-aiff": FileExtension.AIFF,
        # Video types
        "video/mp4": FileExtension.MP4,
        "video/ogg": FileExtension.OGV,
        "video/webm": FileExtension.WEBM,
        "video/x-msvideo": FileExtension.AVI,
        "video/x-matroska": FileExtension.MKV,
        "video/quicktime": FileExtension.MOV,
        "video/x-ms-wmv": FileExtension.WMV,
        "video/x-flv": FileExtension.FLV,
        "video/3gpp": FileExtension.THREE_GP,
        # Font types
        "font/ttf": FileExtension.TTF,
        "font/otf": FileExtension.OTF,
        "font/woff": FileExtension.WOFF,
        "font/woff2": FileExtension.WOFF2,
        # Message types
        "message/rfc822": FileExtension.EML,
        "message/news": FileExtension.NWS,
        # Chemical/Model types
        "chemical/x-pdb": FileExtension.PDB,
        "chemical/x-xyz": FileExtension.XYZ,
        "model/3mf": FileExtension.THREE_MF,
        "model/obj": FileExtension.OBJ,
        "model/stl": FileExtension.STL,
        # Legacy/Obscure types
        "application/x-msmetafile": FileExtension.WMF,
        "application/x-msaccess": FileExtension.MDB,
        "application/x-csh": FileExtension.CSH,
        "application/x-sh": FileExtension.SH,
        "application/x-tcl": FileExtension.TCL,
        "application/x-texinfo": FileExtension.TE,
        "application/x-troff": FileExtension.TR,
        "application/x-wais-source": FileExtension.SRC,
        "application/x-bcpio": FileExtension.BCPIO,
        "application/x-cpio": FileExtension.CPIO,
        "application/x-gtar": FileExtension.GTAR,
        "application/x-hdf": FileExtension.HDF,
        "application/x-netcdf": FileExtension.NC,
        "application/x-shar": FileExtension.SHAR,
        "application/x-sv4cpio": FileExtension.SV4CPIO,
        "application/x-sv4crc": FileExtension.SV4CRC,
        "application/x-ustar": FileExtension.USTAR,
        "application/x-director": FileExtension.DCR,
        "application/x-envoy": FileExtension.EVY,
        "application/x-mif": FileExtension.MIF,
        "application/x-silverlight": FileExtension.SCR,
    }
    return content_type_map.get(content_type, None)


class FileExtension(str, Enum):
    PDF = "pdf"
    JSON = "json"
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    HTML = "html"
    TXT = "txt"
    MD = "md"
    ZIP = "zip"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    PPTX = "pptx"
    TIFF = "tiff"
    GIF = "gif"
    DWG = "dwg"
    ALG = "alg"
    DOC = "doc"
    PPT = "ppt"
    PKT = "pkt"
    PKZ = "pkz"
    RAR = "rar"
    XML = "xml"
    BMP = "bmp"
    TIF = "tif"
    PPTM = "pptm"
    XLS = "xls"
    MP3 = "mp3"
    FLAC = "flac"
    MP4 = "mp4"
    MPEG = "mpeg"
    MPGA = "mpga"
    M4A = "m4a"
    OGG = "ogg"
    WAV = "wav"
    WEBM = "webm"
    MOV = "mov"
    ICS = "ics"
    CSS = "css"
    JS = "js"
    VCF = "vcf"
    BIN = "bin"
    TAR = "tar"
    BZ = "bz"
    BZ2 = "bz2"
    SEVENZ = "7z"
    EXE = "exe"
    SWF = "swf"
    XHTML = "xhtml"
    ATOM = "atom"
    RSS = "rss"
    LATEX = "latex"
    PHP = "php"
    PS = "ps"
    SQL = "sql"
    DVI = "dvi"
    TEX = "tex"
    ODT = "odt"
    APK = "apk"
    JAR = "jar"
    DEB = "deb"
    RPM = "rpm"
    SVG = "svg"
    WEBP = "webp"
    ICO = "ico"
    DJVU = "djvu"
    WEBA = "weba"
    AAC = "aac"
    MID = "mid"
    AIFF = "aiff"
    OGV = "ogv"
    AVI = "avi"
    MKV = "mkv"
    WMV = "wmv"
    FLV = "flv"
    THREE_GP = "3gp"
    TTF = "ttf"
    OTF = "otf"
    WOFF = "woff"
    WOFF2 = "woff2"
    EML = "eml"
    NWS = "nws"
    PDB = "pdb"
    XYZ = "xyz"
    THREE_MF = "3mf"
    OBJ = "obj"
    STL = "stl"
    WMF = "wmf"
    MDB = "mdb"
    CSH = "csh"
    SH = "sh"
    TCL = "tcl"
    TE = "te"
    XI = "xi"
    TR = "tr"
    SRC = "src"
    BCPIO = "bcpio"
    CPIO = "cpio"
    GTAR = "gtar"
    HDF = "hdf"
    NC = "nc"
    SHAR = "shar"
    SV4CPIO = "sv4cpio"
    SV4CRC = "sv4crc"
    USTAR = "ustar"
    DCR = "dcr"
    EVY = "evy"
    MIF = "mif"
    CDF = "cdf"
    SCR = "scr"
    DATA = "data"
    RTF = "rtf"
    KSWPS = "kswps"
    XPSDOCUMENT = "xpsdocument"
    ACROBAT = "acrobat"
    STREAM = "stream"
    PJPG = "pjpeg"
    ZIP_COMPRESSED = "zip-compressed"
    TEMPLATE = "template"
    CHROME_EXTENSION = "chrome-extension"
    REAL = "real"
    OCTET = "octet"
    SAVE = "save"
    SLIDESHOW = "slideshow"
    UNKNOWN = "unknown"
    OCTETSTREAM = "octetstream"
    TEXT = "text"
    MACROENABLED = "macroenabled"
    WORDPROCESSINGML = "wordprocessingml"
    FORM_URLENCODED = "form-urlencoded"
    TYPE = "type"
    CBL = "cbl"
    COMPRESSED = "compressed"
    DOT_PDF = ".pdf"
    SPREADSHEET = "spreadsheet"
    DOWNLOAD = "download"
    PRESENTATION = "presentation"
    RICHTEXT = "richtext"
    JAVASCRIPT = "javascript"
    GRAPHICS = "graphics"
    MSWORD = "msword"
    DRAWING = "drawing"
    RFC822 = "rfc822"

    def as_mime_type(self) -> str:
        """Returns the MIME type associated with the file extension."""
        mime_type = mimetypes.guess_type(f"dummy.{self.value}")[0]
        if mime_type is None:
            raise ValueError(f"Unknown MIME type for extension: {self.value}")

        return mime_type


class RawFile(msgspec.Struct, frozen=True, gc=False):
    """
    Represents an immutable raw file with its content and extension.

    The `RawFile` class is designed for efficient and immutable handling of raw file data.
    It stores file contents as immutable bytes and provides utility methods for reading,
    writing, and manipulating the file content without mutating the original data.

    **Key Features:**

    - **Immutability**: Instances of `RawFile` are immutable. Once created, their contents cannot be modified.
      This is enforced by using `msgspec.Struct` with `frozen=True`, ensuring thread-safety and predictability.
    - **Performance**: Optimized for speed and memory efficiency by disabling garbage collection (`gc=False`)
      and using immutable data structures. This reduces overhead and can significantly boost performance,
      especially when handling many instances.
    - **Compactness**: Stores file content in memory as bytes, leading to fast access and manipulation.
      The absence of mutable state allows for leaner objects.
    - **Garbage Collection**: By setting `gc=False`, the class instances are excluded from garbage collection tracking.
      This improves performance when creating many small objects but requires careful management of resources.
    - **Compression Support**: Provides methods for compressing and decompressing file contents using gzip,
      returning new `RawFile` instances without altering the original data.
    - **Versatile Creation Methods**: Offers multiple class methods to create `RawFile` instances from various sources,
      such as file paths, bytes, base64 strings, strings, streams, URLs, and cloud storage services.

    **Important Notes:**

    - **Memory Usage**: Since the entire file content is stored in memory, handling very large files may lead
      to high memory consumption. Ensure that file sizes are manageable within the available system memory.
    - **Resource Management**: As garbage collection is disabled, it's crucial to manage resources appropriately.
      While the class is designed to be immutable and not require cleanup, be cautious when handling external resources.
    - **Thread-Safety**: Immutability ensures that instances of `RawFile` are inherently thread-safe.

    **Example Usage:**

    ```python
    # Create a RawFile instance from a file path
    raw_file = RawFile.from_file_path('example.pdf')

    # Access the file extension
    print(raw_file.extension)  # Output: FileExtension.PDF

    # Get the size of the file content
    print(raw_file.get_size())  # Output: Size of the file in bytes

    # Compute checksums
    md5_checksum = raw_file.compute_md5()
    sha256_checksum = raw_file.compute_sha256()

    # Save the content to a new file
    raw_file.save_to_file('copy_of_example.pdf')

    # Compress the file content
    compressed_file = raw_file.compress()

    # Decompress the file content
    decompressed_file = compressed_file.decompress()
    ```

    **Methods Overview:**

    - Creation:
      - `from_file_path(cls, file_path: str)`: Create from a file path.
      - `from_bytes(cls, data: bytes, extension: FileExtension)`: Create from bytes.
      - `from_base64(cls, b64_string: str, extension: FileExtension)`: Create from a base64 string.
      - `from_string(cls, content: str, extension: FileExtension, encoding: str = "utf-8")`: Create from a string.
      - `from_stream(cls, stream: BinaryIO, extension: FileExtension)`: Create from a binary stream.
      - `from_url(cls, url: str, ...)`: Create from a URL.
      - `from_s3(cls, bucket_name: str, object_key: str, extension: Optional[FileExtension] = None)`: Create from Amazon S3.
      - `from_azure_blob(cls, connection_string: str, container_name: str, blob_name: str, extension: Optional[FileExtension] = None)`: Create from Azure Blob Storage.
      - `from_gcs(cls, bucket_name: str, blob_name: str, extension: Optional[FileExtension] = None)`: Create from Google Cloud Storage.
      - `from_zip(cls, zip_file_path: str, inner_file_path: str, extension: Optional[FileExtension] = None)`: Create from a file within a ZIP archive.
      - `from_stdin(cls, extension: FileExtension)`: Create from standard input.

    - Utilities:
      - `save_to_file(self, file_path: str)`: Save content to a file.
      - `get_size(self) -> int`: Get the size of the content in bytes.
      - `compute_md5(self) -> str`: Compute MD5 checksum.
      - `compute_sha256(self) -> str`: Compute SHA256 checksum.
      - `get_mime_type(self) -> str`: Get MIME type based on the file extension.
      - `compress(self) -> RawFile`: Compress content using gzip.
      - `decompress(self) -> RawFile`: Decompress gzip-compressed content.
      - `read_async(self) -> bytes`: Asynchronously read the content.

    **Immutability Enforcement:**

    - The class is decorated with `msgspec.Struct` and `frozen=True`, which makes all instances immutable.
    - Any method that would traditionally modify the instance returns a new `RawFile` instance instead.
    - This design ensures that the original data remains unchanged, promoting safer and more predictable code.

    **Performance Considerations:**

    - **No Garbage Collection Overhead**: By setting `gc=False`, instances are not tracked by the garbage collector, reducing overhead.
      This is suitable when instances do not contain cyclic references.
    - **Optimized Data Structures**: Using immutable bytes and avoiding mutable state enhances performance and reduces memory footprint.
    - **Fast Access**: In-memory storage allows for rapid access and manipulation of file content.

    **Garbage Collection and Resource Management:**

    - While garbage collection is disabled for instances, Python's reference counting will still deallocate objects when they are no longer in use.
    - Be mindful when working with external resources (e.g., open files or network connections) to ensure they are properly closed.
    - Since `RawFile` instances hold data in memory, they are automatically cleaned up when references are removed.

    **Thread-Safety:**

    - Immutable objects are inherently thread-safe because their state cannot change after creation.
    - `RawFile` instances can be shared across threads without the need for synchronization mechanisms.

    **Compression Level:**

    - The `compress` and `decompress` methods use gzip with default compression levels.
    - If you need to specify a compression level, you can modify the methods to accept a parameter for the compression level.

    **Extensibility:**

    - The `FileExtension` enum and content type mappings can be extended to support additional file types as needed.
    - Custom methods can be added to handle specific use cases or integrations with other services.

    **Examples of Creating `RawFile` Instances from Different Sources:**

    ```python
    # From bytes
    raw_file = RawFile.from_bytes(b"Hello, World!", FileExtension.TXT)

    # From a base64 string
    raw_file = RawFile.from_base64("SGVsbG8sIFdvcmxkIQ==", FileExtension.TXT)

    # From a URL
    raw_file = RawFile.from_url("https://example.com/data.json")

    # From Amazon S3
    raw_file = RawFile.from_s3("my-bucket", "path/to/object.json")

    # From Azure Blob Storage
    raw_file = RawFile.from_azure_blob("connection_string", "container", "blob.json")

    # From Google Cloud Storage
    raw_file = RawFile.from_gcs("my-bucket", "path/to/blob.json")

    # From standard input
    raw_file = RawFile.from_stdin(FileExtension.TXT)
    ```

    **Disclaimer:**

    - Ensure that all necessary dependencies are installed for methods that interface with external services.
    - Handle exceptions appropriately in production code, especially when dealing with I/O operations and network requests.
    """

    name: Annotated[
        str,
        msgspec.Meta(
            title="Name", description="The name of the file", examples=["example.pdf"]
        ),
    ]
    contents: bytes
    extension: FileExtension

    @classmethod
    def from_file_path(cls, file_path: str) -> RawFile:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found at {file_path}")

        if not path.is_file():
            raise ValueError(f"{file_path} is not a file")

        with open(file_path, "rb") as f:
            data = f.read()

        return cls(
            name=path.name,
            contents=data,
            extension=FileExtension(path.suffix.lstrip(".")),
        )

    @classmethod
    def from_bytes(cls, data: bytes, name: str, extension: FileExtension) -> RawFile:
        return cls(name=name, contents=data, extension=extension)

    @classmethod
    def from_base64(
        cls, b64_string: str, name: str, extension: FileExtension
    ) -> RawFile:
        data = base64.b64decode(b64_string)
        return cls.from_bytes(data=data, name=name, extension=extension)

    @classmethod
    def from_string(
        cls, content: str, name: str, extension: FileExtension, encoding: str = "utf-8"
    ) -> RawFile:
        data = content.encode(encoding)
        return cls.from_bytes(data=data, name=name, extension=extension)

    @classmethod
    def from_stream(
        cls, stream: BinaryIO, name: str, extension: FileExtension
    ) -> RawFile:
        data = stream.read()
        return cls(name=name, contents=data, extension=extension)

    @overload
    @classmethod
    def from_litestar_upload_file(
        cls, file: LitestarUploadFile, is_zip: Literal[False] = False
    ) -> RawFile: ...

    @overload
    @classmethod
    def from_litestar_upload_file(
        cls, file: LitestarUploadFile, is_zip: Literal[True]
    ) -> Sequence[RawFile]: ...

    @classmethod
    @ensure_module_installed("litestar", "litestar")
    def from_litestar_upload_file(
        cls, file: LitestarUploadFile, is_zip: bool = False
    ) -> RawFile | Sequence[RawFile]:
        filename = file.filename
        content_type = file.content_type
        file_contents = file.file.read()

        debug_logger.debug(f"File content type: {content_type}")
        debug_logger.debug(f"File name: {filename}")

        extension: FileExtension = find_extension(
            filename=filename,
            content_type=content_type,
            contents=file_contents,
        )

        return cls(name=file.filename, contents=file_contents, extension=extension)

    @classmethod
    @ensure_module_installed("fastapi", "fastapi")
    def from_fastapi_upload_file(cls, file: FastAPIUploadFile) -> RawFile:
        if file.content_type is None:
            raise ValueError("The content type of the file is missing.")
        file_contents = file.file.read()

        extension: Optional[FileExtension] = find_extension(
            content_type=file.content_type,
            filename=file.filename,
            contents=file_contents,
        )

        if extension is None:
            raise ValueError(f"{file.content_type} is not a supported file type yet.")

        filename = file.filename
        if filename is None:
            raise ValueError("The filename of the file is missing.")

        return cls(name=filename, contents=file_contents, extension=extension)

    @classmethod
    def from_url(
        cls: type[Self],
        url: str,
        *,
        params: Optional[_Params] = None,
        data: Optional[_Data] = None,
        headers: Optional[_HeadersMapping] = None,
        cookies: Optional[CookieJar | _TextMapping] = None,
        files: Optional[_Files] = None,
        auth: Optional[_Auth] = None,
        timeout: Optional[_Timeout] = None,
        allow_redirects: bool = False,
        proxies: Optional[_TextMapping] = None,
        hooks: Optional[_HooksInput] = None,
        stream: Optional[bool] = None,
        verify: Optional[_Verify] = None,
        cert: Optional[_Cert] = None,
        json: Optional[Incomplete] = None,
        extension: Optional[FileExtension] = None,
    ) -> RawFile:
        response: requests.Response = requests.get(
            url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
        )
        response.encoding = "utf-8"

        response_content: bytes | Any = response.content

        if not isinstance(response_content, bytes):
            data = str(data).encode("utf-8")

        file_extension = extension or (
            find_extension(
                content_type=response.headers.get("Content-Type", "").split(";")[0]
            )
            or FileExtension.HTML
        )

        return cls(name=url, contents=response_content, extension=file_extension)

    @ensure_module_installed("boto3", "boto3")
    @classmethod
    def from_s3(
        cls,
        bucket_name: str,
        object_key: str,
        extension: Optional[FileExtension] = None,
    ) -> RawFile:
        import boto3

        s3 = boto3.client("s3")

        if not extension:
            ext = Path(object_key).suffix.lstrip(".")
            if ext.upper() in FileExtension.__members__:
                extension = FileExtension[ext.upper()]
            else:
                head_object = s3.head_object(Bucket=bucket_name, Key=object_key)
                content_type = head_object.get("ContentType", "")
                extension = find_extension(content_type=content_type)

        if not extension:
            raise ValueError(
                "Unable to determine the file extension. Please specify it explicitly."
            )

        obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        data = obj["Body"].read()

        return cls(name=bucket_name, contents=data, extension=extension)

    @ensure_module_installed("azure.storage.blob", "azure-storage-blob")
    @classmethod
    def from_azure_blob(
        cls,
        connection_string: str,
        container_name: str,
        blob_name: str,
        extension: Optional[FileExtension] = None,
    ) -> RawFile:
        from azure.storage.blob import BlobServiceClient

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )

        if not extension:
            ext = Path(blob_name).suffix.lstrip(".")
            if ext.upper() in FileExtension.__members__:
                extension = FileExtension[ext.upper()]
            else:
                properties = blob_client.get_blob_properties()
                content_type = properties.content_settings.content_type
                if content_type is None:
                    raise ValueError(
                        "Unable to determine the file extension. Please specify it explicitly."
                    )

                extension = find_extension(content_type=content_type)

        if not extension:
            raise ValueError(
                "Unable to determine the file extension. Please specify it explicitly."
            )

        stream = blob_client.download_blob()
        data = stream.readall()

        return cls(name=container_name, contents=data, extension=extension)

    @ensure_module_installed("google.cloud.storage", "google-cloud-storage")
    @classmethod
    def from_gcs(
        cls, bucket_name: str, blob_name: str, extension: Optional[FileExtension] = None
    ) -> RawFile:
        from google.cloud.storage import Client

        client = Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if not extension:
            ext = Path(blob_name).suffix.lstrip(".")
            if ext.upper() in FileExtension.__members__:
                extension = FileExtension[ext.upper()]
            else:
                blob.reload()
                content_type = blob.content_type
                extension = find_extension(content_type=content_type)

        if not extension:
            raise ValueError(
                "Unable to determine the file extension. Please specify it explicitly."
            )

        data = blob.download_as_bytes()

        return cls(name=bucket_name, contents=data, extension=extension)

    @classmethod
    def from_zip(
        cls,
        zip_file_path: str,
    ) -> RawFile:
        """
        Creates a RawFile instance from a ZIP archive. The content of the RawFile
        will be the bytes of the entire ZIP archive itself.

        Args:
            zip_file_path: The path to the ZIP archive file.

        Returns:
            A RawFile instance where the contents are the bytes of the ZIP archive
            and the extension is FileExtension.ZIP.
        """
        with open(zip_file_path, "rb") as f:
            data = f.read()

        return cls(
            name=Path(zip_file_path).name, contents=data, extension=FileExtension.ZIP
        )

    @classmethod
    def from_database_blob(cls, blob_data: bytes, extension: FileExtension) -> RawFile:
        return cls.from_bytes(name="database_blob", data=blob_data, extension=extension)

    @classmethod
    def from_stdin(cls, extension: FileExtension) -> RawFile:
        data = sys.stdin.buffer.read()
        return cls.from_bytes(name="stdin", data=data, extension=extension)

    @classmethod
    def from_ftp(
        cls,
        host: str,
        filepath: str,
        username: str = "",
        password: str = "",
        extension: Optional[FileExtension] = None,
    ) -> RawFile:
        import ftplib

        ftp = ftplib.FTP(host)
        ftp.login(user=username, passwd=password)
        data = bytearray()
        ftp.retrbinary(f"RETR {filepath}", data.extend)
        ftp.quit()
        if not extension:
            extension = FileExtension(Path(filepath).suffix.lstrip("."))
        return cls(name=filepath, contents=bytes(data), extension=extension)

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "wb") as f:
            f.write(self.contents)

    def get_size(self) -> int:
        return len(self.contents)

    def compute_md5(self) -> str:
        md5 = hashlib.md5()
        md5.update(self.contents)
        return md5.hexdigest()

    def compute_sha256(self) -> str:
        sha256 = hashlib.sha256()
        sha256.update(self.contents)
        return sha256.hexdigest()

    def get_mime_type(self) -> str:
        mime_type, _ = mimetypes.guess_type(f"file.{self.extension}")
        return mime_type or "application/octet-stream"

    def compress(self) -> RawFile:
        import gzip

        compressed_data = gzip.compress(self.contents)
        return RawFile(
            name="compressed.zip", contents=compressed_data, extension=self.extension
        )  # TODO

    def decompress(self) -> RawFile:
        import gzip

        decompressed_data = gzip.decompress(self.contents)
        return RawFile(
            name=self.name, contents=decompressed_data, extension=self.extension
        )

    async def read_async(self) -> bytes:
        return self.contents

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass  # Nothing to close since we're using bytes

    def __del__(self):
        pass  # No cleanup needed
