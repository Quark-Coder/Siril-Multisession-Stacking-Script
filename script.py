import os
import shutil
import tkinter
import rawpy

from astropy.io import fits
from pysiril.siril import *
from pysiril.wrapper import *
from tkinter.filedialog import askopenfilename
from colorama import init as colorama_init
from colorama import Fore
from colorama import Back
from colorama import Style
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

colorama_init()

class CleanupHandler(FileSystemEventHandler):
    def __init__(self, directory, alt_prefix):
        self.directory = directory
        self.alt_prefix = alt_prefix

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            batch_cleanup(self.alt_prefix, file_path)


def start_watchdog(directory, alt_prefix):
    event_handler = CleanupHandler(directory, alt_prefix)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    return observer


def master_bias(cmd, bias_dir, process_dir):
    cmd.cd(bias_dir)
    cmd.convert('bias', out=process_dir)
    cmd.cd(process_dir)
    cmd.stack('bias', type='rej', sigma_low=3, sigma_high=3, norm='no')
    cleanup(process_dir, 'bias')


def master_flat(cmd, flat_dir, process_dir, use_bias):
    cmd.cd(flat_dir)
    cmd.convert('flat', out=process_dir)
    cmd.cd(process_dir)
    if use_bias:
        cmd.calibrate('flat', bias='bias_stacked')
        cmd.stack('pp_flat', type='rej', sigma_low=3, sigma_high=3, norm='mul')
        cleanup(process_dir, 'pp_flat')
    else:
        cmd.stack('flat', type='rej', sigma_low=3, sigma_high=3, norm='mul')
    cleanup(process_dir, 'flat')


def display_commands(main=False):
    if main:
        print("List of main processing commands:")
        print("  dso - for deep sky stacking")
        print(" ")
    print("Script related commands:")
    print("  reset - for resetting the settings.")
    print("  info - how script works.")


def handle_command(command, settings_file):
    if command == 'dso':
        print(Fore.CYAN + "Deep sky object stacking selected." + Style.RESET_ALL)
        return True
    elif command == 'reset':
        print(Fore.RED + "Resetting all settings..." + Style.RESET_ALL)
        os.remove(settings_file)
        os.system("pause")
        exit()
    elif command == 'info':
        print("1. The script creates empty session folders, inside of which are all the frames that you have selected.")
        print("2. The script calibrates light frames from each session and moves them to the calibrated folder.")
        print("3. The script performs registration and stacking of calibrated light frames in the calibrated folder.")
        print("4. The script exports to the main stacked image folder and deletes all temporary files.")
        print(" ")
    return False

def master_dark(cmd, dark_dir, process_dir):
    cmd.cd(dark_dir)
    cmd.convert('dark', out=process_dir)
    cmd.cd(process_dir)
    cmd.stack('dark', type='rej', sigma_low=3, sigma_high=3, norm='no')
    cleanup(process_dir, 'dark')


def has_spaces(path):
    return ' ' in path


def cleanup(directory, prefix):
    for file in os.listdir(directory):
        if file.startswith(prefix + '_') and not file.startswith(prefix + '_stacked') and (
                file.endswith('.fit') or file.endswith(
            '.FIT') or file == prefix + '_.seq' or file == prefix + '_conversion.txt'):
            print(Fore.GREEN + "CLEANING " + file + Style.RESET_ALL)
            os.remove(os.path.join(directory, file))
        if prefix == 'all':
            print(Fore.GREEN + "CLEANING " + file + Style.RESET_ALL)
            os.remove(os.path.join(directory, file)) # vulnerable place


def batch_cleanup(alt_prefix, file_path):
    directory, filename = os.path.split(file_path)
    new_filename = filename.replace(alt_prefix + '_', '', 1)
    delete_path = os.path.join(directory, new_filename)
    print(Fore.CYAN + "BATCH-CLEANING " + new_filename + Style.RESET_ALL)
    if not delete_path.endswith('.seq'):
        os.remove(delete_path)


