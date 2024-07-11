# Siril-Multisession-Stacking-Script

### This script allows you to:
1. Combine astrophoto sessions from different nights with their calibration frames.
2. Save space on your computer.

The script is still very raw, so be careful,** since its behavior when bugs occur can be very different from what it was designed for.**

## How to use
The script creates the required number of folders with sessions and the necessary frames in them, and also creates a calibrated folder. After which you need to fill all the empty folders with your images. All main folders are created in the directory in which the script is located.

## **Save images before using it!** 
Immediately report any bug or idea that you would like to fix or add to this project.

## Requirements
- colorama==0.4.6
- pysiril==0.0.15
- astropy==6.1.1
- rawpy==0.22.0
- watchdog==4.0.1
