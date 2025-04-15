// server.js
import express from 'express';
import { exec } from 'child_process';
import cors from 'cors';
const app = express();

// Utilisez le middleware cors
app.use(cors());
const PORT = 5000;

app.use(express.json());

app.post('/run-script/:quartier', (req, res) => {
  exec('python3 src/script.py '+req.params.quartier, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error}`);
      return res.status(500).send(error);
    }
    if (stderr) {
      console.error(`Stderr: ${stderr}`);
      return res.status(500).send(stderr);
    }
    console.log(`Stdout: ${stdout}`);
    res.send(stdout);
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
