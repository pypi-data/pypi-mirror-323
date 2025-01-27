# MoliDB Python Client

MoliDB는 안전한 통신을 위해 AES 암호화와 gzip 압축을 사용하는 Python 클라이언트입니다. 이 클라이언트는 MoliDB 서버와 상호작용할 수 있도록 도와줍니다.

## 설치 방법

PyPI에서 `molidb` 패키지를 설치할 수 있습니다:

```sh
pip install molidb
```

## 사용 방법

### 1. 서버와의 연결 설정

먼저, 서버의 URL과 API 토큰을 설정합니다. `dotenv`를 사용하여 환경 변수를 로드하거나 직접 코드를 수정할 수 있습니다.

```py
import molidb

molidb.SERVER_URL = "http://127.0.0.1:17233"   # 기본값
molidb.SECRET_KEY = "ThisIs32byteAESkeyForThisExample" # 기본값
molidb.API_TOKEN  = 'ThisIsExampleAPIKey'              # 기본값
```

### 2. 데이터 목록 조회

서버에서 제공하는 컬렉션 목록을 조회할 수 있습니다:

```py
# 컬렉션 목록 조회
collections = molidb.list_collection()
print(collections)
```

### 3. 특정 컬렉션 조회

특정 컬렉션을 조회하려면 ID를 제공해야 합니다:

```py
# 특정 컬렉션 조회
collection_id = 1  # 조회할 컬렉션 ID
collection_data = molidb.get_collection(collection_id)
print(collection_data)
```

### 4. 컬렉션 업데이트

컬렉션의 데이터를 업데이트할 수 있습니다. 업데이트할 데이터는 Python 딕셔너리 형태로 전달해야 합니다:

```py
# 컬렉션 업데이트
collection_id = 1  # 업데이트할 컬렉션 ID
new_data = {
    "name": "Updated Collection",
    "description": "This is an updated description."
}
updated_collection = molidb.update_collection(collection_id, new_data)
print(updated_collection)
```

### 5. 컬렉션 삭제

컬렉션을 삭제하려면 ID를 제공해야 합니다:

```py
# 컬렉션 삭제
collection_id = 1  # 삭제할 컬렉션 ID
molidb.delete_collection(collection_id)
print(f"Collection {collection_id} deleted successfully.")
```

## 예외 처리

서버와의 통신에서 오류가 발생할 수 있습니다. 예외 처리를 통해 오류 메시지를 처리할 수 있습니다:

```py
try:
    collections = molidb.list_collection()
    print(collections)
except Exception as e:
    print(f"Error occurred: {e}")
```

## 라이센스

이 프로젝트는 [MIT License](https://opensource.org/licenses/MIT)를 따릅니다.
