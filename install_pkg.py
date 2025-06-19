import pandas as pd
import sys
import os
import subprocess
import re
from pathlib import Path

# Configuration
TSV_FILES = {
    'games': "/home/relyf/Tools/vita3k-batch-pkg-installer-main/PSV_GAMES.tsv",
    'dlcs': "/home/relyf/Tools/vita3k-batch-pkg-installer-main/PSV_DLCS.tsv",
    'themes': "/home/relyf/Tools/vita3k-batch-pkg-installer-main/PSV_THEMES.tsv"
}
INPUT_PKG_FOLDER = "/home/relyf/Tools/NPS/PKG"
VITA3K_PROG_PATH = "/home/relyf/Vita3K/Vita3K"

# Statistics tracking
stats = {
    'games': {'success': [], 'failed': [], 'no_zrif': [], 'deleted': []},
    'dlcs': {'success': [], 'failed': [], 'no_zrif': [], 'deleted': []},
    'themes': {'success': [], 'failed': [], 'no_zrif': [], 'deleted': []}
}

SEP = "------------------------------------------"

def get_content_type(content_id):
    """Determine content type based on Content ID pattern"""
    if not content_id:
        return 'unknown'
    
    # Games typically end with _00
    if content_id.endswith('_00'):
        return 'games'
    # DLCs typically have patterns like _01, _02, etc. or contain 'DLC'
    elif re.search(r'_\d{2}$', content_id) and not content_id.endswith('_00'):
        return 'dlcs'
    elif 'DLC' in content_id.upper():
        return 'dlcs'
    # Themes often contain 'THEME' or have specific patterns
    elif 'THEME' in content_id.upper():
        return 'themes'
    else:
        return 'games'  # Default to games if uncertain

def lookup_zrif_by_content_id(content_id, content_type):
    """Lookup zRIF using Content ID from appropriate TSV file"""
    tsv_file = TSV_FILES.get(content_type)
    if not tsv_file or not os.path.exists(tsv_file):
        print(f"Warning: TSV file {tsv_file} for {content_type} not found")
        return None
    
    try:
        df = pd.read_csv(tsv_file, delimiter='\t')
        result = df[df['Content ID'] == content_id]
        if not result.empty:
            zrif = result.iloc[0]['zRIF']
            return zrif if pd.notna(zrif) and len(str(zrif).strip()) > 0 else None
        return None
    except Exception as e:
        print(f"Error reading TSV file {tsv_file}: {e}")
        return None

def lookup_zrif_by_pkg_filename(pkg_filename, content_type):
    """Fallback method: lookup by PKG filename in direct link from appropriate TSV"""
    tsv_file = TSV_FILES.get(content_type)
    if not tsv_file or not os.path.exists(tsv_file):
        return None, None
    
    try:
        df = pd.read_csv(tsv_file, delimiter='\t')
        
        # Remove file extension for matching
        pkg_name_no_ext = os.path.splitext(pkg_filename)[0]
        
        # Try exact filename match first
        matching_rows = df[df['PKG direct link'].str.contains(pkg_filename, na=False, case=False)]
        
        if matching_rows.empty:
            # Try without extension
            matching_rows = df[df['PKG direct link'].str.contains(pkg_name_no_ext, na=False, case=False)]
        
        if not matching_rows.empty:
            zrif = matching_rows.iloc[0]['zRIF']
            content_id = matching_rows.iloc[0]['Content ID']
            return zrif if pd.notna(zrif) and len(str(zrif).strip()) > 0 else None, content_id
        
        return None, None
    except Exception as e:
        print(f"Error in filename lookup for {tsv_file}: {e}")
        return None, None

def try_all_tsv_files_for_lookup(content_id, pkg_filename):
    """Try to find zRIF in any TSV file if content type detection fails"""
    for content_type in ['games', 'dlcs', 'themes']:
        # Try Content ID lookup first
        zrif = lookup_zrif_by_content_id(content_id, content_type)
        if zrif:
            return zrif, content_type
        
        # Try filename lookup as fallback
        zrif, found_content_id = lookup_zrif_by_pkg_filename(pkg_filename, content_type)
        if zrif:
            return zrif, content_type
    
    return None, None

def extract_content_id_from_pkg(pkg_path):
    """
    Try to extract Content ID from PKG file path or name
    This is a heuristic approach - you might need to adjust based on your file naming
    """
    pkg_filename = os.path.basename(pkg_path)
    
    # Common patterns for Content ID in filenames
    patterns = [
        r'([A-Z]{4}\d{5}_\d{2})',  # Standard format like PCSA00001_00
        r'([A-Z]{2}\d{4}-[A-Z]{4}\d{5}_\d{2})',  # With region prefix
    ]
    
    for pattern in patterns:
        match = re.search(pattern, pkg_filename)
        if match:
            return match.group(1)
    
    return None

