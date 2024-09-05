let buttonState = "OFF";

// Conectar al servidor Flask a través de WebSockets
const socket = io();

function fetchESPList() {
    fetch('/api/esp/list')
        .then(response => response.json())
        .then(data => {

            const container = document.querySelector('.cards-container');
            container.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas

            for (const espId in data) {
                if (data.hasOwnProperty(espId)) {
                    const espInfo = data[espId];
                    console.log(data[espId]);
        
                    // Crea una tarjeta para cada ESP
                    const card = document.createElement('div');
                    card.classList.add('card');
        
                    const idElement = document.createElement('p');
                    idElement.innerHTML = `${espId}<span class="estado base" id="esp-id-estado"></span>`;
                    idElement.id = 'esp-id';
                    
                    const list = document.createElement('ul');
                    
                    const ipItem = document.createElement('li');
                    ipItem.innerHTML = `<strong>IP:</strong> <span id="esp-ip">${espInfo.IP}</span>`;
                    
                    const macItem = document.createElement('li');
                    macItem.innerHTML = `<strong>MAC:</strong> <span id="esp-mac">${espInfo.MAC}</span>`;
                    
                    const statusItem = document.createElement('li');
                    statusItem.innerHTML = `<strong>Status:</strong> <span id="esp-status">${espInfo.status}</span>`;
                    
                    const typeItem = document.createElement('li');
                    typeItem.innerHTML = `<strong>Type:</strong> <span id="esp-type">${espInfo.type}</span>`;
                    
                    list.appendChild(ipItem);
                    list.appendChild(macItem);
                    list.appendChild(statusItem);
                    list.appendChild(typeItem);
                    
                    card.appendChild(idElement);
                    card.appendChild(list);
                    
                    // Añade la tarjeta al contenedor
                    container.appendChild(card);
                }
            }
            // Para cada objeto en el array, obtenemos la clave (nombre del ESP32)
            // Object.keys(data).forEach(key => {
            //     const details = data[key];
            //     console.log(`Device: ${key}`);
            //     console.log(`IP: ${details.ip}`);
            //     console.log(`Status: ${details.status}`);
            //     console.log('-------------');
                
            //     const li = document.createElement('li');
            //     li.textContent = `ESP ID: ${key} || IP: ${details.ip}, Status: ${details.status}`;
            //     espList.appendChild(li);
            // });
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

function toggleButtonState() {
    // Cambia el estado del botón
    buttonState = buttonState === "OFF" ? "ON" : "OFF";
    esp_ip = document.getElementById('ip_destino').value;
    document.getElementById('toggleButton').innerText = buttonState;

    // Envía el estado del botón al servidor Flask
    fetch('/update_button', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({  state: buttonState , 
                                destination_ip: esp_ip
                            }),
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

function refresh_ESP_list(){
    console.log("refreshing ESP List");
    fetch('/api/esp/list')
    .then(response => response.json())
    .then(data => {
        for (const espId in data) {
            if (data.hasOwnProperty(espId)) {
                
                const espInfo = data[espId];
                //FIXME: seleccionar el span especifico de la tarjeta correspondiente al esp actual
                const listSpans = document.querySelectorAll('#esp-id-estado');
                Array.from(listSpans).find(function(spanEstado) {

                    if (spanEstado.parentElement.textContent == espId){
                        spanEstado.classList.remove('conectado', 'verificando', 'desconectado', 'base')
    
                        console.log(espId + " status: " + espInfo.status );
    
                        if (espInfo.status == "Online")
                            spanEstado.classList.add('conectado')
                        if (espInfo.status == "Verificando")
                            spanEstado.classList.add('verificando')
                        if (espInfo.status == "Offline")
                            spanEstado.classList.add('desconectado')
                    }
                });
                

            }
        }
        console.log("");
    
    })
    .catch(error => {
        console.error('Error fetching ESP list:', error);
    });
}

// Evento cuando el cliente se conecta
socket.on('connect', () => {
    console.log('Conectado al servidor');
});

// Evento para recibir mensajes del servidor
socket.on('sensor_update', (data) => {
    console.log('GET TyH c/sockets:', data);
            
    // Actualiza el contenido de los elementos del DOM
    document.getElementById('temperature').innerText = data.temperatura;
    document.getElementById('humidity').innerText = data.humedad;
});

//Evento para mostrar nuevos ESP que se conecten
socket.on('add_ESP_to_List', data => {
    console.log("New ESP from server");
    //console.log(data);

    const container = document.querySelector('.cards-container');

    Object.keys(data).forEach(espId => {
            // const details = data[espId];
            // console.log(`Device: ${espId}`);
            // console.log(`IP: ${details.ip}`);
            // console.log(`MAC: ${details.mac}`);
            // console.log(`Status: ${details.status}`);
            // console.log('-------------');

            const espInfo = data[espId];
        
            // Crea una tarjeta para cada ESP
            const card = document.createElement('div');
            card.classList.add('card');

            const idElement = document.createElement('p');
            idElement.innerHTML = `${espId}<span class="estado base" id="esp-id-estado"></span>`;
            idElement.id = 'esp-id';
            
            const list = document.createElement('ul');
            
            const ipItem = document.createElement('li');
            ipItem.innerHTML = `<strong>IP:</strong> <span id="esp-ip">${espInfo.IP}</span>`;
            
            const macItem = document.createElement('li');
            macItem.innerHTML = `<strong>MAC:</strong> <span id="esp-mac">${espInfo.MAC}</span>`;
            
            const statusItem = document.createElement('li');
            statusItem.innerHTML = `<strong>Status:</strong> <span id="esp-status">${espInfo.status}</span>`;
            
            const typeItem = document.createElement('li');
            typeItem.innerHTML = `<strong>Type:</strong> <span id="esp-type">${espInfo.type}</span>`;
            

            list.appendChild(ipItem);
            list.appendChild(macItem);
            list.appendChild(statusItem);
            list.appendChild(typeItem);
            
            card.appendChild(idElement);
            card.appendChild(list);
            
            // Añade la tarjeta al contenedor
            container.appendChild(card);
    });
});

// Evento para manejar la desconexión
socket.on('refresh_ESP_list', () => {
    refresh_ESP_list();
});

// Evento para manejar la desconexión
socket.on('disconnect', () => {
    console.log('Desconectado del servidor');
});

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = () => {
    fetchESPList();
    refresh_ESP_list();
    console.log("We are on live!");
};