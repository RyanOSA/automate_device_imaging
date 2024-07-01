import subprocess

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result.check_returncode()  # This will raise CalledProcessError if the command failed
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\nError: {e.stderr.decode()}")
        raise

def check_install_python():
    """Check if Python3 is installed, if not, install it."""
    try:
        run_command("python3 --version")
    except:
        print("Python3 is not installed. Installing Python3...")
        try:
            run_command("apt update && apt install -y python3")
        except:
            print("Failed to install Python3.")
            raise

def prompt_user(prompt):
    """Prompt the user for input."""
    return input(prompt)

def main():
    # Check and install Python3 if necessary
    try:
        check_install_python()
    except Exception as e:
        print(f"Error during Python3 check/install: {e}")
        return

    # List available drives
    try:
        print("Listing available drives:")
        print(run_command("fdisk -l"))
    except Exception as e:
        print(f"Error listing drives: {e}")
        return

    # Prompt for necessary information
    encrypted_drive = prompt_user("Enter the source drive (e.g., /dev/sda): ")
    is_encrypted = prompt_user("Is the device encrypted with BitLocker? (yes/no): ").strip().lower()
    external_drive = prompt_user("Enter the external drive (e.g., /dev/sdb1): ")
    
    if is_encrypted == 'yes':
        recovery_key = prompt_user("Enter the BitLocker recovery key: ")
        try:
            # Create necessary directories
            run_command("mkdir -p /mnt/bitlocker /mnt/decrypted /mnt/Destination")
        except Exception as e:
            print(f"Error creating directories: {e}")
            return

        try:
            # Install dislocker
            run_command("apt update && apt install -y dislocker")
        except Exception as e:
            print(f"Error installing dislocker: {e}")
            return

        try:
            # Decrypt the BitLocker drive
            dislocker_command = f"dislocker -r -V {encrypted_drive} -p{recovery_key} -- /mnt/bitlocker"
            run_command(dislocker_command)
        except Exception as e:
            print(f"Error decrypting BitLocker drive: {e}")
            return

        try:
            # Mount the decrypted volume
            run_command("mount -o loop /mnt/bitlocker/dislocker-file /mnt/decrypted")
        except Exception as e:
            print(f"Error mounting decrypted volume: {e}")
            return

        source_mount_point = "/mnt/decrypted"
    else:
        try:
            # Create necessary directories
            run_command("mkdir -p /mnt/Source /mnt/Destination")
        except Exception as e:
            print(f"Error creating directories: {e}")
            return

        try:
            # Mount the source drive
            run_command(f"mount {encrypted_drive} /mnt/Source")
        except Exception as e:
            print(f"Error mounting source drive: {e}")
            return

        source_mount_point = "/mnt/Source"

    try:
        # Mount the external hard drive
        run_command(f"mount {external_drive} /mnt/Destination")
    except Exception as e:
        print(f"Error mounting external drive: {e}")
        return

    try:
        # Use rsync to copy files
        run_command(f"rsync -a {source_mount_point}/ /mnt/Destination/")
    except Exception as e:
        print(f"Error copying files with rsync: {e}")
        return

    try:
        # Unmount all paths
        run_command("umount /mnt/Destination")
        if is_encrypted == 'yes':
            run_command("umount /mnt/bitlocker")
            run_command("umount /mnt/decrypted")
        else:
            run_command("umount /mnt/Source")
    except Exception as e:
        print(f"Error unmounting drives: {e}")
        return

    print("Process completed successfully. You can now safely remove the external drive and the USB drive.")

if __name__ == "__main__":
    main()
