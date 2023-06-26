import argparse
import pandas as pd
import shutil
from datetime import datetime
from pandarallel import pandarallel
from pathlib import Path
from PIL import Image
from pydantic import BaseModel, FilePath, DirectoryPath, validator


pandarallel.initialize(progress_bar=True)


class Settings(BaseModel):
    csv_path: FilePath
    image_path: DirectoryPath
    output_path: Path
    prob_threshold: float = 0.
    prob_multi_threshold: float = 0.5
    max_multi_pred: int = 3

    @validator("output_path")
    def output_path_exists(p: Path):
        
        p.mkdir(exist_ok=True)
        return p
    
    @validator("max_multi_pred")
    def bound(n):
        if n > 3:
            print("Only up to 3 species per image supported")
        
        return min(max(n, 1), 3)


def process(settings: Settings):

    def copy_images(row):

        # Going through top max_multi_pred scores
        new_paths = []
        for i in range(1, settings.max_multi_pred + 1):

            new_path = None

            if (
                    (i == 1 and row[f"score_{i}"] > settings.prob_threshold) or \
                    (i > 1 and row[f"score_{i}"] > settings.prob_multi_threshold)
                ):

                orig_path = settings.image_path / row["location"]
                
                exif = get_exif(orig_path)

                camera = get_corridor_string(str(exif[37500]))
                camera_path = "/".join(camera.rsplit("-", 1))
                
                date = datetime.strptime(exif[36867], "%Y:%m:%d %H:%M:%S")
                date_path = f"{date.year}/week{date.isocalendar()[1]}"

                new_path = settings.output_path / date_path / camera_path / row[f"pred_{i}"]
            else:
                # Move to unknown folder
                if i == 1:
                    new_path = settings.output_path / date_path / camera_path / "unknown"

            if new_path is not None:
                new_path.mkdir(exist_ok=True, parents=True)
                shutil.copy2(orig_path, new_path)
            
            new_paths.append(new_path)
        
        return new_paths

    df = pd.read_csv(settings.csv_path)
    print(f"Total images to process: {df.shape[0]}")

    species_paths = df.parallel_apply(copy_images, axis=1)
    pred_path_cols = [f'pred_path_{i+1}' for i in range(settings.max_multi_pred)]
    
    df[pred_path_cols] = pd.DataFrame(species_paths.to_list(), index=df.index)
    df.to_csv(settings.output_path / settings.csv_path.name)


def get_exif(path: Path):

    exif = Image.open(path)._getexif()

    if exif is None:
        raise ValueError(f"No exif data found for file: {path}")
        
    return exif


def get_corridor_string(text: str):

    start = text.find("CORRIDOR")    
    end = text.find("\\", start)
    return text[start:end].strip()


def main():
    parser = argparse.ArgumentParser(description="Convert Mbaza image predictions to sequence predictions")
    parser.add_argument("csv_path", type=Path, help="Path to csv output from Mbaza")
    parser.add_argument("image_path", type=Path, help="Path to images (same as supplied to Mbaza)")
    parser.add_argument("--output_path", type=Path, help="Folder to move images to (default is image_path/predicted)", required=False, default=None)
    parser.add_argument("--p", type=float, help="Confidence threshold to move image for top prediction", required=False, default=0.)
    parser.add_argument("--p_multi", type=float, help="Confidence threshold to also move image for 2nd and 3rd predictions", required=False, default=0.5)
    args = parser.parse_args()

    if args.output_path is None:
        args.output_path = args.image_path / "predicted"

    settings = Settings(
        csv_path=args.csv_path,
        image_path=args.image_path,
        output_path=args.output_path,
        prob_threshold=args.p,
        prob_multi_threshold=args.p_multi
    )

    process(settings=settings)


if __name__ == "__main__":

    main()
