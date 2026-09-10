import {add_sensor_card, add_actuator_card, botones} from "./dom_managment.js"

let buttonState = "OFF";

//OK: estructura
export function fetchESPList() {
    fetch('/api/esp/list')
        .then(response => response.json())
        .then(data => {

            const containerESP = document.querySelector('.esp-cards-container');
            containerESP.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas

            const containerSensors = document.querySelector('.sensor-cards-container');
            containerSensors.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas
            
            const containerActuators = document.querySelector('.actuator-cards-container');
            containerActuators.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas

            for (const espId in data) {
                if (data.hasOwnProperty(espId)) {
                    const espInfo = data[espId];
                    console.log(data[espId]);
        
                    // Crea una tarjeta para cada ESP
                    const card = document.createElement('div');
                    card.classList.add('esp-card');
        
                    const idElement = document.createElement('p');
                    idElement.innerHTML = `<span id="esp-name">${espInfo.ID}</span><span class="estado base" id="esp-id-estado"></span><span data-open-modal class="open-modal">x</span>`;
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
                    containerESP.appendChild(card);

                    if (espInfo.type == "Sensor"){
                        add_sensor_card(espInfo);
                    }
                    if (espInfo.type == "Actuador"){
                        add_actuator_card(espInfo);
                    }
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

            botones();
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

export function toggleButtonState(btn) {

    button = btn;
    buttonState = btn.textContent
    button_esp_id = btn.parentElement.querySelector("#actuator-id").textContent
    
    // Envía el estado del botón al servidor Flask
    fetch('/update_button', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({  state: buttonState , 
                                esp_id: button_esp_id
                            }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    if (buttonState === "OFF"){
        btn.textContent = "ON";
        btn.classList.remove("statusOFF");
        btn.classList.add("statusON")
    } else if (buttonState === "ON"){
        btn.textContent = "OFF";
        btn.classList.remove("statusON");
        btn.classList.add("statusOFF")
    } 


    // Cambia el estado del botón
    buttonState = buttonState === "OFF" ? "ON" : "OFF";
    //esp_ip = document.getElementById('ip_destino').value;
    btn.textContent = buttonState; //cambio el estado del boton en el front
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

//FIXME: estructura
export function refresh_ESP_status(){
    console.log("refreshing ESPs status");
    fetch('/api/esp/list')
    .then(response => response.json())
    .then(data => {
        for (const espId in data) {
            if (data.hasOwnProperty(espId)) {
                
                const espInfo = data[espId];
                const listSpans = document.querySelectorAll('#esp-id-estado');
                Array.from(listSpans).find((spanEstado) => {

                    if (spanEstado.parentElement.textContent.slice(0, -1) == espInfo.ID){
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