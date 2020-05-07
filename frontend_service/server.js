const express = require('express');


const app = express();
app.get('/', (req, res) => {
  res.send('Hello World');
});


app.listen(process.env.PORT, process.env.HOST);