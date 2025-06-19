````markdown
# 📦 vita3k-batch-pkg-installer

Batch install `.pkg` files into **Vita3K** with `zRIF` codes — now with **GUI**, **config saving**, and **cross-platform support**.

---

## ✨ Features

- ✅ Batch installation of games, DLCs, and themes
- ✅ zRIF auto-matching from bundled TSVs
- ✅ Deletes PKG files after successful install
- ✅ Simple GUI: no command-line required
- ✅ Remembers your folders via `config.json`
- ✅ Live install logs in the GUI
- ✅ Works on Windows and Linux (via `pathlib`)

---

## 📷 Screenshot

![image](https://github.com/user-attachments/assets/3e094f68-a5de-45f8-9456-bb317e5ac399)

---

## 📥 Requirements

- **Vita3K build after [July 11, 2023](https://github.com/Vita3K/Vita3K/commit/a5b957ea2af529c9eede5056a9e6b11e293d9166)**  
  Older versions will install games to `AppData/Roaming/Vita3K` instead of your configured path.

---

## 🧠 Notes on Vita3K Paths

If you're using an **older Vita3K build**, your games may be installed to:

```
C:\Users\<You>\AppData\Roaming\Vita3K\ux0\
```

### 🔁 To fix this:
- 🔗 Create a symbolic/NTFS link from Roaming `ux0` to your emulator path
- 📦 Or move all `ux0` contents manually after batch install
- 🆙 Or update Vita3K to a post-July 11 release

---

## 🛠 How to Use

### 🎮 GUI Mode (Recommended)

1. Run `gui_launcher.py`
2. Select:
   - your PKG root folder
   - your Vita3K executable
3. Click **Start Installation**
4. Watch logs live in the bottom window

The script will:
- Auto-detect content type (Game / DLC / Theme)
- Find matching zRIF in TSVs
- Install PKG and delete it if successful
- Save any failed installs or missing zRIFs

---

### 💻 CLI Mode (Advanced)

You can still run `install_pkg.py` manually if desired:

```bash
python install_pkg.py
```

⚠️ You’ll need to hardcode paths at the top of the script.
