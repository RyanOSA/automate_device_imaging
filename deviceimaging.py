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
    encrypted_drive = prompt_user("Enter the encrypted drive (e.g., /dev/sda): ")
    recovery_key = prompt_user("Enter the BitLocker recovery key: ")
    external_drive = prompt_user("Enter the external drive (e.g., /dev/sdb1): ")
    
    # Create necessary directories
    run_command("mkdir -p /mnt/bitlocker /mnt/decrypted /mnt/Destination")

    # Install dislocker
    run_command("apt update && apt install -y dislocker")

    # Decrypt the BitLocker drive
    dislocker_command = f"dislocker -r -V {encrypted_drive} -p{recovery_key} -- /mnt/bitlocker"
    run_command(dislocker_command)

    # Mount the decrypted volume
    run_command("mount -o loop /mnt/bitlocker/dislocker-file /mnt/decrypted")

    # Mount the external hard drive
    run_command(f"mount {external_drive} /mnt/Destination")

    # Use rsync to copy files
    run_command("rsync -a /mnt/decrypted/ /mnt/Destination/")

    # Unmount all paths
    run_command("umount /mnt/Destination")
    run_command("umount /mnt/bitlocker")
    run_command("umount /mnt/decrypted")

    print("Process completed successfully. You can now safely remove the external drive and the USB drive.")

if __name__ == "__main__":
    main()
