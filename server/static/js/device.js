import {DOM_init, renderChart} from "./device/dom_managment.js"
import {getEsp, getEvents} from "./device/api_fetch.js"

export const device_id = sessionStorage.getItem('selectedDeviceID');

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = () => {
    getEsp();
    getEvents();
    DOM_init()
    renderChart();
};