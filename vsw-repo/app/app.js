const express = require('express')
const {exec} = require('child_process');
const app = express()
const port = process.env.PORT || 3000
app.get('/', (req, res) => {
 
 const aca = exec('python3 $agent_home/bin/aca-py start', function (error, stdout, stderr) {
    if (error) {
      console.log(error.stack);
      console.log('Error code: '+error.code);
      console.log('Signal received: '+error.signal);
    }
    console.log('Child Process STDOUT: '+stdout);
    console.log('Child Process STDERR: '+stderr);
  });
  
  aca.on('exit', function (code) {
    console.log('Child process exited with exit code '+code);

    // send data to browser
    res.send("server start up")
  });
 
})
app.listen(port, () => console.log(`Example app listening on port ${port}!`))