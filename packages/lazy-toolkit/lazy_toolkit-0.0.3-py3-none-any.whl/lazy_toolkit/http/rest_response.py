from typing import IO, Any, BinaryIO, Iterable

import jsonpickle

from .status_code import *

CONTENT_TYPE_MAP: dict = {
    '.js': 'application/javascript',
    '.mjs': 'application/javascript',
    '.json': 'application/json',
    '.webmanifest': 'application/manifest+json',
    '.doc': 'application/msword',
    '.dot': 'application/msword',
    '.wiz': 'application/msword',
    '.bin': 'application/octet-stream',
    '.a': 'application/octet-stream',
    '.dll': 'application/octet-stream',
    '.exe': 'application/octet-stream',
    '.o': 'application/octet-stream',
    '.obj': 'application/octet-stream',
    '.so': 'application/octet-stream',
    '.oda': 'application/oda',
    '.pdf': 'application/pdf',
    '.p7c': 'application/pkcs7-mime',
    '.ps': 'application/postscript',
    '.ai': 'application/postscript',
    '.eps': 'application/postscript',
    '.m3u': 'application/vnd.apple.mpegurl',
    '.m3u8': 'application/vnd.apple.mpegurl',
    '.xls': 'application/vnd.ms-excel',
    '.xlb': 'application/vnd.ms-excel',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pot': 'application/vnd.ms-powerpoint',
    '.ppa': 'application/vnd.ms-powerpoint',
    '.pps': 'application/vnd.ms-powerpoint',
    '.pwz': 'application/vnd.ms-powerpoint',
    '.wasm': 'application/wasm',
    '.bcpio': 'application/x-bcpio',
    '.cpio': 'application/x-cpio',
    '.csh': 'application/x-csh',
    '.dvi': 'application/x-dvi',
    '.gtar': 'application/x-gtar',
    '.hdf': 'application/x-hdf',
    '.h5': 'application/x-hdf5',
    '.latex': 'application/x-latex',
    '.mif': 'application/x-mif',
    '.cdf': 'application/x-netcdf',
    '.nc': 'application/x-netcdf',
    '.p12': 'application/x-pkcs12',
    '.pfx': 'application/x-pkcs12',
    '.ram': 'application/x-pn-realaudio',
    '.pyc': 'application/x-python-code',
    '.pyo': 'application/x-python-code',
    '.sh': 'application/x-sh',
    '.shar': 'application/x-shar',
    '.swf': 'application/x-shockwave-flash',
    '.sv4cpio': 'application/x-sv4cpio',
    '.sv4crc': 'application/x-sv4crc',
    '.tar': 'application/x-tar',
    '.tcl': 'application/x-tcl',
    '.tex': 'application/x-tex',
    '.texi': 'application/x-texinfo',
    '.texinfo': 'application/x-texinfo',
    '.roff': 'application/x-troff',
    '.t': 'application/x-troff',
    '.tr': 'application/x-troff',
    '.man': 'application/x-troff-man',
    '.me': 'application/x-troff-me',
    '.ms': 'application/x-troff-ms',
    '.ustar': 'application/x-ustar',
    '.src': 'application/x-wais-source',
    '.xsl': 'application/xml',
    '.rdf': 'application/xml',
    '.wsdl': 'application/xml',
    '.xpdl': 'application/xml',
    '.zip': 'application/zip',
    '.3gp': 'audio/3gpp',
    '.3gpp': 'audio/3gpp',
    '.3g2': 'audio/3gpp2',
    '.3gpp2': 'audio/3gpp2',
    '.aac': 'audio/aac',
    '.adts': 'audio/aac',
    '.loas': 'audio/aac',
    '.ass': 'audio/aac',
    '.au': 'audio/basic',
    '.snd': 'audio/basic',
    '.mp3': 'audio/mpeg',
    '.mp2': 'audio/mpeg',
    '.opus': 'audio/opus',
    '.aif': 'audio/x-aiff',
    '.aifc': 'audio/x-aiff',
    '.aiff': 'audio/x-aiff',
    '.ra': 'audio/x-pn-realaudio',
    '.wav': 'audio/x-wav',
    '.bmp': 'image/bmp',
    '.gif': 'image/gif',
    '.ief': 'image/ief',
    '.jpg': 'image/jpeg',
    '.jpe': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.heic': 'image/heic',
    '.heif': 'image/heif',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
    '.ico': 'image/vnd.microsoft.icon',
    '.ras': 'image/x-cmu-raster',
    '.pnm': 'image/x-portable-anymap',
    '.pbm': 'image/x-portable-bitmap',
    '.pgm': 'image/x-portable-graymap',
    '.ppm': 'image/x-portable-pixmap',
    '.rgb': 'image/x-rgb',
    '.xbm': 'image/x-xbitmap',
    '.xpm': 'image/x-xpixmap',
    '.xwd': 'image/x-xwindowdump',
    '.eml': 'message/rfc822',
    '.mht': 'message/rfc822',
    '.mhtml': 'message/rfc822',
    '.nws': 'message/rfc822',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.html': 'text/html',
    '.htm': 'text/html',
    '.txt': 'text/plain',
    '.bat': 'text/plain',
    '.c': 'text/plain',
    '.h': 'text/plain',
    '.ksh': 'text/plain',
    '.pl': 'text/plain',
    '.rtx': 'text/richtext',
    '.tsv': 'text/tab-separated-values',
    '.py': 'text/x-python',
    '.etx': 'text/x-setext',
    '.sgm': 'text/x-sgml',
    '.sgml': 'text/x-sgml',
    '.vcf': 'text/x-vcard',
    '.xml': 'text/xml',
    '.mp4': 'video/mp4',
    '.mpeg': 'video/mpeg',
    '.m1v': 'video/mpeg',
    '.mpa': 'video/mpeg',
    '.mpe': 'video/mpeg',
    '.mpg': 'video/mpeg',
    '.mov': 'video/quicktime',
    '.qt': 'video/quicktime',
    '.webm': 'video/webm',
    '.avi': 'video/x-msvideo',
    '.movie': 'video/x-sgi-movie',
}


