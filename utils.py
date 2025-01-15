import os
import traceback
import logging

from datetime import datetime
from astropy.io import fits

log_file = "script_log.txt"

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_error_to_file(exception: Exception):
    with open(log_file, "a") as f:
        f.write("\n" + "="*80 + "\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Exception: {exception}\n")
        f.write("Traceback:\n")
        traceback.print_exc(file=f)
        f.write("="*80 + "\n")

def has_spaces(path):
    return ' ' in path

def calculate_integration_time(calibrated_folder):
    total_exposure_time = 0.0
    for fits_file in os.listdir(calibrated_folder):
        if fits_file.endswith('.fits') and fits_file.startswith('r_pp_light') or fits_file.endswith(
                '.fit') and fits_file.startswith('r_pp_light'):
            file_path = os.path.join(calibrated_folder, fits_file)
            with fits.open(file_path) as hdul:
                hdr = hdul[0].header
                if 'EXPTIME' in hdr:
                    total_exposure_time += hdr['EXPTIME']
    return int(total_exposure_time)