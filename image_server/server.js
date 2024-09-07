const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const port = 3000; // You can use any port

// Define your CORS options
const corsOptions = {
    origin: [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    credentials: true,
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
};

app.use(cors(corsOptions));

const imagesPath = path.join(__dirname, '..', 'processor', 'downloaded_images');
app.use('/images', express.static(imagesPath));

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});