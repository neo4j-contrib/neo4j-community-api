from base64 import b64decode
from base64 import b64encode
import boto3

def decrypt_value(encrypted):
    decrypted_response = boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted))
    return decrypted_response['Plaintext']


def decrypt_value_str(encrypted):
    decrypted_response = boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted))
    return decrypted_response['Plaintext'].decode("utf-8")


def encrypt_value(value, kms_key):
    return b64encode(boto3.client('kms').encrypt(Plaintext=value, KeyId=kms_key)["CiphertextBlob"])
