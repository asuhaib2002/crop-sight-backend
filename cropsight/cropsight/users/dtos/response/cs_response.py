from dataclasses import dataclass
from typing import Any, Optional
from dataclasses_json import dataclass_json
from django.http import HttpResponse , JsonResponse


@dataclass_json
@dataclass
class CSResponse:
    success: bool
    message: str
    status: int
    data: Optional[Any] = None
    error: Optional[Any] = None
    error_code: Optional[int] = None

    @staticmethod
    def generate_response(success: bool = False,
                          message: str = '',
                          status: int = 200,
                          data: Any = None,
                          error: Any = None,
                          error_code: int = None):
        return CSResponse(success=success, message=message, status=status,
                          data=data, error=error, error_code=error_code)

    @staticmethod
    def send_response(success: bool = True,
                      message: str = '',
                      status: int = 200,
                      data: Optional[Any] = None,
                      error: Optional[Any] = None,
                      error_code: Optional[int] = None) -> HttpResponse:
        response = CSResponse(success=success, message=message, status=status,
                              data=data, error=error, error_code=error_code)
        return CSResponse._send(response)

    @staticmethod
    def _send(response: 'CSResponse') -> HttpResponse:
        return HttpResponse(
            response.to_json(), status=response.status,
            content_type='application/json'
        )
