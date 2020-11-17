const hello = "hello vsw world from webhook handler";
const express = require("express");
const app = express();
const bodyParser = require("body-parser");
const axios = require("axios");
const json = require("json");
const REPO_AGENT = process.env.REPO_AGENT || "http://localhost:8060";
const ADMIN_URL = process.env.ADMIN_URL || "http://localhost:8061";
const LEDGER_URL = "http://localhost:9000";

const port = 8062;

var REPO_DID = "";

//demo controller

// Tell express to use body-parser's JSON parsing
app.use(bodyParser.json());
app.get("/webhooks", (req, res) => {
  res.send("webhooks");
});

// webhooks (both /topic/:topicid and /webhooks/topic/:topic  paths included for debug purposes)
app.post("/topic/:topicid", async (req, res) => {
  var topicId = req.params.topicid;
  console.log(`topic handler ${topicId}`);

  // handle register use case
  if (topicId == "handle_connections") {
    console.log(topicId);
    handle_connections(req.payload);
    res.send(topicId);
    return;
  }

  // 
  // this should handle publish
  //
  if (topicId == "handle_issue_credential") {
    console.log(topicId);
    await handle_issue_credential(req.payload, res);
    return;
  }
  res.send("no topic handler - OK");
});

// webhooks
app.post("/webhooks/topic/:topicid", async (req, res) => {
  var topicId = req.params.topicid;
  console.log(`topic handler ${topicId}`);

  // handle register use case
  if (topicId == "handle_connections") {
    console.log(topicId);
    handle_connections(req.payload, res);
    return;
  }

  // this should handle publish
  //
  if (topicId == "handle_issue_credential") {
    console.log(topicId);
    res.send(topicId);
    return;
  }
  res.send("no topic handler - OK");
});

// handle connections
async function handle_connections(message, response) {
  if (message.connection_id == connection_id) {
    if (message.state == "active" || message.state == "response") {
      console.log("connected");
      response.send("topic");
    }
  }
}
// handle issue credentials
async function handle_issue_credential(message, response) {
  state = message.state;
  console.log("handle issue credential");
  credential_exchange_id = message.credential_exchange_id;

  if (state == "offer_received") {
    console.log("After receiving credential offer, send credential request");
    axios
      .post(
        `${ADMIN_URL}/issue-credential/records/${credential_exchange_id}/send-request`
      )
      .then((res) => {
        console.log(res);
        axios
          .get(`${ADMIN_URL}/issue-credential/records/${cred_id}/send-request`)
          .then((res) => {
            console.log(res);
            response.json(res.data);
          })
          .catch((error) => {
            console.error(error.response);
            response.status(500).send(error).end();
          });
      })
      .catch((error) => {
        console.error(error.response);
        response.status(500).send(error).end();
      });
  } else if (state == "credential_acked") {
    cred_id = message.credential_id;
    console.log("Stored credential " + cred_id + " in wallet");

    axios
      .get(`${ADMIN_URL}/credential/{cred_id}`)
      .then((res) => {
        console.log(res);
        response.json(res.data);
      })
      .catch((error) => {
        console.error(error.response);
        response.status(500).send(error).end();
      });
  }
}

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});

function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}
