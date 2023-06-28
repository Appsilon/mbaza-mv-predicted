# mbaza-mv-predicted

A small Mbaza post-processing script to copy images from source folder to predicted folder.

## Installation

The package can be installed directly from Github:

```
pip install git+https://github.com/Appsilon/mbaza-mv-predicted.git
```

## Running

Once installed, run the `mbaza_mv_predicted` script to process the `.csv` output from Mbaza, for example:

```
mbaza_mv_predicted /path/to/mbaza_output_file.csv /path/to/images --output_path /path/to/output --p 0.5 --p_multi 0.2
```

This will output a new csv file in the `output_path` directory which contains the original Mbaza information and paths where the image has been copied to.

NOTE: this requires the same `/path/to/images` as provided to Mbaza.

The following commands are optional:

- `output_path` defaults to `/path/to/images/predicted`
- `p` is the probability threshold required to copy the image to the top predicted species (otherwise copied to `unknown`), defaults to 0 i.e. all images will be copied to a species folder
- `p_multi` is the probability threshold required to also copy images to the 2nd/3rd top predicted species folder (multi-label), default behaviour is off i.e. images will only be copied to one folder

For help with commands run:

```
mbaza_mv_predicted -h
```
