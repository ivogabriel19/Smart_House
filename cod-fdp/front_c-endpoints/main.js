document.addEventListener("DOMContentLoaded", function() {
    init();
});

function init() {
    updateSensorSummary();
    updateEnergyChart();
    updateAccessLog();
    updateGardenInfo();

    const roomSelect = document.getElementById('roomSelect');
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            for (const room in data.rooms) {
                const option = document.createElement('option');
                option.value = room;
                option.textContent = room.replace('_', ' ');
                roomSelect.appendChild(option);
            }
            roomSelect.addEventListener('change', updateLightingControls);
            updateLightingControls();
        });

    // Actualizar datos cada 60 segundos
    setInterval(() => {
        updateSensorSummary();
        updateEnergyChart();
        updateAccessLog();
        updateGardenInfo();
    }, 60000);
}

function updateSensorSummary() {
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            const summary = document.getElementById('sensorSummary');
            summary.innerHTML = '';
            for (const [room, sensors] of Object.entries(data.rooms)) {
                const div = document.createElement('div');
                div.innerHTML = `
                    <h3>${room.replace('_', ' ')}</h3>
                    <p>Temperatura: ${sensors.temperature}°C</p>
                    <p>Humedad: ${sensors.humidity}%</p>
                `;
                summary.appendChild(div);
            }
        });
}

function updateEnergyChart() {
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            const chart = document.getElementById('energyChart');
            chart.innerHTML = '';
            const maxEnergy = Math.max(...data.energyData.map(d => d.energy));
            const chartHeight = 250;
            const barWidth = chart.clientWidth / data.energyData.length - 10;

            data.energyData.forEach((d, i) => {
                const bar = document.createElement('div');
                bar.style.position = 'absolute';
                bar.style.left = `${i * (barWidth + 10)}px`;
                bar.style.bottom = '0';
                bar.style.width = `${barWidth}px`;
                bar.style.height = `${(d.energy / maxEnergy) * chartHeight}px`;
                bar.style.backgroundColor = '#4CAF50';

                const label = document.createElement('div');
                label.textContent = d.name;
                label.style.position = 'absolute';
                label.style.bottom = '-20px';
                label.style.width = '100%';
                label.style.textAlign = 'center';

                bar.appendChild(label);
                chart.appendChild(bar);
            });
        });
}

function updateAccessLog() {
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            const log = document.getElementById('accessLog');
            log.innerHTML = '';
            data.accessLog.forEach(entry => {
                const li = document.createElement('li');
                li.textContent = `${entry.time} - ${entry.event} (${entry.rfid})`;
                log.appendChild(li);
            });
        });
}

function updateLightingControls() {
    const controls = document.getElementById('lightingControls');
    const roomSelect = document.getElementById('roomSelect');
    const selectedRoom = roomSelect.value;

    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            const roomData = data.rooms[selectedRoom];

            controls.innerHTML = `
                <label class="switch">
                    <input type="checkbox" ${roomData.lightOn ? 'checked' : ''} onchange="toggleLight('${selectedRoom}')">
                    <span class="slider round"></span>
                </label>
                <input type="color" value="${roomData.lightColor}" onchange="changeLightColor('${selectedRoom}', this.value)">
                <input type="range" min="0" max="100" value="${roomData.brightness}" onchange="changeBrightness('${selectedRoom}', this.value)">
            `;
        });
}

function toggleLight(room) {
    // Aquí puedes implementar la lógica para cambiar el estado de la luz
    console.log(`Light toggled in ${room}`);
}

function changeLightColor(room, color) {
    // Aquí puedes implementar la lógica para cambiar el color de la luz
    console.log(`Light color changed in ${room} to ${color}`);
}

function changeBrightness(room, brightness) {
    // Aquí puedes implementar la lógica para cambiar el brillo de la luz
    console.log(`Light brightness in ${room} set to ${brightness}`);
}

function updateGardenInfo() {
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            const gardenInfo = document.getElementById('gardenInfo');
            gardenInfo.innerHTML = `
                <p>Luz Solar: ${data.garden.sunlight}%</p>
                <p>Humedad del Suelo: ${data.garden.soilMoisture}%</p>
            `;
        });
}

function startWatering() {
    fetch('/api/start_watering', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert('Riego iniciado');
        });
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(sectionId).style.display = 'block';
}
