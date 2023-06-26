from pathlib import Path
from PIL import Image


def get_corridor_string(path: Path):

    exif = Image.open(path)._getexif()

    if exif is None:
        raise ValueError(f"No exif data found for file: {path}")
        
    text = str(exif[37500])
    start = text.find("CORRIDOR")    
    end = text.find("\\", start)
    
    return text[start:end].strip()
