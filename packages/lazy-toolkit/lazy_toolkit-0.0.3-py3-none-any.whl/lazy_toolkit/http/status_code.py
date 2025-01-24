class StatusCode:
    def __init__(self, code: int, message_template: str | None):
        self.code: int = code
        self.message_template: str | None = message_template
        self.message: str | None = None

    def get_message(self) -> str:
        msg: str | None = self.message_template if not self.message else self.message
        return msg if msg is not None else ''

    def set_message(self, message: str) -> 'StatusCode':
        self.message = message
        return self

    def with_message_keyword(self, keyword: str) -> 'StatusCode':
        if keyword and self.message_template:
            self.message = self.message_template.format(text=keyword)
        return self


SUCCESS = StatusCode(200, None)
CREATED = StatusCode(201, None)
UPDATED = StatusCode(200, None)
NO_CONTENT = StatusCode(204, 'Empty content for resource')
BAD_REQUEST = StatusCode(400, 'Bad request')
UNAUTHORIZED = StatusCode(401, 'Unauthorized')
FORBIDDEN = StatusCode(403, 'Forbidden')
NOT_FOUND = StatusCode(404, 'Resource not found')
METHOD_NOT_ALLOWED = StatusCode(405, 'Method not allowed')
CONFLICT = StatusCode(409, 'Resource already exists')
REQUEST_TOO_LARGE = StatusCode(413, 'Request too large')
UNPROCESSABLE = StatusCode(422, 'Request data cannot be processed')
REMOTING_ERROR = StatusCode(500, 'Remote call error')
UNKNOWN_ERROR = StatusCode(500, 'Unknown error')
