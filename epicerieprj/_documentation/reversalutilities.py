import os
import shutil
from pathlib import Path

CONFIG_FILE = "config.txt"

def load_last_input():
    """
    Load the last used source and destination folders from the config file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
            if len(lines) >= 2:
                source = lines[0].strip()
                destination = lines[1].strip()
                return source, destination
    return "", ""

def save_last_input(source, destination):
    """
    Save the current source and destination folders to the config file.
    """
    with open(CONFIG_FILE, "w") as file:
        file.write(f"{source}\n{destination}\n")

def copy_updated_files(src, dst):
    """
    Copy files and folders from src to dst, only updating files that have changed.
    Returns a summary dictionary with statistics.
    """
    src = Path(src)
    dst = Path(dst)

    # Initialize summary statistics
    summary = {
        "files_copied": 0,
        "files_skipped": 0,
        "folders_created": 0,
        "total_size_copied": 0,  # in bytes
    }

    # Create destination folder if it doesn't exist
    if not dst.exists():
        dst.mkdir(parents=True, exist_ok=True)
        summary["folders_created"] += 1
        print(f"Created destination folder: {dst}")

    # Walk through the source directory
    for root, dirs, files in os.walk(src):
        # Get relative path to the source directory
        relative_path = Path(root).relative_to(src)
        dest_dir = dst / relative_path

        # Create subdirectories in the destination if they don't exist
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
            summary["folders_created"] += 1
            print(f"Created subdirectory: {dest_dir}")

        # Copy updated files
        for file in files:
            src_file = Path(root) / file
            dest_file = dest_dir / file

            # Check if the file needs to be updated
            if not dest_file.exists() or src_file.stat().st_mtime > dest_file.stat().st_mtime:
                shutil.copy2(src_file, dest_file)
                summary["files_copied"] += 1
                summary["total_size_copied"] += src_file.stat().st_size
                print(f"Copied: {src_file} -> {dest_file}")
            else:
                summary["files_skipped"] += 1
                print(f"Skipped (up-to-date): {src_file}")

    return summary

def restore_destination(src, dst):
    """
    Restore the destination folder to its original state by copying files from the source.
    Only overwrites files in the destination if they have changed compared to the source.
    Returns a summary dictionary with statistics.
    """
    src = Path(src)
    dst = Path(dst)

    # Initialize summary statistics
    summary = {
        "files_copied": 0,
        "files_deleted": 0,
        "files_skipped": 0,
        "folders_created": 0,
        "total_size_copied": 0,  # in bytes
    }

    # Walk through the source directory
    for root, dirs, files in os.walk(src):
        # Get relative path to the source directory
        relative_path = Path(root).relative_to(src)
        dest_dir = dst / relative_path

        # Create subdirectories in the destination if they don't exist
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
            summary["folders_created"] += 1
            print(f"Created subdirectory: {dest_dir}")

        # Copy files from source to destination (only if changed)
        for file in files:
            src_file = Path(root) / file
            dest_file = dest_dir / file

            # Check if the file has changed (size or modification time)
            if not dest_file.exists() or src_file.stat().st_size != dest_file.stat().st_size or src_file.stat().st_mtime != dest_file.stat().st_mtime:
                shutil.copy2(src_file, dest_file)
                summary["files_copied"] += 1
                summary["total_size_copied"] += src_file.stat().st_size
                print(f"Copied: {src_file} -> {dest_file}")
            else:
                summary["files_skipped"] += 1
                print(f"Skipped (unchanged): {src_file}")

    # Delete files in the destination that don't exist in the source
    for root, dirs, files in os.walk(dst):
        # Get relative path to the destination directory
        relative_path = Path(root).relative_to(dst)
        src_dir = src / relative_path

        for file in files:
            dest_file = Path(root) / file
            src_file = src_dir / file

            if not src_file.exists():
                os.remove(dest_file)
                summary["files_deleted"] += 1
                print(f"Deleted: {dest_file}")

    return summary

def display_summary(summary, operation="Archiving"):
    """
    Display a summary of the operation.
    """
    print(f"\n--- {operation} Summary ---")
    print(f"Files Copied: {summary['files_copied']}")
    if operation == "Restoration":
        print(f"Files Deleted: {summary['files_deleted']}")
    print(f"Files Skipped: {summary['files_skipped']}")
    print(f"Folders Created: {summary['folders_created']}")
    print(f"Total Size Copied: {summary['total_size_copied'] / 1024:.2f} KB")

def main():
    # Load last used source and destination folders
    last_source, last_destination = load_last_input()

    # Ask user for the operation (archive or restore)
    operation = input("Choose operation - (A)rchive or (R)estore [A]: ").strip().upper() or "A"

    if operation == "A":
        # Archive operation
        source_folder = input(f"Enter the source folder path [{last_source}]: ").strip() or last_source
        destination_folder = input(f"Enter the destination folder path [{last_destination}]: ").strip() or last_destination

        # Validate source folder
        if not os.path.exists(source_folder):
            print(f"Error: Source folder '{source_folder}' does not exist.")
            return

        # Save the current inputs for future use
        save_last_input(source_folder, destination_folder)

        # Copy updated files and get summary
        summary = copy_updated_files(source_folder, destination_folder)
        display_summary(summary, "Archiving")

    elif operation == "R":
        # Restore operation
        reverse_source, reverse_destination = last_destination, last_source
        source_folder = input(f"Enter the source folder path [{reverse_source}]: ").strip() or reverse_source
        destination_folder = input(f"Enter the destination folder path [{reverse_destination}]: ").strip() or reverse_destination

        # Validate source folder
        if not os.path.exists(source_folder):
            print(f"Error: Source folder '{source_folder}' does not exist.")
            return

        # Restore destination to its original state
        summary = restore_destination(source_folder, destination_folder)
        display_summary(summary, "Restoration")

    else:
        print("Invalid operation selected. Please choose 'A' for Archive or 'R' for Restore.")

    print("Operation completed.")

if __name__ == "__main__":
    main()