import io

import matplotlib.pyplot as plt
from PIL import Image
from rich import print


def save_fig_as_bmp(path: str, dpi: int = 100):
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    plt.close()
    buf.seek(0)
    Image.open(buf).convert("RGB").save(path, format="BMP")
    buf.close()
    print("[[green]system[/green]] График сохранён в " + path)
