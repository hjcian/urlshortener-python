# URL shortener
一個以 Python 實作的 URL 縮址後端系統

## Usage
### Run server

> Prerequisites:
> - Python 3.x
> - virtualenv
> 

```shell
git clone https://github.com/hjcian/urlshortener-python.git
cd urlshortener-python
virtualenv -p python3 env
source ./env/bin/activate
pip install -r requirements.txt
python main.py
```

### shortenURL
```shell
curl --request POST \
  --url http://127.0.0.1:12345/shortenURL \
  --header 'content-type: application/json' \
  --data '{"url": "http://example.com/","apikey": "hello world"}'
```

### getURL
```shell
curl --request POST \
  --url http://127.0.0.1:12345/getURL \
  --header 'content-type: application/json' \
  --data '{"token": "DgRetB5"}'
```

## Assumptions
- 以 APIKey 區分使用者
- 寫流量(100 QPS❓) 
  - URL ▶️ Token 的流量
- 讀流量(10000 QPS❓)
  - 使用者點擊的流量

## Considerations
### URL ▶️ Token 的換號策略
- 考慮過的實作
  - 以 URL 及 API Key 當作 hash function input，來產生 big number，並用前 40 bits 的值來產生 base 62 encoding，用此結果當成縮址的 Token