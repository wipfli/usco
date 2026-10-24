# usco
State of Colorado digital elevation model preparation scripts for Mapterhorn

## steps

Download all zip files from a private S3 bucket to `source-store/usco/`.

Then run all the steps in `main.py` one after the other. This should unpackage the zips, group files by coordinate reference system, and help select which files are not yet in the 3DEP dataset used by mainline Mapterhorn.