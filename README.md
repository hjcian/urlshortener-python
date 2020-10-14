# URL shortener
一個以 Python 實作的 URL 縮址後端系統

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