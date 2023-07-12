import pandas as pd
import sys
import os
import subprocess
import re

# Provide the TSV file path and the name to lookup
TSV_FILE = 'PSV_GAMES.tsv'

# folder that contains all the .pkg games downloaded from NoPayStation
INPUT_PKG_FOLDER = "s:\\roms-staging\\vita extract"

# Path to vita3k emulator
VITA3K_PROG_PATH = "C:\\Programs\\LaunchBox\\Emulators\\Vita 3k\\Vita3K.exe"

# list that stores the game name for summary
list_pkg_install_success = [] # list of pkg that installed successfully
list_pkg_install_fail = [] # list of pkg that failed to install
list_games_no_matching_zrif = [] # list of game that failed to lookup zrif from TSV file

SEP = "------------------------------------------"

# Lookup a game zRIF using the 'Name' column in TSV file
def lookup_zrif_by_game_name(tsv_file, name):
    try:
        df = pd.read_csv(tsv_file, delimiter='\t')
        result = df[df['Name'] == name]
        if not result.empty:
            return result.iloc[0].to_dict()["zRIF"]
    except:
        return None

def lookup_zrif_by_pkg_direct_link(tsv_file, pkg_name):
    search_text = pkg_name
    field_name = 'PKG direct link'
    zrif_field = 'zRIF'

    try:
        data = pd.read_csv(tsv_file, delimiter='\t')

        # Find the row that contains a partial match for the search text in the specified field
        matching_row = data[data[field_name].str.contains(search_text, na=False)]

        if len(matching_row) > 0:
            # Get the value of the 'zRIF' field from the matching row
            zrif_value = matching_row[zrif_field].values[0]

            if len(zrif_value) > 0:
                return zrif_value
            else:
                return None
        else:
            return None
    except:
        return None


def install_pkg(vita3k_prog_path, pkg_file_path, zrif):
    global list_pkg_install_fail

    try:
        print("Installing pkg=%s, zrif=%s" % (pkg_file_path, zrif))
        executable_path = vita3k_prog_path
        arguments = [ "--pkg", pkg_file_path, "--zrif", zrif ]

        command = [executable_path] + arguments

        print("command:")
        print(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
        # Read and print the output in real-time
        for line in process.stdout:
            # uncomment to print out each line in real time
            # print(line, end='')

            # Check if the word 'exception' is present in the output
            if 'exception' in line.lower():
                # Store the command in a list
                error_command = command

                list_pkg_install_fail.append(pkg_file_path)

                # Handle the error here
                print(f"Exception occurred while executing the command: {error_command}")
                break
        # Wait for the process to finish
        process.wait()

    except subprocess.CalledProcessError as e:
        # Store the command in a list
        error_command = command

        # Handle the error here
        list_pkg_install_fail.append(pkg_file_path)
        print(f"Error occurred while executing the command: {error_command}")
        print(f"Error message: {e}")

# Extract only the 'Game Name' until just before left bracket. E.g. 'Access Denied (USA)' will return 'Access Denied'
def extract_text(text):
    # Extract text until just before the left bracket
    pattern = r"^(.*?)\s*\("
    matches = re.match(pattern, text)

    if matches:
        extracted_text = matches.group(1)
        return extracted_text
   
if __name__ == "__main__":

    # Assuming the folder has the structure of 'Game Name (Region)/game.pkg'
    for dirpath,_,filenames in os.walk(INPUT_PKG_FOLDER):
        for f in filenames:
            pkg_file_path = os.path.abspath(os.path.join(dirpath, f))
            
            folder_name = os.path.basename(os.path.dirname(pkg_file_path))
            game_name = extract_text(folder_name)
            zrif = lookup_zrif_by_pkg_direct_link(TSV_FILE, f)

            if zrif is not None:
                print("zRIF for game %s =%s" % (game_name, zrif))
                install_pkg(VITA3K_PROG_PATH, pkg_file_path, zrif)
                list_pkg_install_success.append(game_name)

            else:
                print("Failed to find zrif for game=%s" % game_name)
                list_games_no_matching_zrif.append(game_name)        


    print(SEP)
    print("Summary")
    print(SEP)
    print("Finished installing %d pkg!" % len(list_pkg_install_success))
    print("Failed to install %d pkg!" % len(list_pkg_install_fail))
    for _ in list_pkg_install_fail:
        print(_)

    print("%d games with no matching zrif!" % len(list_games_no_matching_zrif))
    for _ in list_games_no_matching_zrif:
        print(_)

# EOF