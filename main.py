from glob import glob
from multiprocessing import Pool
import zipfile
import os
import shutil
import subprocess
import rasterio
import numpy as np
import hashlib

import feet_to_meters
import source_to_cog

def process(filepath):
    folder = filepath.replace('.zip', '')
    os.makedirs(folder, exist_ok=True)
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(folder)
    os.remove(filepath)

def step1():
    filepaths = glob('source-store/usco/*.zip')
    print(len(filepaths))
    argument_tuples = [(filepath,) for filepath in filepaths]
    with Pool() as pool:
        pool.starmap(process, argument_tuples, chunksize=1)

def step2():
    folders = glob('source-store/usco/*')
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        filepaths = glob(f'{folder}/*')
        if len(filepaths) == 0:
            continue
        for filepath in filepaths:
            if '\\' in filepath:
                esri_folder = filepath.split('/')[-1].split('\\')[0]
                esri_filename = filepath.split('/')[-1].split('\\')[1]
                subfolder = f'{folder}/{esri_folder}'
                os.makedirs(subfolder, exist_ok=True)
                shutil.move(filepath, f'{subfolder}/{esri_filename}')
                print(f'renamed {filepath}')
def step3():
    filepaths = glob('source-store/usco/*/*')
    filenames = set({})
    for filepath in filepaths:
        filename = filepath.split('/')[-1].split('.')[0]
        if filename in filenames:
            print(filepath)
        filenames.add(filename)


def run_command(command, silent=True, env=None):
    if env is None:
        env = os.environ.copy()
    if not silent:
        print(command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = p.communicate()
    err = stderr.decode()
    if err != '' and not silent:
        print(err)
    out = stdout.decode()
    if out != '' and not silent:
        print(out)
    return out, err

def to_cog(filepath_in, filepath_out):
    run_command(f'GDAL_CACHEMAX=512 gdal_translate -of COG -co BLOCKSIZE=512 -co OVERVIEWS=NONE -co SPARSE_OK=YES -co BIGTIFF=YES -co COMPRESS=LERC -co MAX_Z_ERROR=0.001 "{filepath_in}" "{filepath_out}"', silent=False)
    if os.path.isdir(filepath_in):
        shutil.rmtree(filepath_in)
    else:
        os.remove(filepath_in)

def step4():
    filepaths = glob('source-store/usco/*/*')
    argument_tuples = []
    suffixes = set({})
    for filepath in filepaths:
        filepath_in = filepath
        zip_name = filepath.split('/')[-2]
        filename = filepath.split('/')[-1]
        filepath_out = ''
        if os.path.isdir(filepath):
            filepath_out = f'source-store/usco/{zip_name}-{filename}.tif'
        else:
            if filename.endswith('.xml'):
                continue
            filename = filename.replace('.IMG', '.tif').replace('.img', '.tif')
            filepath_out = f'source-store/usco/{zip_name}-{filename}'
        argument_tuples.append((filepath_in, filepath_out))
        suffixes.add(filepath_out.split('.')[-1])
    print(suffixes)
    with Pool() as pool:
        pool.starmap(to_cog, argument_tuples, chunksize=1)

def step5():
    filepaths = glob('source-store/usco/*')
    for filepath in filepaths:
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)

def step6():
    os.remove('source-store/usco/progress.json')

def step7():
    filepaths = glob('source-store/usco/*.tif')
    crs_to_filepaths = {}
    for i, filepath in enumerate(filepaths):
        if i % 1000 == 0:
            print(f'scan {i} / {len(filepaths)}')

        with rasterio.open(filepath) as src:
            if src.crs not in crs_to_filepaths:
                crs_to_filepaths[src.crs] = []
            crs_to_filepaths[src.crs].append(filepath)
    
    j = 0
    for i, crs in enumerate(crs_to_filepaths.keys()):
        md5_hash = hashlib.md5(str(crs).encode('utf-8'))
        folder = f'source-store/usco/crs_{md5_hash.hexdigest()}'
        os.makedirs(folder, exist_ok=True)
        for filepath in crs_to_filepaths[crs]:
            filename = filepath.split('/')[-1]
            shutil.move(filepath, f'{folder}/{filename}')
            j += 1
            if j % 1000 == 0:
                print(f'move {j} / {len(filepaths)}')

def step8():
    filepaths = glob('source-store/usco/*.tif.aux.xml')
    for filepath in filepaths:
        os.remove(filepath)

def step9():
    folders = glob('source-store/usco/*')
    for folder in folders:
        print(folder)
        filepaths = glob(f'{folder}/*')
        filepath = filepaths[0]
        with rasterio.open(filepath) as src:
            print(src.crs)
            print(len(filepaths))
            print()

def step10():
    folders = glob('source-store/usco/*')
    for folder in folders:
        print(folder)
        filepaths = glob(f'{folder}/*')
        nodata_values = set({})
        with rasterio.open(filepaths[0]) as src:
            print(src.crs)
        print('num files', len(filepaths))
        for filepath in filepaths:
            with rasterio.open(filepath) as src:
                nodata_values.add(src.nodata)
        for nodata in nodata_values:
            print(nodata)
        print()

