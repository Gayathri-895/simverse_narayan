const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// --- Simulation State ---
let simState = {
    env: {
        co2: 400, // ppm
        temp: 22, // Celsius
        light: 50, // Intensity %
    },
    plant: {
        health: 100,
        growthStage: 0, // 0 to 100
        oxygenProduction: 0,
        carbonAbsorption: 0,
    },
    history: []
};

// --- Photosynthesis Logic Engine ---
function updateSimulation() {
    const { co2, temp, light } = simState.env;

    // Simplified Photosynthesis Formula: Rate = f(CO2, Temp, Light)
    // Optimal: CO2 ~ 800-1000, Temp ~ 25, Light ~ 80
    const lightFactor = Math.sin((light / 100) * Math.PI / 2); // Efficiency curve
    const co2Factor = Math.min(co2 / 800, 1.5);
    const tempFactor = 1 - Math.abs(temp - 25) / 30; // Peak at 25C

    const growthRate = Math.max(0, lightFactor * co2Factor * tempFactor);
    
    // Update plant stats
    simState.plant.growthStage = Math.min(100, simState.plant.growthStage + (growthRate * 0.1));
    simState.plant.oxygenProduction = growthRate * 5;
    simState.plant.carbonAbsorption = growthRate * 4;

    // Health degrades if conditions are extreme
    if (temp > 40 || temp < 5 || co2 < 100) {
        simState.plant.health = Math.max(0, simState.plant.health - 0.5);
    } else {
        simState.plant.health = Math.min(100, simState.plant.health + 0.1);
    }

    // Emit live data
    io.emit('simUpdate', simState);
}

// Run simulation loop every 1 second
setInterval(updateSimulation, 1000);

// --- API Endpoints ---
app.get('/api/state', (req, res) => {
    res.json(simState);
});

app.post('/api/update-env', (req, res) => {
    const { co2, temp, light } = req.body;
    if (co2 !== undefined) simState.env.co2 = co2;
    if (temp !== undefined) simState.env.temp = temp;
    if (light !== undefined) simState.env.light = light;
    
    res.json({ success: true, newState: simState.env });
});

app.post('/api/reset', (req, res) => {
    simState.plant.growthStage = 0;
    simState.plant.health = 100;
    res.json({ success: true });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
    console.log(`GreenSim Logic Engine running on port ${PORT}`);
});
