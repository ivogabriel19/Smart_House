import {DOM_init} from "./home/dom_managment.js"
import {refresh_ESP_status, fetchESPList} from "./home/api_fetch.js"
import { sockets_init } from "./home/sockets.js";

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = () => {
    fetchESPList();
    refresh_ESP_status();
    DOM_init();
    sockets_init();
    console.log("We are on live!");
};  