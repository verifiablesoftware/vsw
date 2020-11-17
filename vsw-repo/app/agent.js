import {exec} from 'child_process';

const DEFAULT_INTERNAL_HOST = "127.0.0.1";
const DEFAULT_EXTERNAL_HOST = "localhost";
const HTTP_PORT = 8060;
const ADMIN_PORT = 8061;
const WEBHOOK_PORT = 8062;

function start_agent() {
    console.log('start agent');
    let agent = exec('python3 /home/indy/bin/aca-py start ' + get_agent_args(), function (error, stdout, stderr) {
        if (error) {
          console.log(error.stack);
          console.log('Error code: '+error.code);
          console.log('Signal received: '+error.signal);
        }
        console.log('Child Process STDOUT: '+stdout);
        console.log('Child Process STDERR: '+stderr);
    });
    console.log('start agent done');
    return agent;
}

function get_agent_args() {
    let wallet_name = 'Repo.Agent' + Math.random();
    let args = {
        '--endpoint': `http://${DEFAULT_EXTERNAL_HOST}:${HTTP_PORT}`,
        '--label': 'Repo.Agent',
        '--admin-insecure-mode': '',
        '--inbound-transport': 'http 0.0.0.0 8060',
        '--outbound-transport': 'http ',
        '--admin': '0.0.0.0 8061',
        '--webhook-url': `http://${DEFAULT_EXTERNAL_HOST}:${WEBHOOK_PORT}/webhooks`,
        '--wallet-type': 'indy', //use indy wallet for now
        '--wallet-name': wallet_name,
        '--wallet-key': wallet_name
    };
    console.log(`webhook-url: http://${DEFAULT_EXTERNAL_HOST}:${WEBHOOK_PORT}/webhooks`)
    let str_arg = '';
    for (let key in args) {
        str_arg += key + ' ' + args[key] + ' ';
    }
    return str_arg;
}

export default {
    start_agent: start_agent
}