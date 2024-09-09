const express = require('express');
const axios = require('axios');
const multer = require('multer')
const fs = require('fs');
const FormData = require('form-data');
const path = require('path');

const app = express();
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get('/', (req, res) => {
    res.render('index');
});

const upload = multer({ dest: 'uploads/' });

app.post('/generate-instructions', upload.array('screenshots'), async (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).send('No files uploaded.');
    }

    try {
        const form = new FormData();
        
        // Loop through each uploaded file and add it to the FormData
        req.files.forEach(file => {
            form.append('screenshots', fs.createReadStream(file.path), file.originalname);
        });
        
        // Add the context field
        form.append('context', req.body.context);

        // Send the form data (images and context) to the Flask server
        const response = await axios.post('http://localhost:5000/generate-instructions', form, {
            headers: {
                ...form.getHeaders(),
            },
        });

        // Clean up the uploaded files after the request
        req.files.forEach(file => {
            if (fs.existsSync(file.path)) {
                fs.unlinkSync(file.path);
            }
        });

        // Return the Flask server's response to the client
        res.status(200).json({
            message: 'Images sent to Flask server!',
            flaskResponse: response.data,
        });

    } catch (error) {
        console.error('Error sending images:', error);

        // Clean up files in case of an error
        req.files.forEach(file => {
            if (fs.existsSync(file.path)) {
                fs.unlinkSync(file.path);
            }
        });

        res.status(500).send('Error communicating with Flask server');
    }
});

app.listen(3001, () => {
    console.log('Express server running on port http://localhost:3001');
});
