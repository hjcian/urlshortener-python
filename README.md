# URL shortener
A simple python-implemented URL shortener and some system level thinkings

## Usage
### Installation and Run

> System Prerequisites:
> - git
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

### System APIs
#### /shortenURL
- shorten the given URL, return a token to frontend fir further use

```shell
curl --request POST \
  --url http://127.0.0.1:12345/shortenURL \
  --header 'content-type: application/json' \
  --data '{"url": "http://example.com/"}'
```

Successful response (200)
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 19
Server: Werkzeug/1.0.1 Python/3.8.2
Date: Sat, 17 Oct 2020 05:25:17 GMT

{
  "token": "54e3QA"
}
```

Error responses (400)
- given nothing or field of 'url' is not a JSON string


#### /getURL
- give the token, backend will return the original URL to frontend for further use (e.g. redirect)
- if token not exists, reply a 404 NOT FOUND

```shell
curl --request POST \
  --url http://127.0.0.1:12345/getURL \
  --header 'content-type: application/json' \
  --data '{"token": "54e3QA"}'
```

Successful response (200)
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 30
Server: Werkzeug/1.0.1 Python/3.8.2
Date: Sat, 17 Oct 2020 05:25:32 GMT

{
  "url": "http://example.com/"
}
```

Error responses (400)
- given nothing or field of 'token' is not a JSON string


## Assumptions
- 使用者**不需要登入**就能創建短網址。也就是一個功能單純的 public service
- 讀寫流量假設為 **100:10000** (QPS)，用來估計硬體需求
- 短網址僅儲存 **5 年** (因為硬碟雖然便宜但不是無限大，且不做 data purge 也會造成 DB 效率下降)

## Capacity Estimation and Constraints
**Traffic estimates**
- 寫入流量假設為 **100 QPS** (即每秒產生短網址的數量)
- 讀取流量假設為 **10000 QPS** (即未來每秒存取短網址的數量)
- 假設五年時間，創建的短網址存好存滿，則會有約 **15 billions 的短網址**。
  > 5(year) * 365(days/year) * 86400(sec./day) * 100(QPS) = 15768000000

**Bandwidth estimates**
- 估計 application 節點會承受多少實際流量
- 由於每筆 entry 約 506 bytes，故考慮
- **incoming** 的頻寬供創建短網址，保守估計約 **50 KiB/s**
  > 100 (QPS) * 506 / 1024(K) ~= 50 KiB/s
- **outcoming** 的頻寬供查詢原址，保守估計約 **5 MiB/s**
  > 10000 (QPS) * 506 / 1024(K) / 1024 (M) ~= 5 MiB/s

**Storage estimates**
- 估計需要多少 disk usage
- 沒有考量使用者，故 DB 目前僅需要一張 table 儲存 token | url
- token 考慮到 6 letters (6 bytes，見下述討論)，url 則再假設只允許 500 letters (500 bytes)，**故一筆 entry 需要 506 bytes**
- 故總共 15 billions 筆 entries 需要約 **7.6 TiB**
  > 506 * 15768000000 / 1024(K) / 1024(M) / 1024(G) / 1024(T) ~= 7.6 TiB

**Memory estimates**
- 估計當有 cache layer 時，需要多少記憶體
- 簡單使用 80/20 法則來估計，i.e. 一整天有 80% 的 cache 量會由 20% 的 unique 查詢所產生
- 故大約需要 81 GiB 的記憶體
  > 10000 (QPS) * 86400 * 506 / 1024(K) / 1024(M) / 1024(G) * 20% ~= 81 GiB

**Summary**
|||
| - | - |
|創建短網址|100 QPS|
|轉址查詢|10000 QPS|
|incoming data|50 KiB/s|
|outcoming data|5 MiB/s|
|儲存5年|7.6 TiB|
|緩存|81 GiB|

## DB schema design
- 最基本的需求僅需要一張 table 儲存 token 與 url，通常還會加上 createAt 與 deleteAt 方便操作
- 故 table schema 為：
  - token (PK, string)
  - url (string)
  - createAt (time, secondary index)
  - deleteAt (time, secondary index)
- createAt 與 deleteAt 加上 index 在後續若要做統計分析時可加速查找
- deleteAt 上 index 在未來做 data purge 時也能避免 full table scan

## token generation
### online generate
- 短網址需要的 token 長度，假設使用 **base 62** 的方式來產生
  > base 62: 只的是使用 digits(10) + lower letters(26) + upper letters(26) 共 62 個 characters
- 那麼 token 長度只需要 **6 位**即可
  > log(15768000000) / log(62) ~= 5.69 < min. token length = 6
- 接著我們利用 hash function ，將原始網址作為 input 產生 n-bit hash value。在此簡單使用 MD5 來產生 128-bit 的 hash value
- 再利用此 128-bit 的 value 轉換成 base 62 的 encoded string，會有 21 個 letters，我們簡單取用前 6 位的 letters 作為 token 即可。若需要考慮衝突的情境則可再利用其他位置的 letters
  > 128 * log(2) / log(62) ~= 21
