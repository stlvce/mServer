import sys
from PIL import Image
import io

_WIN32_CLIPBOARD_AVAILABLE = False
try:
    import win32clipboard
    from PIL import ImageGrab

    _WIN32_CLIPBOARD_AVAILABLE = True
except ImportError:
    pass


def send_image_to_clipboard(image: Image.Image):
    """
    Копирует PIL Image в системный буфер обмена.
    Поддерживается только Windows (через pywin32).
    """
    if not _WIN32_CLIPBOARD_AVAILABLE:
        print(
            "⚠️  Копирование изображения в буфер обмена поддерживается только на Windows (требуется pywin32).",
            file=sys.stderr,
        )
        print("   Установите: pip install pywin32")
        return False

    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # BMP header starts at 14th byte
    output.close()

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    finally:
        win32clipboard.CloseClipboard()
    return True
