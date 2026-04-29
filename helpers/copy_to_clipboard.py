import io
import sys

import matplotlib.pyplot as plt
from PIL import Image
from rich import print

_WIN32_CLIPBOARD_AVAILABLE = False
try:
    import win32clipboard

    _WIN32_CLIPBOARD_AVAILABLE = True
except ImportError:
    pass


def copy_fig_to_clipboard(dpi: int = 100) -> bool:
    """Copies the current matplotlib figure to the Windows clipboard as a BMP image.

    Returns True on success, False if win32clipboard is unavailable.
    """
    if not _WIN32_CLIPBOARD_AVAILABLE:
        print(
            "[[yellow]clipboard[/yellow]]  Копирование в буфер обмена поддерживается только на Windows (требуется pywin32).",
            file=sys.stderr,
        )
        return False

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    plt.close()
    buf.seek(0)

    bmp_buf = io.BytesIO()
    Image.open(buf).convert("RGB").save(bmp_buf, "BMP")
    data = bmp_buf.getvalue()[14:]  # strip 14-byte BMP file header
    bmp_buf.close()
    buf.close()

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    finally:
        win32clipboard.CloseClipboard()

    print(
        "[[green]clipboard[/green]] График скопирован в буфер обмена (Windows). Можно вставить Ctrl+V."
    )

    return True
