// FOR debugging - not needed

app.get("/health_check", (req, res) => {
    console.log(ADMIN_URL);
    console.log(REPO_AGENT);
    res.send(hello);
  });
  
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
  
  app.get("/register", (request, response) => {
    let data = {
      alias: "Repo.Agent",
      seed: "my_seed_00000000000000000000" + getRandomInt(9999),
      role: "TRUST_ANCHOR",
    };
    axios
      .post(`${LEDGER_URL}/register`, data)
      .then((res) => {
        console.log(res);
        REPO_DID = res.data.did;
        response.json(res.data);
      })
      .catch((error) => {
        console.error(error.response);
        response.status(500).send(error).end();
      });
  });
  
  // create invitation using repo agent directly
  // output config.json
  app.get("/create_invitation", (req, response) => {
    var data = " ";
    var config = {
      method: "post",
      url: `${ADMIN_URL}/connections/create-invitation?multi_use=true`,
      headers: {},
      data: data,
    };
    axios(config)
      .then(function (res) {
        console.log("respose received");
        console.log(res);
        var invitation = res.data.invitation;
        var config = { repo: REPO_DID, invitation };
        console.log(config);
        response.json(config);
      })
      .catch((error) => {
        console.error(error.response);
        response.status(500).send(error).end();
      });
  });