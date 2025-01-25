import sys

VERSION = "1.1.1"

def encrypt(plain_text, key, offset):
    if len(plain_text) > 300:
        return "Error: Input text is too long. Limit to 300 characters."
    
    encrypted_text = " ".join(str((ord(char) * key) - offset) for char in plain_text)
    return encrypted_text

def decrypt(encrypted_text, key, offset):
    decrypted_text = ""
    try:
        encrypted_numbers = encrypted_text.strip().split()
        for number in encrypted_numbers:
            ascii_value = (int(number) + offset) // key
            decrypted_text += chr(ascii_value)
    except Exception as e:
        return f"Error during decryption: {e}"
    return decrypted_text

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_help():
    print(f"{YELLOW}Usage: dualkey{RESET}")
    print("Run the command 'dualkey' to start the encryption/decryption tool.")
    print("Options:")
    print("  -h, --help      Show this help message and exit\n")
    print("Instructions:")
    print("  1. Choose whether to (E)ncrypt or (D)ecrypt.")
    print("  2. Enter a 4-digit encryption key (e.g., 1234).")
    print("  3. Enter a 4 to 6-digit offset value (e.g., 123456).")
    print("  4. Input text to encrypt (max 300 characters) or decrypt an encrypted string.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(0)

    print(f"{GREEN}\
    DDDDD   U   U   AAAAA   L       K   K   EEEEE   Y   Y\n\
    D    D  U   U  A     A  L       K  K    E        Y Y\n\
    D    D  U   U  AAAAAAA  L       000     EEEE      Y\n\
    D    D  U   U  A     A  L       K  K    E         Y\n\
    DDDDD   UUUUU  A     A  LLLLL   K   K   EEEEE     Y{RESET}\n")
    print(f"{YELLOW}Encryption/Decryption Tool v{VERSION}{RESET}\n")
    
    while True:
        try:
            key = int(input(f"{YELLOW}Enter encryption key (4-digit number): {RESET}"))
            if key < 1000 or key > 9999:
                print(f"{RED}Error: Encryption key must be a 4-digit number.{RESET}")
                continue
            offset = int(input(f"{YELLOW}Enter offset value (4 to 6 digit number): {RESET}"))
            if offset < 1000 or offset > 999999:
                print(f"{RED}Error: Offset must be between 4 to 6 digits.{RESET}")
                continue
            break
        except ValueError:
            print(f"{RED}Error: Please enter valid numbers.{RESET}")

    action = input(f"{YELLOW}Do you want to (E)ncrypt or (D)ecrypt? {RESET}").strip().upper()

    if action == 'E':
        plain_text = input(f"{YELLOW}Enter text to encrypt (max 300 characters): {RESET}")
        encrypted_text = encrypt(plain_text, key, offset)
        print(f"{GREEN}Encrypted Text: {RESET}{encrypted_text}")

    elif action == 'D':
        encrypted_text = input(f"{YELLOW}Enter the encrypted text to decrypt: {RESET}")
        decrypted_text = decrypt(encrypted_text, key, offset)
        print(f"{GREEN}Decrypted Text: {RESET}{decrypted_text}")

    else:
        print(f"{RED}Invalid option. Please enter 'E' for encrypt or 'D' for decrypt.{RESET}")

if __name__ == "__main__":
    main()