def setup_directories():
    workdir = os.getcwd()

    if has_spaces(workdir):
        print(Fore.RED + "Space(-s) were detected in the path to your working directory. Please remove "
                         "them before using the script.")
        os.system('pause')
        exit()

    if not os.path.isdir(workdir + "/calibrated"):
        session_count = int(input(Fore.YELLOW + "Enter the number of sessions: " + Style.RESET_ALL))
        use_darks = input(Fore.YELLOW + "Use dark frames? (y/n): " + Style.RESET_ALL).lower() == 'y'
        use_flats = input(Fore.YELLOW + "Use flat frames? (y/n): " + Style.RESET_ALL).lower() == 'y'
        use_bias = input(Fore.YELLOW + "Use bias frames? (y/n): " + Style.RESET_ALL).lower() == 'y'

        if not os.path.isdir(workdir + "/session_1"):
            for session_num in range(1, session_count + 1):
                session_dir = os.path.join(workdir, f"session_{session_num}")
                os.makedirs(session_dir)
                if use_darks:
                    os.makedirs(os.path.join(session_dir, "darks"))
                if use_flats:
                    os.makedirs(os.path.join(session_dir, "flats"))
                if use_bias:
                    os.makedirs(os.path.join(session_dir, "biases"))
                os.makedirs(os.path.join(session_dir, "lights"))
        os.makedirs(os.path.join(workdir, "calibrated"))
        print(Fore.RED + "Add files to folders!" + Style.RESET_ALL)
        proceed = input(Fore.YELLOW + "Proceed? (y/n): " + Style.RESET_ALL).lower() == 'y'

        if not proceed:
            exit()

    return workdir


has_rgb_images = False
has_mono_images = False

def check_directories(workdir):
    need_exit = False

    for folder in os.listdir(workdir):
        if folder.startswith('session_'):
            folder_path = os.path.join(workdir, folder)
            folder_empty = False

            lights_folder_path = os.path.join(folder_path, "lights")

            if not os.path.exists(lights_folder_path):
                print(Fore.RED + f"{folder}: Lights folder does not exist!" + Style.RESET_ALL)
                folder_empty = True
            elif not os.listdir(lights_folder_path):
                print(Fore.RED + f"{folder}: Lights folder is empty! Add files to it!" + Style.RESET_ALL)
                folder_empty = True
            else:
                for file in os.listdir(lights_folder_path):
                    if file.endswith(('.fit', '.FIT', '.fits', '.FITS', '.raw', '.nef', '.cr2', '.cr3', '.arw')):
                        file_path = os.path.join(lights_folder_path, file)
                        try:
                            if file.endswith(('.fit', '.FIT', '.fits', '.FITS')):
                                with fits.open(file_path) as hdul:
                                    data = hdul[0].data
                                    if len(data.shape) == 3 and data.shape[0] == 3:
                                        global has_rgb_images
                                        has_rgb_images = True
                                    elif len(data.shape) == 2:
                                        global has_mono_images
                                        has_mono_images = True
                            elif file.endswith(('.raw', '.nef', '.cr2', '.cr3', '.arw')):
                                with rawpy.imread(file_path):
                                    has_rgb_images = True
                        except Exception as e:
                            print(Fore.RED + f"Error reading {file}: {e}" + Style.RESET_ALL)

            flats_folder_path = os.path.join(folder_path, "flats")
            if os.path.isdir(flats_folder_path):
                if not os.listdir(flats_folder_path):
                    print(Fore.RED + f"{folder}: Flats folder is empty! Add files to it!" + Style.RESET_ALL)
                    folder_empty = True

            darks_folder_path = os.path.join(folder_path, "darks")
            if os.path.isdir(darks_folder_path):
                if not os.listdir(darks_folder_path):
                    print(Fore.RED + f"{folder}: Darks folder is empty! Add files to it!" + Style.RESET_ALL)
                    folder_empty = True

            biases_folder_path = os.path.join(folder_path, "biases")
            if os.path.isdir(biases_folder_path):
                if not os.listdir(biases_folder_path):
                    print(Fore.RED + f"{folder}: Biases folder is empty! Add files to it!" + Style.RESET_ALL)
                    folder_empty = True

            if folder_empty:
                need_exit = True

    if need_exit:
        os.system("pause")
        exit()

    if has_rgb_images and has_mono_images:
        print(
            Fore.RED + "Error: Both RGB and Monochrome images detected in lights "
                       "folders." + Style.RESET_ALL)
        os.system("pause")
        exit()

    if has_rgb_images:
        print(Fore.RED + "R" + Fore.GREEN + "G" + Fore.BLUE + "B" + Fore.WHITE + " images detected." + Style.RESET_ALL)

    if has_mono_images:
        print(Back.WHITE + Fore.BLACK + "Monochrome images detected." + Style.RESET_ALL)

