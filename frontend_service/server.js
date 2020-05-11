const express = require('express');
const app = express();


app.get('/', (req, res) => {
    res.sendFile(__dirname + "/content/index.html");
})


app.listen(process.env.PORT, process.env.HOST)