def delete_pkg_file(pkg_file_path, content_type):
    """Safely delete PKG file after successful installation"""
    try:
        pkg_filename = os.path.basename(pkg_file_path)
        print(f"🗑️  Deleting successfully installed PKG: {pkg_filename}")
        os.remove(pkg_file_path)
        stats[content_type]['deleted'].append(pkg_filename)
        print(f"✓ Successfully deleted: {pkg_filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to delete {pkg_filename}: {e}")
        return False

def install_pkg(vita3k_prog_path, pkg_file_path, zrif, content_type):
    """Install PKG with proper error handling and Linux compatibility"""
    try:
        print(f"Installing {content_type[:-1]}: {os.path.basename(pkg_file_path)}")
        print(f"zRIF: {zrif}")
        
        # Ensure the executable is executable
        if not os.access(vita3k_prog_path, os.X_OK):
            print(f"Warning: {vita3k_prog_path} is not executable. Attempting to make it executable...")
            try:
                os.chmod(vita3k_prog_path, 0o755)
            except Exception as e:
                print(f"Failed to make executable: {e}")
                stats[content_type]['failed'].append(os.path.basename(pkg_file_path))
                return False
        
        # Build command
        command = [vita3k_prog_path, "--pkg", pkg_file_path, "--zrif", zrif]
        
        print(f"Command: {' '.join(command)}")
        
        # Set up environment for Linux compatibility
        env = os.environ.copy()
        env['LC_ALL'] = 'C'  # Ensure consistent locale
        
        # Execute with timeout to prevent hanging
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env
        )
        
        try:
            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
            
            # Check for success/failure indicators
            if process.returncode == 0:
                if 'exception' not in stdout.lower() and 'error' not in stderr.lower():
                    stats[content_type]['success'].append(os.path.basename(pkg_file_path))
                    print(f"✓ Successfully installed {os.path.basename(pkg_file_path)}")
                    
                    # Auto-delete the PKG file after successful installation
                    delete_pkg_file(pkg_file_path, content_type)
                    
                    return True
            
            # If we get here, something went wrong
            print(f"✗ Installation failed for {os.path.basename(pkg_file_path)}")
            if stderr:
                print(f"Error output: {stderr}")
            stats[content_type]['failed'].append(os.path.basename(pkg_file_path))
            return False
            
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"✗ Installation timed out for {os.path.basename(pkg_file_path)}")
            stats[content_type]['failed'].append(os.path.basename(pkg_file_path))
            return False
            
    except Exception as e:
        print(f"✗ Exception during installation of {os.path.basename(pkg_file_path)}: {e}")
        stats[content_type]['failed'].append(os.path.basename(pkg_file_path))
        return False

def extract_game_name(folder_name):
    """Extract clean game name from folder name"""
    # Remove region info in parentheses
    pattern = r"^(.*?)\s*\("
    match = re.match(pattern, folder_name)
    return match.group(1).strip() if match else folder_name.strip()

def extract_content_id_from_pkg(pkg_path):
    """
    Extract Content ID from PKG filename
    Example: UP9000-PCSA00011_00-PDUSAC00ARMYPACK.pkg -> UP9000-PCSA00011_00-PDUSAC00ARMYPACK
    """
    pkg_filename = os.path.basename(pkg_path)
    
    # Remove .pkg extension
    content_id = os.path.splitext(pkg_filename)[0]
    
    return content_id

