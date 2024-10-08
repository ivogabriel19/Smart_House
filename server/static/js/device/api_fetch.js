import {add_ESP_card, add_sensor_card, add_add_event_button} from "./dom_managment.js"
import { device_id } from "../device.js";

export let device_data = {};
export let event_to_delete = "";

let openBtns = document.querySelectorAll(".open-modal");
const modal = document.querySelector("[data-modal]");

export function getEsp(){
    fetch('/leer_item/'+ device_id)
        .then(response => response.json())
        .then(data => {
            device_data = data;
            add_ESP_card(data);
            if (data.type == "Sensor"){
                add_sensor_card(data);
            }
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

export function getEvents(){
    fetch('/get_esp_events/' + device_id)
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al obtener los eventos.');
        }
        return response.json();
    })
    .then(data => {
        // Obtener el contenedor donde se mostrarán los eventos
        const eventosContainer = document.querySelector('.eventos-container');
        eventosContainer.innerHTML = ''; // Limpiar el contenedor

        // Verificar si hay eventos
        if (data.events.length === 0) {
            eventosContainer.innerHTML = '<p>No hay eventos programados para este dispositivo.</p>';
        } else {
            // Recorrer los eventos y agregarlos al contenedor
            data.events.forEach(evento => {
                const eventDiv = document.createElement('div');
                eventDiv.classList.add('event');

                const eventAlias = document.createElement('p');
                eventAlias.classList.add('alias');
                eventAlias.innerHTML = `${evento.event_alias}`;

                // Crear los elementos para mostrar los detalles del evento
                const jobId = document.createElement('p');
                jobId.innerHTML = `<small><small>${evento.job_id}</small></small><span data-open-modal class="open-modal">x</span>`;

                const eventType = document.createElement('p');
                eventType.textContent = `Tipo de evento: ${evento.event_type}`;

                const eventAction = document.createElement('p');
                eventAction.textContent = `Acción: ${evento.event_action}`;

                const eventData = document.createElement('pre');
                eventData.textContent = `Datos del evento: ${JSON.stringify(evento.event_data, null, 2)}`;

                // Agregar los detalles del evento al div
                eventDiv.appendChild(eventAlias);
                eventDiv.appendChild(jobId);
                eventDiv.appendChild( document.createElement('br') );
                eventDiv.appendChild(eventType);
                eventDiv.appendChild(eventAction);
                eventDiv.appendChild(eventData);

                // Insertar el evento en el contenedor de eventos
                eventosContainer.appendChild(eventDiv);
            });

            openBtns = document.querySelectorAll(".open-modal");

            //Botones que manejan la eliminacion de uns ESP de la lista
            openBtns.forEach(btn => {
                btn.addEventListener("click", () => {
                    modal.showModal();
                    event_to_delete = btn.parentElement.textContent.slice(0, -1);
                    //document.querySelector("[data-modal]").style.display = flex;
                })
            });
        }
        
        add_add_event_button();
    })
    .catch(error => {
        console.error('Error:', error);
        const eventosContainer = document.querySelector('.eventos-container');
        eventosContainer.innerHTML = `<p>Error al cargar los eventos: ${error.message}</p>`;
        add_add_event_button();
    });
}

// Función para obtener los datos históricos del backend Flask
export async function fetchHistoricalData(deviceId) {
    const response = await fetch(`/historico/${deviceId}`);
    const data = await response.json();
    return data;
}