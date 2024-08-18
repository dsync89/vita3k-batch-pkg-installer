# vita3k-batch-pkg-installer
Batch install pkg files for vita3k with zrif downloaded from NoPayStation

Note:
You must use Vita3k from release https://github.com/Vita3K/Vita3K/commit/a5b957ea2af529c9eede5056a9e6b11e293d9166 and above. So basically all release after July 11 will work as it fixes the issue where the game will always installed to your User/Roaming folder instead of the emulator path (which might be a custom path). If you refuse to update, you can either 1) create ntfs/symbolic link for the ux0 folder in your Roaming folder, or 2) move all the ux0 folder from Roaming to your Vita emulator data folder.

After batch install, make sure to click 'Refresh' button at the top right to refresh the game list!

Your input folder must be structured in the format of `Game Folder (Region)/Game.pkg` for best result.

It will store the list of game/pkg for games that failed to install, either a missing zRIF when trying to match the game or error during installation.

For the record, even using batch job, it took 3 full days to fully import all 1824 titles to a USB3 connected HDD @7200RPM. Imagine doing it manually via the GUI for each of these titles individually!

Example output after running
```
...
------------------------------------------
Summary
------------------------------------------
Finished installing 2 pkg!
Failed to install 0 pkg!
0 games with no matching zrif!
```

# Getting Started

### Microsoft Windows users

1. Download and install Python 3.x for Windows OS: 
	https://www.python.org/downloads/windows/

2. Install module "pandas" for Python by opening the Windows CMD and executing the next command:
	
       python.exe -m pip install pandas

3. Open "install_pkg.py" file in notepad, and set the right directory paths in these lines:

       # folder that contains all the .pkg games downloaded from NoPayStation
       INPUT_PKG_FOLDER = "C:\\Packages"
    
       # Path to vita3k emulator
       VITA3K_PROG_PATH = "C:\\Vita3K\\Vita3K.exe"

	(notice the usage of two backslashes "\\" to separate folder names as shown above.)

	Save the file changes when you are done.

4. Run "install_pkg.py" file and wait until the batch operation is completed.

That's all.