def process_pkg_files():
    """Process all PKG files in the input directory - Games first, then DLCs, then Themes"""
    if not os.path.exists(INPUT_PKG_FOLDER):
        print(f"Error: Input folder {INPUT_PKG_FOLDER} does not exist!")
        return
    
    if not os.path.exists(VITA3K_PROG_PATH):
        print(f"Error: Vita3K executable {VITA3K_PROG_PATH} does not exist!")
        return
    
    # Check which TSV files exist
    existing_tsv_files = []
    for content_type, tsv_file in TSV_FILES.items():
        if os.path.exists(tsv_file):
            existing_tsv_files.append(content_type)
        else:
            print(f"Warning: {tsv_file} not found - {content_type} won't be processed")
    
    if not existing_tsv_files:
        print("Error: No TSV files found!")
        return
    
    print(f"Available TSV files for: {', '.join(existing_tsv_files)}")
    
    # Find all PKG files and categorize them
    pkg_files_by_type = {'games': [], 'dlcs': [], 'themes': []}
    
    for root, dirs, files in os.walk(INPUT_PKG_FOLDER):
        for file in files:
            if file.lower().endswith('.pkg'):
                pkg_file_path = os.path.join(root, file)
                
                # Extract content ID to determine type
                content_id = extract_content_id_from_pkg(pkg_file_path)
                content_type = get_content_type(content_id) if content_id else 'games'
                
                pkg_files_by_type[content_type].append(pkg_file_path)
    
    total_files = sum(len(files) for files in pkg_files_by_type.values())
    print(f"Found {total_files} PKG files:")
    print(f"  Games: {len(pkg_files_by_type['games'])}")
    print(f"  DLCs: {len(pkg_files_by_type['dlcs'])}")
    print(f"  Themes: {len(pkg_files_by_type['themes'])}")
    print(SEP)
    
    # Process in order: Games first, then DLCs, then Themes
    install_order = ['games', 'dlcs', 'themes']
    
    for content_type in install_order:
        if not pkg_files_by_type[content_type]:
            continue
            
        print(f"\n{'='*60}")
        print(f"INSTALLING {content_type.upper()}")
        print(f"{'='*60}")
        
        for pkg_file_path in pkg_files_by_type[content_type]:
            pkg_filename = os.path.basename(pkg_file_path)
            folder_name = os.path.basename(os.path.dirname(pkg_file_path))
            game_name = extract_game_name(folder_name)
            
            print(f"Processing {content_type[:-1]}: {pkg_filename}")
            
            # Extract Content ID
            content_id = extract_content_id_from_pkg(pkg_file_path)
            zrif = None
            
            if content_id:
                print(f"Content ID: {content_id}")
                # Try lookup in the appropriate TSV file
                zrif = lookup_zrif_by_content_id(content_id, content_type)
            
            # If primary lookup failed, try all TSV files
            if not zrif:
                print("Primary lookup failed, searching all TSV files...")
                zrif, found_type = try_all_tsv_files_for_lookup(content_id, pkg_filename)
                if found_type and found_type != content_type:
                    print(f"Found in {found_type} TSV file instead of {content_type}")
                    content_type = found_type
            
            if zrif:
                print(f"Found zRIF for {content_type[:-1]}: {game_name}")
                install_pkg(VITA3K_PROG_PATH, pkg_file_path, zrif, content_type)
            else:
                print(f"✗ No zRIF found for {content_type[:-1]}: {game_name}")
                stats[content_type]['no_zrif'].append(game_name)
            
            print(SEP)

def print_summary():
    """Print installation summary"""
    print("\n" + "=" * 60)
    print("INSTALLATION SUMMARY")
    print("=" * 60)
    
    total_success = sum(len(stats[t]['success']) for t in stats)
    total_failed = sum(len(stats[t]['failed']) for t in stats)
    total_no_zrif = sum(len(stats[t]['no_zrif']) for t in stats)
    total_deleted = sum(len(stats[t]['deleted']) for t in stats)
    
    print(f"Total processed: {total_success + total_failed + total_no_zrif}")
    print(f"Successfully installed: {total_success}")
    print(f"Failed to install: {total_failed}")
    print(f"No zRIF found: {total_no_zrif}")
    print(f"PKG files deleted: {total_deleted}")
    print()
    
    for content_type in ['games', 'dlcs', 'themes']:
        if any(stats[content_type].values()):
            print(f"{content_type.upper()}:")
            print(f"  ✓ Successful: {len(stats[content_type]['success'])}")
            print(f"  ✗ Failed: {len(stats[content_type]['failed'])}")
            print(f"  ? No zRIF: {len(stats[content_type]['no_zrif'])}")
            print(f"  🗑️  Deleted: {len(stats[content_type]['deleted'])}")
            
            if stats[content_type]['failed']:
                print(f"  Failed {content_type}:")
                for item in stats[content_type]['failed']:
                    print(f"    - {item}")
            
            if stats[content_type]['no_zrif']:
                print(f"  {content_type.title()} without zRIF:")
                for item in stats[content_type]['no_zrif']:
                    print(f"    - {item}")
            
            if stats[content_type]['deleted']:
                print(f"  Deleted {content_type}:")
                for item in stats[content_type]['deleted']:
                    print(f"    - {item}")
            print()

if __name__ == "__main__":
    print("Vita3K PKG Installer with Auto-Delete")
    print("Supports Games, DLCs, and Themes")
    print("⚠️  PKG files will be automatically deleted after successful installation!")
    print(SEP)
    
    try:
        process_pkg_files()
        print_summary()
    except KeyboardInterrupt:
        print("\n\nInstallation interrupted by user")
        print_summary()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print_summary()

# EOF