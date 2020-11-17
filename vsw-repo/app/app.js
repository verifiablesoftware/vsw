import agent from './agent.js'
import express from 'express'
import axios from 'axios'

const app = express()
const port = process.env.PORT || 8000
const LEDGER_URL = `http://${process.env.DOCKERHOST}:9000` || 'http://localhost:9000'
const REPO_AGENT = process.env.REPO_AGENT || 'http://localhost:8060'
const ADMIN_URL = process.env.REPO_ADMIN || 'http://localhost:8061'

var REPO_DID = ''

// 
// gets the DID for the REPO
//
app.get('/register', (request, response) => {
  let data = {"alias": 'Repo.Agent', "seed": "my_seed_00000000000000000000" + getRandomInt(9999), "role": "TRUST_ANCHOR"};
  console.log(LEDGER_URL) 
  axios
  .post(`${LEDGER_URL}/register`, data)
  .then(res => {
    console.log(res)
    REPO_DID = res.data.did
    response.json(res.data)
  })
  .catch(error => {
    console.error(error.response)
    response.status(500).send(error).end()
  })
})

//
// returing URLs, checking 
//
app.get('/health_check', (req, res) => {
  console.log(ADMIN_URL)
  console.log(REPO_AGENT)
  console.log(LEDGER_URL)
  res.send(`REPO up and running with ADMIN URL:  ${ADMIN_URL} REPO_AGENT: ${REPO_AGENT} LEDGER_URL: ${LEDGER_URL}`)
})

//
// schema fix
//
app.post("/schema_definition", (request, response) => {
  console.log('schemas')
  var data = {
    schema_name: "vsw schema",
    schema_version: "0.2",
    attributes: ["name", "url", "digest", "timestamp"],
  };
  var config = {
    method: "post",
    url: `${REPO_AGENT}/schemas`,
    headers: {},
    data: data,
  };
  axios(config)
    .then(function (res) {
      console.log("respose received");
      console.log(res);
      var schema_id = res.data.schema_id;
      console.log(res.data);
      response.json(res.data);
    })
    .catch((error) => {
      console.error(error.response);
      response.status(500).send(error).end();
    });
});

// 
// create invitation using repo agent directly 
// output can be used as .config.json for client
//
app.get('/create_invitation', (req, response) => {
  var data = ' '
  var config = {
    method: 'post',
    url:`${ADMIN_URL}/connections/create-invitation?multi_use=true`,
    headers: {},
    data: data 
  }
  axios(config)
  .then(function(res) {
    console.log('respose received')
    console.log(res)
    var invitation = res.data.invitation
    var config = {"repo": REPO_DID, invitation}
    console.log(config)
    response.json(config)
  })
  .catch(error => {
    console.error(error.response);
    response.status(500).send(error).end()
  })
})


// start repo agent
await agent.start_agent();

// start the server
app.listen(port, () => {
  console.log(`VSW-REPO app listening on port ${port}!`)
  console.log('ledger default url: ' + LEDGER_URL);
});

function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}

