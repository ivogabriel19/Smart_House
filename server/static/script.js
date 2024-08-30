let buttonState = "OFF";

function fetchESPList() {
    fetch('/api/esp/list')
        .then(response => response.json())
        .then(data => {

            const espList = document.getElementById('espList');
            espList.innerHTML = ''; // Limpiar la lista actual

            // Para cada objeto en el array, obtenemos la clave (nombre del ESP32)
            Object.keys(data).forEach(key => {
                const details = data[key];
                console.log(`Device: ${key}`);
                console.log(`IP: ${details.ip}`);
                console.log(`Status: ${details.status}`);
                console.log('-------------');
                
                const li = document.createElement('li');
                li.textContent = `ESP ID: ${key} || IP: ${details.ip}, Status: ${details.status}`;
                espList.appendChild(li);
            });
            
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

function toggleButtonState() {
    // Cambia el estado del botón
    buttonState = buttonState === "OFF" ? "ON" : "OFF";
    document.getElementById('toggleButton').innerText = buttonState;

    // Envía el estado del botón al servidor Flask
    fetch('/update_button', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: buttonState }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Función para simular la obtención de datos JSON desde el servidor
function dummy_fetchSensorData() {
    // Supongamos que este JSON se obtiene de una respuesta HTTP desde un servidor Flask
    const sensorData = {
        "temperatura": "29.6º",
        "humedad": "50.0%"
    };

    // Actualiza el contenido de los elementos del DOM
    document.getElementById('temperature').innerText = sensorData.temperatura;
    document.getElementById('humidity').innerText = sensorData.humedad;
}

// Función para simular la obtención de datos JSON desde el servidor
function fetchSensorData() {
    // Envía el estado del botón al servidor Flask
    fetch('/get-TyH')
        .then(response => response.json())
        .then(data => {
            console.log('GET TyH c/5s:', data);
            // console.log('Temperatura:', data.temperatura);
            // console.log('Humedad:', data.humedad);

            
            // Actualiza el contenido de los elementos del DOM
            document.getElementById('temperature').innerText = data.temperatura;
            document.getElementById('humidity').innerText = data.humedad;
    })
    .catch((error) => {
        console.error('Error:', error);
    });

}

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = fetchESPList;
setInterval(fetchSensorData, 60000);