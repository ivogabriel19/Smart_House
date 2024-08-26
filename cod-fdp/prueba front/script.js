        // Datos simulados
        const data = {
            rooms: {
                living_room: { temperature: 22.5, humidity: 45, lightOn: true, lightColor: "#ffffff", brightness: 80 },
                bedroom: { temperature: 20.0, humidity: 50, lightOn: false, lightColor: "#ffff00", brightness: 60 },
                kitchen: { temperature: 23.5, humidity: 55, lightOn: true, lightColor: "#00ff00", brightness: 100 }
            },
            garden: { sunlight: 75, soilMoisture: 60 },
            accessLog: [
                { time: "08:00", event: "Puerta Desbloqueada", rfid: "RFID-001" },
                { time: "12:30", event: "Ventana Abierta", rfid: "RFID-002" },
                { time: "18:45", event: "Puerta Bloqueada", rfid: "RFID-001" }
            ],
            energyData: [
                { name: "Lun", energy: 4 },
                { name: "Mar", energy: 3 },
                { name: "Mié", energy: 5 },
                { name: "Jue", energy: 2 },
                { name: "Vie", energy: 4 },
                { name: "Sáb", energy: 6 },
                { name: "Dom", energy: 3 }
            ],
            customColors: {
                living_room: [{ name: "Relax", color: "#a1d2ce" }, { name: "Fiesta", color: "#ff69b4" }],
                bedroom: [{ name: "Noche", color: "#191970" }],
                kitchen: [{ name: "Cocina", color: "#ffa500" }]
            }
        };

        // Funciones de utilidad
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById(sectionId).style.display = 'block';
        }

        function updateSensorSummary() {
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
        }

        function updateEnergyChart() {
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
        }

        function updateAccessLog() {
            const log = document.getElementById('accessLog');
            log.innerHTML = '';
            data.accessLog.forEach(entry => {
                const li = document.createElement('li');
                li.textContent = `${entry.time} - ${entry.event} (${entry.rfid})`;
                log.appendChild(li);
            });
        }

        function updateLightingControls() {
            const controls = document.getElementById('lightingControls');
            const roomSelect = document.getElementById('roomSelect');
            const selectedRoom = roomSelect.value;
            const roomData = data.rooms[selectedRoom];

            controls.innerHTML = `
                <label class="switch">
                    <input type="checkbox" ${roomData.lightOn ? 'checked' : ''} onchange="toggleLight('${selectedRoom}')">
                    <span class="slider"></span>
                </label>
                <input type="color" value="${roomData.lightColor}" onchange="changeColor('${selectedRoom}', this.value)">
                <input type="range" min="0" max="100" value="${roomData.brightness}" onchange="changeBrightness('${selectedRoom}', this.value)">
                <div id="customColors"></div>
                <input type="text" id="newColorName" placeholder="Nombre del color">
                <button onclick="saveCustomColor('${selectedRoom}')">Guardar Color</button>
            `;

            updateCustomColors(selectedRoom);
        }

        function updateCustomColors(room) {
            const customColorsDiv = document.getElementById('customColors');
            customColorsDiv.innerHTML = '';
            data.customColors[room].forEach(color => {
                const colorDiv = document.createElement('div');
                colorDiv.className = 'custom-color';
                colorDiv.innerHTML = `
                    <button class="color-button" style="background-color: ${color.color}" onclick="applyCustomColor('${room}', '${color.color}')"></button>
                    <span>${color.name}</span>
                    <button onclick="deleteCustomColor('${room}', '${color.name}')">Eliminar</button>
                `;
                customColorsDiv.appendChild(colorDiv);
            });
        }

        function toggleLight(room) {
            data.rooms[room].lightOn = !data.rooms[room].lightOn;
            updateLightingControls();
        }

        function changeColor(room, color) {
            data.rooms[room].lightColor = color;
        }

        function changeBrightness(room, brightness) {
            data.rooms[room].brightness = brightness;
        }

        function saveCustomColor(room) {
            const name = document.getElementById('newColorName').value;
            const color = data.rooms[room].lightColor;
            if (name && color) {
                data.customColors[room].push({ name, color });
                updateCustomColors(room);
                document.getElementById('newColorName').value = '';
            }
        }

        function applyCustomColor(room, color) {
            data.rooms[room].lightColor = color;
            document.querySelector(`#lightingControls input[type="color"]`).value = color;
        }

        function deleteCustomColor(room, name) {
            data.customColors[room] = data.customColors[room].filter(c => c.name !== name);
            updateCustomColors(room);
        }

        function updateGardenInfo() {
            const gardenInfo = document.getElementById('gardenInfo');
            gardenInfo.innerHTML = `
                <p>Luz solar: ${data.garden.sunlight}%</p>
                <p>Humedad del suelo: ${data.garden.soilMoisture}%</p>
            `;
        }

        function startWatering() {
            alert('Sistema de riego activado');
        }

        // Inicialización
        function init() {
            updateSensorSummary();
            updateEnergyChart();
            updateAccessLog();
            updateGardenInfo();

            const roomSelect = document.getElementById('roomSelect');
            for (const room in data.rooms) {
                const option = document.createElement('option');
                option.value = room;
                option.textContent = room.replace('_', ' ');
                roomSelect.appendChild(option);
            }
            roomSelect.addEventListener('change', updateLightingControls);

            updateLightingControls();

            // Actualizar datos cada 60 segundos
            setInterval(() => {
                // Aquí se simularía la obtención de nuevos datos del backend
                updateSensorSummary();
                updateEnergyChart();
                updateAccessLog();
                updateGardenInfo();
            }, 60000);
        }

        window.onload = init;