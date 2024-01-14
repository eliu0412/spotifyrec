//import createClient from 'redis';
const createClient = require('redis');
const tf = require('@tensorflow/tfjs-node');
const app = require('express')();
const PORT = 8080;

//console.log(\))

app.listen(
    PORT,
    () => console.log(`its alive on http://localhost:${PORT}`)
)


app.get('/get-playlist/:song', async (req, res) => {

    const modelPath = "/Users/prithviseran/Documents/spotify_rec/tfjs-model/model.json";
    this.model = await tf.loadGraphModel(`file://${modelPath}`);

    //songname-length
    const { song } = req.params;

    songName = song.split("_")[0]
    playlistLength = song.split("_")[1]

    const client = createClient.createClient({
        password: 'U51bAsqkEnU47h7NevU1l0SlfSDiOsNx',
        socket: {
            host: 'redis-17912.c124.us-central1-1.gce.cloud.redislabs.com',
            port: 17912
        }
    });

    const setup = require("/Users/prithviseran/Documents/spotify_rec/everything_to_import/ml/index.js");

    await client.connect();

    const playlist_songs = [];

    //console.log(songName)

    for (let i = 0; i < playlistLength; i++) {
        // Your code to be executed in each iteration

        songId = await client.get(songName);

        //console.log(songId)

        const inputTensor = tf.tensor([[songId]], [1, 1], 'int32')
        //console.log(inputTensor)
        const results = this.model.execute(inputTensor)
        //console.log(results)
        const r0 = await results[0].data()
        // the first elemnt is not always the recommended index, so we check
        const recommendationsArray = r0.constructor === Int32Array ? r0 : await results[1].data()
        const recommendedId = recommendationsArray[0]
        console.log(recommendedId + 5)
        console.log('recommendedUserIdx', recommendedId)

        console.log(String(recommendedId))

        recommendedSong = await client.get(String(recommendedId));

        console.log(recommendedSong);

        playlist_songs.push(recommendedSong);

        songName = recommendedSong

        console.log(songName);
    }

    res.status(200).send({
        "playlist": playlist_songs
    })

    console.log(playlist_songs)
    
});