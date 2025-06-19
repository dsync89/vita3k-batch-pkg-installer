📦 vita3k-batch-pkg-installer

Batch install .pkg files into Vita3K with zRIF codes sourced from NoPayStation TSVs — now with GUI, config saving, and cross-platform support.
✨ Features

    ✅ Automatic batch installation of .pkg games, DLCs, and themes.

    ✅ Matches Content ID to zRIF from NoPayStation .tsv files.

    ✅ Deletes installed PKG files after successful install.

    ✅ GUI for selecting .pkg folder and Vita3K executable.

    ✅ Remembers your paths using a local config.json.

    ✅ Live logs shown in GUI.

    ✅ Cross-platform: Windows & Linux compatible (via pathlib).

📷 Screenshot

    GUI mode with automatic path detection and logs:
    ![image](https://github.com/user-attachments/assets/3e094f68-a5de-45f8-9456-bb317e5ac399)

📥 Requirements

    Vita3K release after July 11, 2023
    Older versions may incorrectly install games to the Roaming directory instead of the emulator path.

📁 Folder Structure

Your PKG folder should follow this structure:

/your/pkg/folder/
├── Game Name (USA)/
│   └── PCSA00001.pkg
├── Game Name 2 (JPN)/
│   └── PCSG00002.pkg

    Folder name format helps with accurate game name detection and cleaner logs.

🧠 Notes on Vita3K

If you are not using the recommended Vita3K release or newer:

    ❗ Games may install to AppData/Roaming/Vita3K instead of your custom path.

    Workarounds:

        Use NTFS/symbolic links to redirect ux0 from Roaming.

        Manually move installed ux0 contents from Roaming to your custom Vita3K folder.

🛠 Usage
🖥 GUI Mode (Recommended)

    Launch gui_launcher.py

    Select:

        your .pkg root folder

        the Vita3K executable

    Click Start Installation

    Wait for the logs and check results!

The tool will:

    Auto-scan and sort games/DLCs/themes.

    Lookup zRIF from TSV files in /tsv.

    Install and delete .pkg files after success.

    Track failed or missing zRIF entries for review.
