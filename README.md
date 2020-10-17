# URL shortener
A simple python-implemented URL shortener and some system level thinkings
## Table of Contents
- [URL shortener](#url-shortener)
  - [Table of Contents](#table-of-contents)
  - [Installation and Run](#installation-and-run)
  - [System APIs](#system-apis)
    - [/shortenURL](#shortenurl)
    - [/getURL](#geturl)
    - [/\<token>](#token)
  - [System Assumptions](#system-assumptions)
  - [Capacity Estimation and Constraints](#capacity-estimation-and-constraints)
  - [DB schema design](#db-schema-design)
  - [Token generation strategy](#token-generation-strategy)
  - [Fundamental system schematic diagram](#fundamental-system-schematic-diagram)
  - [Concerns need to be eased](#concerns-need-to-be-eased)
    - [1. 直接用 Python program 接流量？](#1-直接用-python-program-接流量)
    - [2. Online token generation 可能會是效率瓶頸，如何解決？](#2-online-token-generation-可能會是效率瓶頸如何解決)
    - [3. DB 選用基準？](#3-db-選用基準)
    - [4. DB 的 partition 與 replication？](#4-db-的-partition-與-replication)
    - [5. 哪裡會需要 Cache layer？](#5-哪裡會需要-cache-layer)
    - [6. 那裡會需要 Load balancer？](#6-那裡會需要-load-balancer)
    - [7. 過期資料清除策略？](#7-過期資料清除策略)
  - [References](#references)

## Installation and Run

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

## System APIs
### /shortenURL
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

Error responses
- (400) given nothing or field of 'url' is not a JSON string
- (500) internal error

### /getURL
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

Error responses
- (400) given nothing or field of 'token' is not a JSON string
- (404) not found the token, maybe it is invalid or already expired
- (500) internal error

### /\<token>
- an endpoint for demostrating the redirection behavior
```shell
curl --request GET \
  --url http://127.0.0.1:12345/54e3QA
```

Successful response (302)
```shell
HTTP/1.0 302 FOUND
location: http://example.com/
Content-Type: text/html; charset=utf-8
Content-Length: 0
Server: Werkzeug/1.0.1 Python/3.8.2
Date: Sat, 17 Oct 2020 09:02:06 GMT
```

Error responses
- (404) not found the token, maybe it is invalid or already expired

## System Assumptions
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

## Token generation strategy
- 先使用即時的 **online generation** 方式，client 有創建請求時則即時運算產生 token
- 短網址需要的 token 長度，假設使用 **base 62** 的方式來產生
  > base 62: 只的是使用 digits(10) + lower letters(26) + upper letters(26) 共 62 個 characters
- 那麼 token 長度只需要 **6 位**即可
  > log(15768000000) / log(62) ~= 5.69 < min. token length = 6
- 接著我們利用 hash function ，將原始網址作為 input 產生 n-bit hash value。在此簡單使用 MD5 來產生 128-bit 的 hash value
- 再利用此 128-bit 的 value 轉換成 base 62 的 encoded string，會有 21 個 letters，我們簡單取用前 6 位的 letters 作為 token 即可。若需要考慮衝突的情境則可再利用其他位置的 letters
  > 128 * log(2) / log(62) ~= 21

## Fundamental system schematic diagram
- 目前實作品的處理流程，簡單來看僅有四個元件：
    1. Client 端
    2. App 主程式
    3. token generator 負責產生短網址 token
    4. Database，負責資料儲存

![](https://i.imgur.com/DYhboam.png)
- 以上圖為基礎，底下提出幾點圖上架構尚須進一步考慮的隱憂 (紅圈數字)

## Concerns need to be eased
### 1. 直接用 Python program 接流量？
- **當然不能這麼做**，首先 python program 至少得先用 WSGI 帶起來，此舉還能做出 master / workers 的架構，來充分利用機器的 CPU、消弭一點 GIL 可能帶來的隱憂
    - e.g. [gunicorn](https://gunicorn.org/)
- 實際上，面對 public 的節點需使用成熟的 web server 來處理 concurrent requests (e.g. Apache or Nginx)
- Nginx 應會較適合此題的場景
    - 因 C10K 問題會在同時間有超多 connections，multi-thread process 的 apache 會因建立太多 connections 及 threads 造成硬體資源消耗過多
    - Nginx 使用 event-driven 的底層架構，讓 user space 只靠 single thread 就能處理大量的 requests，以此來因應 C10K 問題
- 而目前的實作品假設前面還有 web server 與 web 前端服務來處理真正的轉址行為

🆕 ***改善後的 client <---> app 示意圖***
![](https://i.imgur.com/57Cdf8D.png)

### 2. Online token generation 可能會是效率瓶頸，如何解決？
- 再獨立一支 token generation service (TGS)，負責事先產生好 6 letters tokens，並儲存下來，app 需要時向它存取即可
- 好處是 app 端不需要對 URL encode，也不用擔心 token collision 的問題了

**app 為多台的 concurrency 情境，可能同個 token 被重複取得嗎？**
- 所以 TGS 的 token pool 必須有 lock 的機制避免 multiple requests access token pool at the same time

**token pool 有 lock 的話，那吞吐量如何被保證？**
- TGS 可總是將 available tokens 保存在 memory 來加速 (i.e. token pool)
- TGS 還會需要自己一個資料庫，有兩張 tables 分別儲存 avaliable tokens 與 used tokens
    - 額外的儲存需求約 **88 GiB**
        > 15768000000 * 6 / 1024 / 1024 / 1024 ~= 88 GiB
- 發現 token pool 沒有時再從 avaliable tokens table 批次讀取儲存到 token pool
- 當 token 被 app 取走時則將 token 儲存到 used tokens table
- app 也可選擇批次取得 tokens 放到 app 的 memory 裡，減少 connection 的次數及可能被 lock 的機會來提速

**single point of failure?**
- TGS 的 QPS 可透過 app 的批次存取來減少，故可簡單給個 standby server 等 main server 掛點時切換

🆕 ***改善後的 APP <---> TGS 示意圖***
![](https://i.imgur.com/TslMCHx.png)


### 3. DB 選用基準？
- 考慮到 billions 數量級的儲存
- entry 之間毫無 **relation**
- read-heavy application
- 故應傾向**選擇 NoSQL database**

Refs:
- [When to choose NoSQL over SQL?](https://dev.to/ombharatiya/when-to-choose-nosql-over-sql-536p)
- [MongoDB vs MySQL: A Comparative Study on Databases](https://www.simform.com/mongodb-vs-mysql-databases/)
- [why are noSQL databases more scalable than SQL?](https://softwareengineering.stackexchange.com/questions/194340/why-are-nosql-databases-more-scalable-than-sql)

### 4. DB 的 partition 與 replication？
- 單台機器儲存 7.6 TiB 的資料可能有點誇張
- 可使用 DB 應已內建的 partition 機制來做分散式儲存
    - key hash 來讓資料足夠分散在不同 partition + [consistent hashing](https://medium.com/@sandeep4.verma/consistent-hashing-8eea3fb4a598) 來避免加減機器時造成大量的資料搬遷
- 接著，可考慮再利用 replication 的支援將讀寫分離

### 5. 哪裡會需要 Cache layer？
- 縮址還原的請求，10000 QPS 的路徑上每次都去查詢 DB 會是顯而易見的瓶頸
- 可選擇 Redis 或 Memcache 介於 APP 與 DB 之間
- Evict strategy 使用 LRU，只 caching 最近被存取的策略符合我們的應用假設
- :warning: 使用 Redis 時要注意，因為 Redis 是 single threaded 的架構，故 data 最好要設定 [expiration time](https://stackoverflow.com/a/36173972/8694937)，避免 Redis 在尖峰時刻處理 app 請求、卻又同時要處理大量的 eviction，造成 CPU 繁忙降低吞吐量
- 若單台真的撐不住，則可以再進一步做 replication 分散流量，但與 app 之間就需要 LB 來導流
- 當 cache miss 時，app 才向 DB 存取資料，然後將資料存到 cache
    - 此時可選擇是由 app 來負責直接 update cache 或尋找 DB 的功能來直接對 cache server 做 update

🆕 **改善後的 APP <---> DB 示意圖**
![](https://i.imgur.com/W3Cf2T4.png)

### 6. 那裡會需要 Load balancer？

- 基本上，節點需要被 scaling 來處理流量的前面都可以放 LB：
    1. client -> app
        -> client -> LB -> app(s)
    2. app -> cache
        -> app -> LB -> cache(s)
    3. app -> DB
        -> app -> LB -> DB(s)
- 當 cache 與 DB 皆有多台時，端看 DB 產品提供何種 replication 的機制，若為 master / slaves 的架構，則將讀取流量都分散到 read-only 的 slaves 上
- 寫入的需求 (創建短網址與 update cache) 則由 master 負責做

### 7. 過期資料清除策略？
- 由背景程式在離峰時段施作

## References
- learn a lot from:
  - [Designing a URL Shortening service like TinyURL](https://www.educative.io/courses/grokking-the-system-design-interview/m2ygV4E81AR)
  - [系統設計 - 設計縮網址服務](https://www.jyt0532.com/2019/12/05/design-tiny-url/)