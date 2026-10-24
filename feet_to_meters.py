import rasterio
from glob import glob
from multiprocessing import Pool
import os

from main import run_command

US_SURVEY_FOOT = 0.304800609601219 # m

def process_file(filepath_in, filepath_out):
    nodata = None
    with rasterio.open(filepath_in) as src:
        nodata = src.nodata
    
    command = f'gdal_calc.py -A "{filepath_in}" --outfile="{filepath_out}" --calc="A*{US_SURVEY_FOOT}" --NoDataValue={nodata}'
    run_command(command, silent=False)

def process_source(source):
    folder_out = f'source-store/{source}m'
    os.makedirs(folder_out, exist_ok=True)
    filepaths_in = sorted(glob(f'source-store/{source}/*.tif'))
    argument_tuples = []
    for filepath_in in filepaths_in:
        filename = filepath_in.split('/')[-1]
        filepath_out = f'{folder_out}/{filename}'
        argument_tuples.append((filepath_in, filepath_out))
    with Pool(30) as pool:
        pool.starmap(process_file, argument_tuples, chunksize=1)

if __name__ == '__main__':
    # filepath_in = 'source-store/uscob/0000d9bf-f5bf-41ed-b219-0a999faf3e54-dem_LD32341593.tif'
    # filepath_out = 'out.tif'
    # process_file(filepath_in, filepath_out)
    source = 'uscoo'
    process_source(source)