def main():
    dir_path = os.path.join(os.environ['APPDATA'], 'multisession-script')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    settings_file = os.path.join(dir_path, "settings.txt")
    default_siril_path = "C:\\Program Files\\Siril\\bin\\siril.exe"

    if os.path.isfile(default_siril_path):
        with open(settings_file, "w", encoding='utf-8') as settings:
            settings.write(default_siril_path + "\n")
        os.system('cls')

    if not os.path.isfile(settings_file):
        print(
            Fore.RED + "No SiriL.exe found in default location. Select SiriL.exe in installed directory."
            + Style.RESET_ALL)
        while True:
            path = askopenfilename(title='Select SiriL.exe')
            if not path:
                print(Fore.RED + "No Siril executable selected. Exiting..." + Style.RESET_ALL)
                os.system("pause")
                exit()
            if "Siril.exe" in path or "siril.exe" in path:
                bits_select = input(Fore.YELLOW + "Use 16 or 32 bits processing? 32 recommended \n"
                                                  "Choose the first one if you have less space (16/32): "
                                    + Style.RESET_ALL)

                with open(settings_file, "w", encoding='utf-8') as settings:
                    settings.write(path + "\n")
                    settings.write(bits_select + "_bits")
                os.system('cls')

                break
            else:
                tkinter.messagebox.showerror(title="Error", message="This is not a Siril.exe or siril.exe")

    print(Fore.BLUE + "Quark-Coder multi-session processing script" + Style.RESET_ALL)
    print(Fore.RED + "THIS SCRIPT IS UNDER TESTING. SAVE THE IMAGES BEFORE USING THE SCRIPT!" + Style.RESET_ALL)
    print(" ")

    command = ""
    while command not in ['dso', 'reset', 'stack']:
        if not os.path.isdir(os.path.join(os.getcwd(), "calibrated")):
            display_commands(main=True)
        else:
            display_commands()
            print("  stack - for stacking")

        print(" ")
        command = input(Fore.YELLOW + "Write a command: " + Style.RESET_ALL).strip().lower()
        if handle_command(command, settings_file):
            break

    if command == 'stack':
        print(Fore.CYAN + "Stacking started." + Style.RESET_ALL)

    workdir = setup_directories()

    if os.path.isdir(os.path.join(workdir, "calibrated")):
        check_directories(workdir)

        try:
            with open(settings_file, "r", encoding='utf-8') as settings:
                lines = settings.readlines()
                final_path = lines[0].strip()
                bit_depth = lines[1].strip().replace('_bits', '')

            app = Siril(siril_exe=final_path)
            cmd = Wrapper(app)
            app.Open()

            if bit_depth == '16':
                cmd.set16bits()
            elif bit_depth == '32':
                cmd.set32bits()

            cmd.setext('fit')
            for folder in os.listdir(workdir):
                if folder.startswith('session_'):
                    session_dir = os.path.join(workdir, folder)
                    os.chdir(session_dir)
                    process_dir = os.path.join(session_dir, "process")

                    has_flats = os.path.isdir(os.path.join(session_dir, "flats"))
                    has_darks = os.path.isdir(os.path.join(session_dir, "darks"))
                    has_biases = os.path.isdir(os.path.join(session_dir, "biases"))

                    if not os.path.exists(process_dir):
                        os.makedirs(process_dir)

                    if has_flats and has_biases:
                        master_bias(cmd, os.path.join(session_dir, 'biases'), process_dir)
                        master_flat(cmd, os.path.join(session_dir, 'flats'), process_dir, True)
                    elif has_flats:
                        master_flat(cmd, os.path.join(session_dir, 'flats'), process_dir, False)

                    if has_darks:
                        master_dark(cmd, os.path.join(session_dir, 'darks'), process_dir)

                    cmd.cd(os.path.join(session_dir, 'lights'))
                    cmd.convert('light', out=process_dir)
                    cmd.cd(process_dir)

                    if has_rgb_images:
                        if has_flats and has_biases and has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', dark='dark_stacked', flat='pp_flat_stacked', cc='dark', cfa=True,
                                          equalize_cfa=True, debayer=True)
                            observer.stop()
                            observer.join()

                        elif has_flats and has_biases and not has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', flat='pp_flat_stacked', cfa=True, equalize_cfa=True, debayer=True)
                            observer.stop()
                            observer.join()

                        elif has_flats and not has_biases and has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', flat='flat_stacked', dark='dark_stacked', cc='dark', cfa=True,
                                          equalize_cfa=True, debayer=True)
                            observer.stop()
                            observer.join()

                        elif has_flats and not has_biases and not has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', flat='flat_stacked', cfa=True, equalize_cfa=True, debayer=True)
                            observer.stop()
                            observer.join()

                        elif not has_flats and not has_biases and has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', dark='dark_stacked', cc='dark', cfa=True, equalize_cfa=True,
                                          debayer=True)
                            observer.stop()
                            observer.join()

                        elif not has_flats and not has_biases and not has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', cfa=True, equalize_cfa=True, debayer=True)
                            observer.stop()
                            observer.join()

                    if has_mono_images:
                        if has_flats and has_biases and has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', dark='dark_stacked', flat='pp_flat_stacked', cc='dark', cfa=True,
                                          equalize_cfa=True, debayer=False)
                            observer.stop()
                            observer.join()

                        elif has_flats and has_biases and not has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', flat='pp_flat_stacked', cfa=True, equalize_cfa=True, debayer=False)
                            observer.stop()
                            observer.join()

                        elif has_flats and not has_biases and has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', flat='flat_stacked', dark='dark_stacked', cc='dark', cfa=True,
                                          equalize_cfa=True, debayer=False)
                            observer.stop()
                            observer.join()

                        elif has_flats and not has_biases and not has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', flat='flat_stacked', cfa=True, equalize_cfa=True, debayer=False)
                            observer.stop()
                            observer.join()

                        elif not has_flats and not has_biases and has_darks:
                            observer = start_watchdog(process_dir, 'pp')
                            cmd.calibrate('light', dark='dark_stacked', cc='dark', cfa=True, equalize_cfa=True,
                                          debayer=False)
                            observer.stop()
                            observer.join()

                        # elif not has_flats and not has_biases and not has_darks:
                        #     cmd.calibrate('light', cfa=True, equalize_cfa=True, debayer=False)
                        #     cleanup(process_dir, 'light')
                        # A mono image that does not have any calibration frames cannot be
                        # calibrated, so it is immediately sent to calibrated and stacked

            calibrated_folder = os.path.join(workdir, 'calibrated')

            existing_files = os.listdir(calibrated_folder)
            max_number = 0
            for file_name in existing_files:
                if file_name.startswith('pp_light') and file_name.endswith('.fit'):
                    number_str = file_name.split('_')[-1].split('.')[0]
                    try:
                        number = int(number_str)
                        if number > max_number:
                            max_number = number
                    except ValueError:
                        continue

            for session_folder in sorted(os.listdir(workdir)):
                session_path = os.path.join(workdir, session_folder)
                if os.path.isdir(session_path):
                    process_path = os.path.join(session_path, 'process')
                    if os.path.isdir(process_path):
                        for file_name in sorted(os.listdir(process_path)):
                            if file_name.startswith('pp_light') and file_name.endswith('.fit'):
                                src_file = os.path.join(process_path, file_name)
                                max_number += 1
                                new_file_name = f"pp_light_{max_number:05d}.fit"
                                dest_file = os.path.join(calibrated_folder, new_file_name)
                                shutil.move(src_file, dest_file)
                                print(Fore.GREEN + f'File {src_file} moved to {dest_file}' + Style.RESET_ALL)


            cmd.cd(calibrated_folder)

            observer = start_watchdog(calibrated_folder, 'r')
            cmd.register('pp_light')
            observer.stop()
            observer.join()

            total_exposure_time = 0.0
            for fits_file in os.listdir(calibrated_folder):
                if fits_file.endswith('.fits') and fits_file.startswith('r_pp_light') or fits_file.endswith(
                        '.fit') and fits_file.startswith('r_pp_light'):
                    file_path = os.path.join(calibrated_folder, fits_file)
                    with fits.open(file_path) as hdul:
                        hdr = hdul[0].header
                        if 'EXPTIME' in hdr:
                            total_exposure_time += hdr['EXPTIME']
            total_exposure_time_int = int(total_exposure_time)

            cmd.stack('r_pp_light', type='rej', sigma_low=3, sigma_high=3, norm='addscale', output_norm=True,
                      rgb_equal=True, out='../' + 'result_' + str(total_exposure_time_int) + 's')

            cleanup(calibrated_folder, 'all')

            app.Close()

        except Exception as e:
            print(Fore.RED + f"\n**** ERROR *** {str(e)}\n" + Style.RESET_ALL)

    os.system("pause")


if __name__ == "__main__":
    main()
