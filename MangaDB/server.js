const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(bodyParser.json());

mongoose.connect('mongodb://majeedgoat:hz8xHSzwbBekxkvZ@cluster0-shard-00-00.bl8d5.mongodb.net:27017,cluster0-shard-00-01.bl8d5.mongodb.net:27017,cluster0-shard-00-02.bl8d5.mongodb.net:27017/?replicaSet=atlas-t4u8c5-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0 ', {
    useNewUrlParser: true,
    useUnifiedTopology: true
  })
  .then(() => {
    console.log('');
  })
  .catch(err => {
    console.error('MongoDB connection error:', err);
  });  

const db = mongoose.connection;
db.on('error', console.error.bind(console, 'MongoDB connection error:'));
db.once('open', () => {
  console.log('Connected to MongoDB');
});

const kuzhiSchema = new mongoose.Schema({
    latitude: {
        type: Number,
        required: true
    },
    longitude: {
        type: Number,
        required: true
    },
    severity: {
        type: String,
        required: true
    }
},{
    timestamps: true
});

const Kuzhi = mongoose.model('Kuzhi', kuzhiSchema);

//GET
app.get('/kuzhi', async (req, res) => {
  try {
    const kuzhii = await Kuzhi.find();
    res.json(kuzhii);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

//POST
app.post('/kuzhi', async (req, res) => {
  const kuzhi = new Kuzhi({
    latitude: req.body.latitude,
    longitude: req.body.longitude,
    severity: req.body.severity
  });

  try {
    const newKuzhi = await kuzhi.save();
    res.status(201).json(newKuzhi);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});