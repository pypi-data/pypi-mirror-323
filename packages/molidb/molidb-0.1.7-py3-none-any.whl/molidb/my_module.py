import json, requests, gzip, base64
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def gzip_compress(data: bytes) -> bytes:
    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as f:
        f.write(data)
    return buf.getvalue()

def gzip_decompress(data: bytes) -> bytes:
    buf = BytesIO(data)
    with gzip.GzipFile(fileobj=buf, mode='rb') as f:
        return f.read()

class molidb:
    def __init__(self,SERVER_URL = "http://127.0.0.1:17233", SECRET_KEY = "ThisIs32byteAESkeyForThisExample", API_TOKEN  = 'ThisIsExampleAPIKey'):
        self.SERVER_URL = SERVER_URL
        self.SECRET_KEY = SECRET_KEY
        self.API_TOKEN = API_TOKEN
    def get_headers(self):
        return {
        'Authorization': f"{self.API_TOKEN}",
        'Content-Type': 'application/json'
    }
    def aes_encrypt(self,data: bytes) -> bytes:
        cipher = AES.new(self.SECRET_KEY.encode(), AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        return cipher.iv + ct_bytes

    def aes_decrypt(self,data: bytes) -> bytes:
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(self.SECRET_KEY.encode(), AES.MODE_CBC, iv=iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        return decrypted
    def list_collection(self):
        response = requests.get(f"{self.SERVER_URL}/collection", headers=self.get_headers())
        if response.status_code == 200:
            encrypted_data_base64 = response.json().get("data")
            encrypted_data = base64.b64decode(encrypted_data_base64)
            aes_decrypt_data = self.aes_decrypt(encrypted_data)
            decompressed_data = gzip_decompress(aes_decrypt_data)
            data = json.loads(decompressed_data)
            return data
        else:
            raise f"HTTP FAIL : {response.json()}"

    def get_collection(self,id):
        response = requests.get(f"{self.SERVER_URL}/collection/{id}", headers=self.get_headers())
        if response.status_code == 200:
            encrypted_data_base64 = response.json().get("data")
            encrypted_data = base64.b64decode(encrypted_data_base64)
            decrypted_data = self.aes_decrypt(encrypted_data)
            decompressed_data = gzip_decompress(decrypted_data)
            data = json.loads(decompressed_data)
            return data
        else:
            raise f"HTTP FAIL : {response.json()}"

    def update_collection(self,id, data):
        json_data = json.dumps(data).encode()
        compressed_data = gzip_compress(json_data)
        encrypted_data = self.aes_encrypt(compressed_data)
        encrypted_data_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        headers = self.get_headers()
        headers['body'] = encrypted_data_base64
        response = requests.put(f"{self.SERVER_URL}/collection/{id}", headers=headers)
        if response.status_code == 200:
            encrypted_data_base64 = response.json().get("data")
            encrypted_data = base64.b64decode(encrypted_data_base64)
            aes_decrypt_data = self.aes_decrypt(encrypted_data)
            decompressed_data = gzip_decompress(aes_decrypt_data)
            data = json.loads(decompressed_data)
            return data
        else:
            raise f"HTTP FAIL : {response.json()}"

    def delete_collection(self,id):
        response = requests.delete(f"{self.SERVER_URL}/collection/{id}", headers=self.get_headers())
        if response.status_code != 200:
            raise f"HTTP FAIL : {response.json()}"
        
if __name__ == '__main__':
    db = molidb()
    print(db.list_collection())
    print(db.update_collection('user', [{'id':'molidb','money':10}]))
    userlist = db.get_collection('user')
    print(userlist)
    for user in userlist:
        if user['id'] == 'molidb':
            user['money'] += 20
    print(db.get_collection('user'))
    print(db.update_collection('user', userlist))
    print(db.list_collection())