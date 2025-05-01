import os
import sys

# --- Configuration ---

# File extensions to include (lowercase)
# Add or remove extensions as needed for your project
ALLOWED_EXTENSIONS = {
    '.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml',
    '.md', '.sh', '.bat', '.java', '.c', '.cpp', '.h', '.hpp', '.cs',
    '.go', '.php', '.rb', '.swift', '.kt', '.kts', '.sql', '.xml',
    '.toml', '.ini', '.cfg', '.env', '.dockerfile', '.gitignore',
    # Add specific filenames without extensions if needed (lowercase)
    'readme', 'license', 'dockerfile', 'requirements' # Added requirements based on your example
}

# Directories to exclude entirely (case-sensitive)
EXCLUDED_DIRS = {
    '.git',             # Git repository metadata
    '__pycache__',      # Python bytecode cache
    'node_modules',     # Node.js dependencies
    'venv',             # Python virtual environments (common name)
    '.venv',            # Python virtual environments (another common name)
    'env',              # Python virtual environments (another common name)
    'target',           # Rust/Java build output
    'build',            # Common build output directory
    'dist',             # Common distribution directory
    '.svn',             # Subversion metadata
    '.hg',              # Mercurial metadata
    '.idea',            # JetBrains IDE metadata
    '.vscode',          # VS Code metadata
    'bin',              # Often contains compiled binaries
    'obj',              # Often contains compiled object files
    'logs',             # Often contains runtime logs, not source code
    'temp',             # Temporary files
    'tmp',              # Temporary files
}

# Output filename
OUTPUT_FILENAME = "_combined_code_context.txt"

# --- Script Logic ---

def get_script_directory():
    """Gets the directory where the script is located."""
    # Use sys.argv[0] if __file__ is not defined (e.g., in some frozen environments)
    script_path = os.path.abspath(sys.argv[0] if hasattr(sys, 'argv') else __file__)
    return os.path.dirname(script_path)

def should_include_file(filename):
    """Checks if a file should be included based on its extension or name."""
    if not filename:
        return False
    
    base_name_lower = os.path.basename(filename).lower()
    name_part, ext = os.path.splitext(base_name_lower)

    # Check specific filenames first (case-insensitive)
    # Check if the name part (without extension) or the full name is in the allowed set
    if name_part in ALLOWED_EXTENSIONS or base_name_lower in ALLOWED_EXTENSIONS:
         return True
        
    # Check extensions (case-insensitive)
    return ext in ALLOWED_EXTENSIONS if ext else False # Ensure ext is not empty

def generate_context():
    """Scans directories and generates the combined context file."""
    script_dir = get_script_directory()
    output_filepath = os.path.join(script_dir, OUTPUT_FILENAME)
    # Use the correct way to get the script's own filename
    script_filename = os.path.basename(sys.argv[0] if hasattr(sys, 'argv') else __file__)


    print(f"Starting scan in directory: {script_dir}")
    print(f"Output will be saved to: {output_filepath}")
    print(f"Excluding directories: {', '.join(EXCLUDED_DIRS)}")
    print("-" * 30)

    all_content = []
    file_count = 0
    empty_files_found = 0

    for root, dirs, files in os.walk(script_dir, topdown=True):
        # Modify dirs in-place to prevent descending into excluded directories
        # Important: Compare based on directory name only, not the full path being built
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        relative_dir = os.path.relpath(root, script_dir)
        if relative_dir == '.':
            relative_dir = '' # Keep root paths clean

        # Skip the root directory if it's in the exclusion list (needed for top-level)
        # This check was slightly flawed before, ensure it checks the base name
        if os.path.basename(root) in EXCLUDED_DIRS and root != script_dir:
             print(f"Skipping excluded directory: {relative_dir}")
             continue

        print(f"Scanning: {os.path.join(script_dir, relative_dir) if relative_dir else script_dir}")

        for filename in files:
            # Skip the script file itself and the output file more reliably
            current_full_path = os.path.join(root, filename)
            if current_full_path == os.path.join(script_dir, script_filename):
                # print(f"  - Skipping self: {filename}") # Debug
                continue
            if current_full_path == output_filepath:
                # print(f"  - Skipping output file: {filename}") # Debug
                continue

            if should_include_file(filename):
                file_path = os.path.join(root, filename)
                relative_path = os.path.normpath(os.path.join(relative_dir, filename)).replace("\\", "/") # Normalize path separators

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    all_content.append(f"\n--- File: {relative_path} ---\n")
                    all_content.append(content) # Append the actual content, even if empty

                    # ***** THE FIX IS HERE *****
                    # Added the 'f' prefix to make it an f-string
                    all_content.append(f"\n--- End File: {relative_path} ---\n")
                    # ***************************

                    file_count += 1
                    if not content.strip(): # Check if content is empty or just whitespace
                         empty_files_found += 1
                         # print(f"  + Added (empty): {relative_path}") # Uncomment for verbose output
                    # else:
                         # print(f"  + Added: {relative_path}") # Uncomment for verbose output


                except Exception as e:
                    print(f"  ! Error reading {relative_path}: {e}")
            # else: # Uncomment for debugging excluded files
            #     relative_path = os.path.normpath(os.path.join(relative_dir, filename)).replace("\\", "/")
            #     print(f"  - Skipped: {relative_path}")


    print("-" * 30)
    print(f"Found and processed {file_count} files.")
    if empty_files_found > 0:
        print(f"  ({empty_files_found} of these files were empty or contained only whitespace)")


    if not all_content:
        print("No relevant files found to include in the context.")
        # Add input() pause on Windows if running by double-click
        if sys.platform == "win32" and sys.stdin.isatty(): # Check if running interactively
             input("Press Enter to exit...")
        return

    try:
        print(f"Writing combined context to {output_filepath}...")
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            # Join content; ensure there isn't an excessive newline at the very start if the first element starts with one
            output_string = "".join(all_content)
            if output_string.startswith('\n'):
                 output_string = output_string[1:]
            outfile.write(output_string)
        print("Successfully created context file.")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    generate_context()
    # Add input() pause on Windows if running by double-click, checking if it's interactive
    if sys.platform == "win32" and sys.stdin.isatty():
         input("Press Enter to exit...")