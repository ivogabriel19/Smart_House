import {device_data, event_to_delete, getEvents, fetchHistoricalData} from "./api_fetch.js"
import { device_id } from "../device.js";

const homeBtn = document.getElementById("btnHome");
const addEventBtn = document.getElementById("add-event-btn");
const event_modal = document.querySelector("[data-del-modal]");
const confirmdelBtn = document.querySelector("[confirm-del-btn]");
const closeBtn = document.querySelector(".close-del-modal");
const espSelect = document.getElementById("esp-id-select");
const typeSelect = document.getElementById("event-type");
const actionSelect = document.getElementById('event-action');
const optionsContainer = document.querySelector(".options");
const form = document.getElementById("event-form");

const closeBtns = document.querySelectorAll(".close-modal");
const modal = document.querySelector("[data-modal]");
const confirmBtn = document.querySelector("[confirm-btn]");

export function DOM_init(){

    homeBtn.addEventListener("click", () => {
        window.location.href = "/";
    })
    
    closeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            modal.close();
        })
    });
    
    confirmBtn.addEventListener("click", () =>{
        console.log(event_to_delete);
        fetch('/delete_event', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "device_id" : device_id,
                "job_id" : event_to_delete
            })
        })
        .then(response => {
            // Verificar el status code
            if (response.status === 200) {
                return response.json(); // Convertir la respuesta a JSON
            } else {
                throw new Error(`Error: Status code ${response.status}`);
            }
        }).then(data => {
            getEvents();
            console.log(data);
        })
        .catch(error => {
            console.error('Error removing ' + event_to_delete, error);
        });
        modal.close();
    })
    
    confirmdelBtn.addEventListener("click", (i) =>{
        // Obtener los valores de los campos
        const eventAlias = document.getElementById('event-alias').value;
        const eventType = document.getElementById('event-type').value;
        const eventAction = document.getElementById('event-action').value;
        let eventData;
    
        // Obtener los valores según el tipo de evento
        if (eventType === 'horario') {
            const time = document.getElementById('time').value;
            eventData = { time };
        } else if (eventType === 'fecha') {
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            eventData = { date, time };
        } else if (eventType === 'intervalo') {
            const interval = document.getElementById('interval').value;
            eventData = { interval };
        }
    
        fetch("/schedule-event", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({  'esp_id': device_id ,
                                    'eventAlias': eventAlias , 
                                    'eventAction': eventAction , 
                                    'eventType': eventType , 
                                    'eventData': eventData
                                }),
        })
        .then(response => response.json())
        .then(data => {
            getEvents();
        });
        console.log(eventData);
        event_modal.close();
    });
    
    typeSelect.addEventListener("change", () => {
        // Obtener el valor de la opción seleccionada
        const selectedOption = typeSelect.value;
        // console.log(selectedOption);
    
        const div = document.createElement('div');
        div.classList.add('form-group');
        
        optionsContainer.innerHTML = ``;
        if( selectedOption=="horario" ){
            div.innerHTML = `
                            <label for="time">Hora (hh:mm)</label>
                            <input type="time" id="time">
            `;
        } else if ( selectedOption=="fecha" ){
            div.innerHTML = `
                            <label for="date">Fecha</label>
                            <input type="date" id="date">
                            <label for="time">Hora (hh:mm)</label>
                            <input type="time" id="time">
            `;        
        } else if ( selectedOption=="intervalo" ){
            div.innerHTML = `
                            <label for="interval">Intervalo de Tiempo (minutos)</label>
                            <input type="number" id="interval">
            `;        
        }
    
        optionsContainer.appendChild(div);
    
    });    
}

export function add_ESP_card(esp){
    
    const containerESP = document.querySelector('.cards-container');
    containerESP.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas

    const espInfo = esp;

    // Crea una tarjeta para cada ESP
    const card = document.createElement('div');
    card.classList.add('esp-card');

    const idElement = document.createElement('p');
    idElement.innerHTML = `<span id="esp-name">${espInfo.ID}</span><span class="estado base" id="esp-id-estado"></span>`;
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
}

export function add_sensor_card(esp){
    var espInfo = esp;
    const container = document.querySelector('.cards-container');

    // Crea una tarjeta para cada ESP
    const card = document.createElement('div');
    card.classList.add('sensor-card');

    const idItem = document.createElement('h4');
    idItem.innerHTML = `${espInfo.ID}`;
    idItem.id = 'sensor-id';
    
    const tempItem = document.createElement('p');
    tempItem.innerHTML = `<strong>Temperatura:</strong> <span id="sensor-temp">${espInfo.data.temperatura}</span>`;
    
    const humItem = document.createElement('p');
    humItem.innerHTML = `<strong>Humedad:</strong> <span id="sensor-hum">${espInfo.data.humedad}</span>`;
    
    // Añade a la tarjeta la info correspondiente
    card.appendChild(idItem);
    card.appendChild(tempItem);
    card.appendChild(humItem);
    
    // Añade la tarjeta al contenedor
    container.appendChild(card);
}

export function add_add_event_button(){

    const btn = document.createElement('div');
    btn.classList.add('add-event-btn');
    btn.id = 'add-event-btn';            

    btn.innerHTML = `<span>+</span>añadir Evento`;
    
    const eventosContainer = document.querySelector('.eventos-container');
    eventosContainer.appendChild(btn);

    const _addEventBtn = document.getElementById("add-event-btn");

    _addEventBtn.addEventListener("click", () => {
        event_modal.showModal();
        //console.log("open!");
        const op = document.createElement('option');
        op.innerHTML = `<option value=${device_id}>${device_id}</option>`;
        espSelect.appendChild(op);
        espSelect.value = device_id;
        espSelect.disabled = true;

        if (device_data.type == "Actuador"){
            actionSelect.innerHTML = `<option value="activar">Activar actuador</option>
                                        <option value="desactivar">Desactivar Actuador</option>`;
        }
    })
}

// Función para renderizar el gráfico
export async function renderChart() {
    const deviceId = device_id;  // El ID del dispositivo
    const historicalData = await fetchHistoricalData(deviceId);

    // Extraer los datos necesarios para el gráfico
    const timestamps = historicalData.map(entry => entry.timestamp);
    const temperatures = historicalData.map(entry => entry.temperatura);
    const humidity = historicalData.map(entry => entry.humedad);

    const ctx = document.getElementById('historicoChart').getContext('2d');
    const historicoChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [
                {
                    label: 'Temperatura (°C)',
                    data: temperatures,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true
                },
                {
                    label: 'Humedad (%)',
                    data: humidity,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    fill: true
                }
            ]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Timestamps'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Mediciones'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}