def get_content_type(extension: str) -> str:
    content_type: str | None = CONTENT_TYPE_MAP.get(extension, None)
    if not content_type:
        content_type = 'application/octet-stream'
    return content_type


class RestResponse:
    def __init__(self):
        # is_success means the operation is success or not, it does not mean the status code is success or not
        # - E.g., a response may have a status code of 200 but the operation failed (such as provided ID not found in DB), and is_success=False
        # - It means the server handled the request properly, and the fault is on the client side
        self.is_success: bool = False
        self.message: str | None = None
        self.status_code: int = -1
        self.data: Any = None
        self.token: str | None = None

    def to_json(self) -> str:
        return jsonpickle.encode(self, unpicklable=False)  # type: ignore

    @staticmethod
    def __succeeded(status_code: StatusCode,
                    data: Any = None,
                    token: str | None = None,
                    msg: str | None = None) -> 'RestResponse':
        """
        Success with a status code
        """
        response: RestResponse = RestResponse()
        response.is_success = True
        response.message = msg if msg else status_code.message
        response.status_code = status_code.code
        response.data = data
        response.token = token

        return response

    @staticmethod
    def __failed(status_code: StatusCode,
                 data: Any = None,
                 msg: str | None = None) -> 'RestResponse':
        """
        Failed with a status code
        """
        response: RestResponse = RestResponse()
        response.is_success = False
        response.message = msg if msg else status_code.message
        response.status_code = status_code.code
        response.data = data

        return response

    @staticmethod
    def failed(status_code: StatusCode | None = None,
               data: Any = None,
               header: dict | None = None,
               msg: str | None = None) -> tuple[str, int, dict]:
        """
        :return: tuple[str, int, dict]: Flask response for data, status code, and customized header
        """
        if header is None:
            header = {'Content-Type': get_content_type('.json')}
        if 'Content-Type' not in header:
            header['Content-Type'] = get_content_type('.json')
        if status_code is None:
            status_code = UNPROCESSABLE

        response: RestResponse = RestResponse.__failed(status_code=status_code, data=data, msg=msg)
        return response.to_json(), status_code.code, header

    @staticmethod
    def success(status_code: StatusCode | None = None,
                data: Any = None,
                token: str | None = None,
                header: dict | None = None,
                msg: str | None = None) -> tuple[str, int, dict]:
        """
        :return: tuple[str, int, dict]: Flask response for data, status code, and customized header
        """
        if header is None:
            header = {'Content-Type': get_content_type('.json')}
        if 'Content-Type' not in header:
            header['Content-Type'] = get_content_type('.json')
        if status_code is None:
            status_code = SUCCESS

        response: RestResponse = RestResponse.__succeeded(status_code=status_code, data=data, token=token,
                                                          msg=msg)
        return response.to_json(), status_code.code, header
