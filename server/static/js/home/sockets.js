import {sensor_update, add_new_ESP_card} from "./dom_managment.js"

export function sockets_init(){
    // Conectar al servidor Flask a través de WebSockets
    const socket = io();

    // Evento cuando el cliente se conecta
    socket.on('connect', () => {
        console.log('Conectado al servidor');
    });

    // Evento para recibir mensajes del servidor
    socket.on('sensor_update', (data) => {
        sensor_update(data);
    });

    //Evento para mostrar nuevos ESP que se conecten
    socket.on('add_ESP_to_List', espInfo => {
        console.log("New ESP from server");
        add_new_ESP_card(espInfo);
    });

    // Evento para manejar la desconexión
    socket.on('refresh_ESP_status', () => {
        refresh_ESP_status();
    });

    // Evento para manejar la desconexión
    socket.on('disconnect', () => {
        console.log('Desconectado del servidor');
    });
}