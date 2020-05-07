const express = require('express');
const http = require('http')

const app = express();
app.use(express.urlencoded())


app.get('/', (req, res) => {
    res.sendFile(__dirname + "/content/index.html");
})


app.post('/send-file', (req, res) => {
    filename = req.body.filename
    url = req.body.url
    console.log(filename + " " + url)
    send_file(filename, url)
    res.end()
})

function send_file(filename, url){
    const options = {
        hostname: process.env.DATABASE_API_HOST,
        port: process.env.DATABASE_API_PORT,
        path: '/add',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'filename': filename,
            'url': url
        })
    }
    
    const req = http.request(options, res => {
        console.log(`statusCode: ${res.statusCode}`)
        res.on('data', d => {
            process.stdout.write(d)
        })
    })
    
    req.on('error', error => {
    console.error(error)
    })
    
    req.write(options['body'])
    req.end()
}


app.listen(process.env.PORT, process.env.HOST)