import subprocess

def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}\nError: {result.stderr.decode()}")
        exit(result.returncode)
    return result.stdout.decode()

def check_install_python():
    """Check if Python3 is installed, if not, install it."""
    try:
        run_command("python3 --version")
    except:
        print("Python3 is not installed. Installing Python3...")
        run_command("apt update && apt install -y python3")

def prompt_user(prompt):
    """Prompt the user for input."""
    return input(prompt)

def main():
    # Check and install Python3 if necessary
    check_install_python()

    # List available drives
    print("Listing available drives:")
    print(run_command("fdisk -l"))

    # Prompt for necessary information
    encrypted_drive = prompt_user("Enter the source drive (e.g., /dev/sda): ")
    is_encrypted = prompt_user("Is the device encrypted with BitLocker? (yes/no): ").strip().lower()
    external_drive = prompt_user("Enter the external drive (e.g., /dev/sdb1): ")
    
    if is_encrypted == 'yes':
        recovery_key = prompt_user("Enter the BitLocker recovery key: ")
        # Create necessary directories
        run_command("mkdir -p /mnt/bitlocker /mnt/decrypted /mnt/Destination/")

        # Install dislocker
        run_command("apt update && apt install -y dislocker")

        # Decrypt the BitLocker drive
        dislocker_command = f"dislocker -r -V {encrypted_drive} -p{recovery_key} -- /mnt/bitlocker"
        run_command(dislocker_command)

        # Mount the decrypted volume
        run_command("mount -o loop /mnt/bitlocker/dislocker-file /mnt/decrypted")

        source_mount_point = "/mnt/decrypted"
    else:
        # Create necessary directories
        run_command("mkdir -p /mnt/Source /mnt/Destination")

        # Mount the source drive
        run_command(f"mount {encrypted_drive} /mnt/Source")

        source_mount_point = "/mnt/Source"

    # Mount the external hard drive
    run_command(f"mount {external_drive} /mnt/Destination")

    # Use rsync to copy files
    run_command(f"rsync -a {source_mount_point}/ /mnt/Destination/")

    # Unmount all paths
    run_command("umount /mnt/Destination")
    if is_encrypted == 'yes':
        run_command("umount /mnt/bitlocker")
        run_command("umount /mnt/decrypted")
    else:
        run_command("umount /mnt/Source")

    print("Process completed successfully. You can now safely remove the external drive and the USB drive.")

if __name__ == "__main__":
    main()
