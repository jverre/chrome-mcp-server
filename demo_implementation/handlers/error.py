from ..models import messages

def create_error_response(message: messages.Request, error_code: int, error_message: str) -> messages.Response:
    return messages.Response(
        id=message.id,
        error=messages.Error(
            code=error_code,
            message=error_message
        )
    )