import agent from './agent.js'
import express from 'express'
import axios from 'axios'

const app = express()
const port = process.env.PORT || 3000
const LEDGER_URL = `http://${process.env.DOCKERHOST}:9000`

app.get('/register', (request, response) => {
  let data = {"alias": 'Repo.Agent', "seed": "my_seed_00000000000000000000" + getRandomInt(9999), "role": "TRUST_ANCHOR"};
  axios
  .post(`${LEDGER_URL}/register`, data)
  .then(res => {
    console.log(res);
    response.json(res.data);
  })
  .catch(error => {
    console.error(error.response);
    response.status(500).send(error).end();
  })
});

app.get('/health_check', (req, res) => {
  res.send("up");
});

await agent.start_agent();
app.listen(port, () => {
  console.log(`Example app listening on port ${port}!`)
  console.log('ledger default url: ' + LEDGER_URL);
});


function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}