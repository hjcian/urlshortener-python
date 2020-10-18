import http from 'k6/http'
import { Counter } from 'k6/metrics'
// import { sleep } from 'k6'
const data = JSON.parse(open('./data.json'))
const tokens = data.tokens.slice(0, 1000)

const OKCounter = new Counter('Status - 200')
const NotFoundCounter = new Counter('Status - 404')
const ErrorCounter = new Counter('Status - error')

export const options = {
  vus: 100, // how many concurrent user
  iterations: 100 // how many steps a user doing
//   duration: '30s'
}

const choose = (choices) => {
  const index = Math.floor(Math.random() * choices.length)
  return choices[index]
}

export default function () {
  const token = choose(tokens)
  const payload = JSON.stringify({
    token
  })
  const params = {
    headers: {
      'Content-Type': 'application/json'
    }
  }

  const resp = http.post('http://127.0.0.1:12345/getURL', payload, params)

  if (resp.status === 200) {
    OKCounter.add(1)
  } else if (resp.status === 404) {
    NotFoundCounter.add(1)
  } else {
    ErrorCounter.add(1)
  }
}
