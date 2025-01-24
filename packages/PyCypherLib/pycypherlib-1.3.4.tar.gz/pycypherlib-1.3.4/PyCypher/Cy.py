import os
import sys
import base64
from getpass import getpass

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Please install 'cryptography'.")
    sys.exit(1)

class Cy:
    def __init__(self):
        self._xMode = None
        self._xfIn = None
        self._xfOut = None
        self._xPwd = None
        self._xNewPwd = None
        self._xDel = False
        self._xDataLines = None
        print('''
    $$$$$$$$$$$$$$$$$$$$
    $$ PY CIPHER v1.3 $$
    $$ >> by eaannist $$
    $$$$$$$$$$$$$$$$$$$$
        ''')
    def enc(self, input_file=None):
        self._xMode = "enc"
        if input_file:
            self._xfIn = input_file
        return self

    def dec(self, input_file=None):
        self._xMode = "dec"
        if input_file:
            self._xfIn = input_file
        return self

    def run(self, input_file=None):
        self._xMode = "run"
        if input_file:
            self._xfIn = input_file
        return self

    def encLines(self, output_file=None):
        self._xMode = "enc_lines"
        if output_file:
            self._xfOut = output_file
        return self

    def decLines(self, input_file=None):
        self._xMode = "dec_lines"
        if input_file:
            self._xfIn = input_file
        return self

    def changeP(self, input_file=None):
        self._xMode = "changeP"
        if input_file:
            self._xfIn = input_file
        return self

    def newName(self, output_file):
        self._xfOut = output_file
        return self

    def Lines(self, data):
        if not isinstance(data, (str, list)):
            raise ValueError("Lines must be a string or list of strings.")
        self._xDataLines = data
        return self

    def terminalL(self, msg="Enter line: "):
        line_input = input(msg).rstrip("\r")
        if self._xDataLines is None:
            self._xDataLines = []
        elif isinstance(self._xDataLines, str):
            self._xDataLines = [self._xDataLines]
        self._xDataLines.append(line_input)
        if self._xMode == "enc":
            self._xMode = "enc_lines"
        return self

    def newP(self, password):
        self._xNewPwd = password
        return self

    def delInput(self):
        self._xDel = True
        return self

    def P(self, password):
        self._xPwd = password
        return self._xExec()

    def terminalP(self, msg="Password: "):
        self._xPwd = getpass(msg)
        return self._xExec()

    def _xExec(self):
        if self._xMode == "enc":
            return self._xDoEncFile()
        elif self._xMode == "dec":
            return self._xDoDecFile()
        elif self._xMode == "run":
            return self._xDoRunFile()
        elif self._xMode == "enc_lines":
            return self._xDoEncLines()
        elif self._xMode == "dec_lines":
            return self._xDoDecLines()
        elif self._xMode == "changeP":
            return self._xDoChangePwd()
        else:
            raise ValueError("No valid mode selected.")

    def _xKdf(self, password, salt):
        pwd_bytes = bytearray(password.encode("utf-8"))
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key_material = kdf.derive(pwd_bytes)
        for i in range(len(pwd_bytes)):
            pwd_bytes[i] = 0
        del pwd_bytes
        key = base64.urlsafe_b64encode(key_material)
        temp_ba = bytearray(key_material)
        for i in range(len(temp_ba)):
            temp_ba[i] = 0
        del key_material
        del temp_ba
        return key

    def _xEncData(self, data, password):
        salt = os.urandom(16)
        key = self._xKdf(password, salt)
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(data)
        self._xZero(key)
        del key
        return salt + encrypted_data

    def _xDecData(self, enc_data, password):
        salt = enc_data[:16]
        encrypted = enc_data[16:]
        key = self._xKdf(password, salt)
        cipher_suite = Fernet(key)
        try:
            decrypted = cipher_suite.decrypt(encrypted)
        except Exception:
            print("Error: Wrong password or corrupt data.")
            decrypted = None
        self._xZero(key)
        del key
        return decrypted

    def _xZero(self, bdata):
        if isinstance(bdata, bytearray):
            for i in range(len(bdata)):
                bdata[i] = 0
        else:
            temp_ba = bytearray(bdata)
            for i in range(len(temp_ba)):
                temp_ba[i] = 0
            del temp_ba

    def _xWipe(self):
        if self._xPwd is not None:
            temp_ba = bytearray(self._xPwd.encode("utf-8"))
            for i in range(len(temp_ba)):
                temp_ba[i] = 0
            del temp_ba
            self._xPwd = None
        if self._xNewPwd is not None:
            temp_ba2 = bytearray(self._xNewPwd.encode("utf-8"))
            for i in range(len(temp_ba2)):
                temp_ba2[i] = 0
            del temp_ba2
            self._xNewPwd = None

    def _xFileDel(self, filename):
        if not os.path.isfile(filename):
            return
        try:
            size = os.path.getsize(filename)
            with open(filename, "r+b") as f:
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        except:
            pass
        try:
            os.remove(filename)
        except:
            pass

    def _xDoEncFile(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File '{self._xfIn}' not found.")

        with open(self._xfIn, "rb") as f:
            data = f.read()
        enc_data = self._xEncData(data, self._xPwd)
        self._xZero(data)
        del data
        out_file = self._xfOut or (self._xfIn + ".cy")
        with open(out_file, "wb") as f:
            f.write(enc_data)
        self._xZero(enc_data)
        del enc_data
        self._xWipe()

        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Encrypted and deleted '{self._xfIn}' -> '{out_file}'.")
        else:
            print(f"Encrypted '{self._xfIn}' -> '{out_file}'.")
        return self

    def _xDoDecFile(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File '{self._xfIn}' not found.")

        with open(self._xfIn, "rb") as f:
            enc = f.read()
        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            print("Decryption failed.")
            return self

        if self._xfOut:
            out_file = self._xfOut
        else:
            if self._xfIn.endswith(".cy"):
                out_file = self._xfIn[:-3]
            else:
                out_file = self._xfIn + ".dec"

        with open(out_file, "wb") as f:
            f.write(dec_data)
        self._xZero(dec_data)
        del dec_data
        self._xWipe()

        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Decrypted and deleted '{self._xfIn}' -> '{out_file}'.")
        else:
            print(f"Decrypted '{self._xfIn}' -> '{out_file}'.")
        return self

    def _xDoRunFile(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File '{self._xfIn}' not found.")

        with open(self._xfIn, "rb") as f:
            enc = f.read()
        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            print("Cannot run: decryption failed.")
            return self

        if self._xfIn.endswith(".py.cy"):
            print("Executing decrypted content...")
            try:
                code_str = dec_data.decode("utf-8")
                exec(code_str, globals())
                self._xZero(code_str.encode("utf-8"))
                del code_str
            except Exception as e:
                print(f"Error: {str(e)}")
        else:
            print("Error: Not a .py.cy file.")

        self._xZero(dec_data)
        del dec_data
        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Executed and deleted '{self._xfIn}'.")
        self._xWipe()
        return self

    def _xDoEncLines(self):
        if self._xDataLines is None:
            raise ValueError("No lines data.")
        if isinstance(self._xDataLines, list):
            data_str = "\n".join(self._xDataLines)
        else:
            data_str = str(self._xDataLines)

        data_bytes = data_str.encode("utf-8")
        enc_data = self._xEncData(data_bytes, self._xPwd)
        out_file = self._xfOut or "cyfile.cy"
        with open(out_file, "wb") as f:
            f.write(enc_data)

        self._xZero(data_bytes)
        del data_bytes
        self._xZero(data_str.encode("utf-8"))
        del data_str
        self._xZero(enc_data)
        del enc_data
        self._xWipe()
        print(f"Encrypted lines -> '{out_file}'.")
        return self

    def _xDoDecLines(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File '{self._xfIn}' not found.")

        with open(self._xfIn, "rb") as f:
            enc = f.read()
        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            print("Decryption failed.")
            return None

        text = dec_data.decode("utf-8")
        self._xZero(dec_data)
        del dec_data

        if "\n" in text:
            splitted = text.split("\n")
            if len(splitted) > 1:
                result = splitted
            else:
                result = text
        else:
            result = text

        if self._xDel:
            self._xFileDel(self._xfIn)
            print(f"Decrypted and deleted '{self._xfIn}'.")
        else:
            print(f"Decrypted '{self._xfIn}'.")
        self._xWipe()
        return result

    def _xDoChangePwd(self):
        if not self._xfIn:
            raise ValueError("No input file specified.")
        if not os.path.isfile(self._xfIn):
            raise FileNotFoundError(f"File '{self._xfIn}' not found.")

        if not self._xPwd:
            raise ValueError("Old password is missing.")
        if not self._xNewPwd:
            raise ValueError("New password is missing.")

        with open(self._xfIn, "rb") as f:
            enc = f.read()
        dec_data = self._xDecData(enc, self._xPwd)
        self._xZero(enc)
        del enc

        if dec_data is None:
            self._xWipe()
            print("Password change failed (wrong old password or corrupt data).")
            return self

        new_enc_data = self._xEncData(dec_data, self._xNewPwd)
        self._xZero(dec_data)
        del dec_data

        with open(self._xfIn, "wb") as f:
            f.write(new_enc_data)

        self._xZero(new_enc_data)
        del new_enc_data
        self._xWipe()
        print(f"Password changed for '{self._xfIn}'.")
        return self
