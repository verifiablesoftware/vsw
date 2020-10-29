import agent from './agent.js'
import express from 'express'

const app = express()
const port = process.env.PORT || 3000

app.get('/', (req, res) => {
  const aca = agent.start_agent();
  res.send('start agent')
})

app.get('/health_check', (req, res) => {
  res.send("up");
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))