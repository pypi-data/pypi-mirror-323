import io
import os
import tempfile

from cryptography.fernet import Fernet
from dotenv import dotenv_values

# Define the environment variable name for the master key
ENVVAULT_MASTER_KEY = "MASTER_KEY"


class CredentialsManager:
    def __init__(self, env_name="development", key_path="master.key"):
        """
        Initializes the CredentialsManager.

        :param env_name: Environment name (e.g., development, production).
        :param key_path: Master key file path.
        """
        self.env_name = env_name or os.getenv("ENV") or os.getenv("NODE_ENV")
        self.key_path = key_path
        self.env_enc_path = (
            ".env.enc" if env_name == "production" else f".env.{env_name}.enc"
        )
        self.key = None

    def create_master_key(self, key=None):
        """
        Creates a new master key if not provided and saves it.
        """
        new_key = key or Fernet.generate_key()
        self.save_master_key(new_key)

    def save_master_key(self, key):
        """
        Saves the master key to a file and environment variable.
        """
        with open(self.key_path, "wb") as f:
            f.write(key)
        os.environ[ENVVAULT_MASTER_KEY] = key.decode("utf-8")
        self.key = key

    def load_master_key(self):
        """
        Loads the master key from environment variable or file.

        :return: Master key (bytes).
        """
        key = os.getenv(ENVVAULT_MASTER_KEY)
        if key:
            self.key = key.encode("utf-8")
        elif os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                self.key = f.read()
                os.environ[ENVVAULT_MASTER_KEY] = self.key.decode("utf-8")

    def regenerate_master_key(self):
        """
        Regenerates the master key and updates the encrypted data by decrypting it with the old key and re-encrypting it with the new key.
        """
        # First, load the old master key to use for decryption
        self.load_master_key()
        old_key = self.key

        # Generate a new master key to use for encryption
        self.create_master_key()

        # Check if the encrypted file exists to proceed with re-encryption
        if not os.path.exists(self.env_enc_path):
            return

        # Read the encrypted data from the file
        with open(self.env_enc_path, "rb") as f:
            encrypted_data = f.read()

        # If there is encrypted data, decrypt it using the old key, then re-encrypt it using the new key
        if encrypted_data:
            decrypted_data = Fernet(old_key).decrypt(encrypted_data).decode("utf-8")
            encrypted_data = Fernet(self.key).encrypt(decrypted_data.encode("utf-8"))
            # Write the re-encrypted data back to the file
            with open(self.env_enc_path, "wb") as f:
                f.write(encrypted_data)

        return self.key

    def create_empty_env_enc(self):
        """
        Creates an empty .env.enc file.
        """
        with open(self.env_enc_path, "wb") as f:
            f.write(b"")

    def decrypt_to_temp(self):
        """
        Decrypts the .env.enc file to a temporary file.

        :return: Temporary file path.
        """
        if not os.path.exists(self.env_enc_path):
            raise FileNotFoundError(f"Encrypted file {self.env_enc_path} not found.")

        with open(self.env_enc_path, "rb") as f:
            encrypted_data = f.read()

        cipher_suite = Fernet(self.key)
        decrypted_data = (
            cipher_suite.decrypt(encrypted_data).decode("utf-8")
            if encrypted_data
            else ""
        )
        # Creates a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".env"
        ) as temp_file:
            temp_file.write(decrypted_data)

        return temp_file.name

    def decrypt_env(self):
        """
        Decrypts the .env.enc file and returns the environment variables dictionary.

        :return: Decrypted environment variables dictionary.
        """
        if not os.path.exists(self.env_enc_path):
            raise FileNotFoundError(f"Encrypted file {self.env_enc_path} not found.")

        with open(self.env_enc_path, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = (
            Fernet(self.key).decrypt(encrypted_data).decode("utf-8")
            if encrypted_data
            else ""
        )

        # Convert the decrypted string to a stream for dotenv_values
        decrypted_stream = io.StringIO(decrypted_data)
        # Parse the decrypted content using dotenv_values
        return dotenv_values(stream=decrypted_stream)

    def encrypt_from_temp(self, temp_file_path):
        """
        Re-encrypts from the temporary file to the .env.enc file.

        :param temp_file_path: Temporary file path.
        """
        with open(temp_file_path, "rb") as f:
            plain_data = f.read()

        cipher_suite = Fernet(self.key)
        encrypted_data = cipher_suite.encrypt(plain_data)

        with open(self.env_enc_path, "wb") as f:
            f.write(encrypted_data)

        print(f"Re-encrypted and saved to {self.env_enc_path}")

    def cleanup_temp_file(self, temp_file_path):
        """
        Cleans up the temporary file.

        :param temp_file_path: Temporary file path.
        """
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")

    def ensure_files_exist(self, is_editing=False):
        """
        Ensures the master key and .env.enc file exist. If is_editing is True, it does not create a new master key if it does not exist.
        """
        self.create_empty_env_enc() if not os.path.exists(self.env_enc_path) else None
        self.load_master_key()

        if self.key is None:
            if is_editing:
                raise ValueError(
                    "Error: master.key does not exist, you can use init command to create a new Key."
                )
            else:
                self.create_master_key()

    def load_to_environment(self):
        """
        Loads the decrypted environment variables into os.environ.
        """
        env_vars = self.decrypt_env()
        for key, value in env_vars.items():
            os.environ[key] = value
