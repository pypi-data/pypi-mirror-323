""" Entry File into Dog-City that calls SL-Dog Functions and ensures file location is correct.
Last Updated by Jasper Sheeds 1/21/25 """

import os
import subprocess
from DogCity.DOGCITY import main
from dotenv import load_dotenv
from DogCity.SupportFunctions import find_file_loc, error_log, get_errors
global main_attempts
main_attempts = 0

def entry_main(attempts):
    """ Entry Method. Takes an attempt counter as a parameter to ensure user doesn't endlessly
    attempt to select the wrong file. """
    load_dotenv()
    sldog_loc = os.getenv('sl_dog_path')
    if attempts <= 3:
        try:
            is_file = os.path.isfile(sldog_loc)
            if is_file and os.path.basename(sldog_loc) == 'InfoSense SLDOG.exe':
                try:
                    subprocess.run(sldog_loc)
                    main()
                except:
                    error_log("There's been an error connecting to SLDOG.")
            else:
                find_file_loc()
                attempts += 1
                entry_main(attempts)
        except:
            try:
                find_file_loc()
                attempts += 1
                entry_main(attempts)
            except:
                error_log("There's been an error in finding file location.")
    else:
        error_log("Error: file locating attempts exceeded. Please try again.")

entry_main(main_attempts)

temp_errors = get_errors()