def step11():
    shutil.move('source-store/usco/crs_0452846223829c21bacbb6701d74e517', 'source-store/uscoa')
    shutil.move('source-store/usco/crs_08c9287cb1333ad7ed9a48c5d8b61519', 'source-store/uscob')
    shutil.move('source-store/usco/crs_0fbf32185cdded6d62091e122e03f286', 'source-store/uscoc')
    shutil.move('source-store/usco/crs_2e8d21651514953314141df535ac6853', 'source-store/uscod')
    shutil.move('source-store/usco/crs_3c6b56178efdfde650a3e1b13ebc3891', 'source-store/uscoe')
    shutil.move('source-store/usco/crs_3f9505f4ef62b44dba519e884ce16c50', 'source-store/uscof')
    shutil.move('source-store/usco/crs_50f06a6f3e42c9ddc70dce53ec9bc290', 'source-store/uscog')
    shutil.move('source-store/usco/crs_510b2c924b47e18cbce5b408214be873', 'source-store/uscoh')
    shutil.move('source-store/usco/crs_538c486df81663fd1b3530e53e198ba2', 'source-store/uscoi')
    shutil.move('source-store/usco/crs_6adf97f83acf6453d4a6a4b1070f3754', 'source-store/uscoj')
    shutil.move('source-store/usco/crs_7bedfe6a3ebc50a7cccf53b8969f52fb', 'source-store/uscok')
    shutil.move('source-store/usco/crs_8226ac915cdaeedca3fb963e0fe2531b', 'source-store/uscol')
    shutil.move('source-store/usco/crs_a4d6dd74bc88da2866211873fa7c7753', 'source-store/uscom')
    shutil.move('source-store/usco/crs_cb256bdc3e68e80a410ff12fd1c89eb4', 'source-store/uscon')
    shutil.move('source-store/usco/crs_d59153ed47986632fab254856300fb67', 'source-store/uscoo')
    shutil.move('source-store/usco/crs_ddc49d89c9231a389ac192463338f94c', 'source-store/uscop')
    shutil.move('source-store/usco/crs_f1321b1cc5d3a57bb11d8d44adabf0c1', 'source-store/uscoq')
    shutil.move('source-store/usco/crs_f7db1136aac38be732a3435d9f6b910e', 'source-store/uscor')
    shutil.move('source-store/usco/crs_fcb38e6c2c760033143e912627f5c76a', 'source-store/uscos')
    shutil.move('source-store/usco/crs_fd52ede6e92e9200dc0e935a34f2a73e', 'source-store/uscot')

    # uscoa: not good, it is a surface model and only a small stripe
    # uscob: looks good, but grid artifact at high zoom. a lot of the data is already in Mapterhorn it seems. large color difference, is the data maybe in ft?
    # uscoc: looks good, more detailed than main, same color
    # uscod: looks good, has z16 and z17 data with same filename scheme, probably already fully in main
    # uscoe: zoom 19, skipping. maybe horizontal units are in feet?
    # uscof: probably in feet, one nice block
    # uscog: probably in feet, looks already in main
    # uscoh: looks good, already mostly covered
    # uscoi: looks good
    # uscoj: crs not defined
    # uscok: looks ok, small river basin, already in main

def step12():
    folders = sorted(glob('source-store/*'))
    for folder in folders:
        filepaths = sorted(glob(f'{folder}/*.tif'))
        with rasterio.open(filepaths[-1]) as src:
            print(folder)
            print(src.crs)
            band1 = src.read(1, masked=True)
            print(np.ma.mean(band1))
            print()

def step13():
    folders = sorted(glob('source-store/*'))
    for folder in folders:
        filepaths = glob(f'{folder}/*.tif')
        with rasterio.open(filepaths[0]) as src:
            band1 = src.read(1, masked=True)
            mean_elevation = np.ma.mean(band1)
            if 'COMPD_CS[' in str(src.crs):
                continue
            if mean_elevation > 4000 or 'UNIT["US survey foot"' in str(src.crs):
                print(folder)

def step14():
    sources = [
        'uscob',
        'uscof',
        'uscog',
        'uscoo',
        'uscop',
        'uscoq',
        'uscos',
        'uscot',
    ]
    for source in sources:
        print(f'working on {source}...')
        shutil.move(f'source-store/{source}/bounds.csv', f'source-store/{source}/bounds.csv.bak')
        feet_to_meters.process_source(source)

def step15():
    sources = [
        'uscobm',
        'uscofm',
        'uscogm',
        'uscoom',
        'uscopm',
        'uscoqm',
        'uscosm',
        'uscotm',
    ]
    for source in sources:
        print(f'working on {source}...')
        source_to_cog.main(source)

def step16():
    # selection was done based on visual inspection with index.html
    selected_sources = [
        'uscobm',
        'uscoc',
        'uscofm',
        'uscol',
        'uscopm',
    ]
    filepaths = sorted(glob('source-store/*/bounds.csv'))
    for filepath in filepaths:
        source = filepath.split('/')[1]
        if source not in selected_sources:
            shutil.move(filepath, f'{filepath}.bak')

if __name__ == "__main__":
    step16()
