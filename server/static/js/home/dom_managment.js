import {fetchESPList, toggleButtonState} from "./api_fetch.js"

let openBtns = document.querySelectorAll(".open-modal");
let nameBtns = document.querySelectorAll("#esp-name");
const closeBtns = document.querySelectorAll(".close-modal");
const modal = document.querySelector("[data-modal]");
const confirmBtn = document.querySelector("[confirm-btn]");
const btnHome = document.getElementById("btnHome");
const btnDevices = document.getElementById("btnDevices");
const btnRooms = document.getElementById("btnRooms");
const btnLights = document.getElementById("btnLights");
const sctDevices = document.getElementById("esp-list-sct");
const sctRooms =  document.getElementById("sensor-container-sct");
const sctLigth =  document.getElementById("ON-OFF_button-cont");

var esp_to_delete = "";

export function DOM_init(){

    btnHome.addEventListener("click", ()=>{
        mostrarTodos();
    })
    
    btnDevices.addEventListener("click", ()=>{
        ocultarTodos();
        sctDevices.style.display = "block";
        btnDevices.classList.add('selected');
    })
    
    btnRooms.addEventListener("click", ()=>{
        ocultarTodos();
        sctRooms.style.display = "block";
        btnRooms.classList.add('selected');
    })
    
    btnLights.addEventListener("click", ()=>{
        ocultarTodos();
        sctLigth.style.display = "block";
        btnLights.classList.add('selected');
    })
    
    closeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            modal.close();
        })
    });
    
    confirmBtn.addEventListener("click", () =>{
        //console.log(esp_to_delete + " deleted");    // TODO: fetch para eliminar ESP
        //FIXME: a veces hace multiples llamados
        fetch('/eliminar_item/' + esp_to_delete, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
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
            console.log(data);
            fetchESPList();
        })
        .catch(error => {
            console.error('Error removing ' + esp_to_delete, error);
        });
        modal.close();
    })
    

}

function mostrarTodos(){
    sctDevices.style.display = "block";
    btnDevices.classList.remove('selected');
    sctRooms.style.display = "block";
    btnRooms.classList.remove('selected');
    sctLigth.style.display = "block";
    btnLights.classList.remove('selected');
}

function ocultarTodos(){
    sctDevices.style.display = "none";
    btnDevices.classList.remove('selected');
    sctRooms.style.display = "none";
    btnRooms.classList.remove('selected');
    sctLigth.style.display = "none";
    btnLights.classList.remove('selected');
}

//esta funcion es porque los botones para abrir el modal se van generando dinamicamente
export function botones(){
    openBtns = document.querySelectorAll(".open-modal");
    nameBtns = document.querySelectorAll("#esp-name");

    //Botones que manejan la eliminacion de uns ESP de la lista
    openBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            modal.showModal();
            esp_to_delete = btn.parentElement.textContent.slice(0, -1);
            //document.querySelector("[data-modal]").style.display = flex;
        })
    });
    //Botones para redirigirse a la pagina con detalles del ESP
    nameBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            // Guardar el device_id en el sessionStorage
            sessionStorage.setItem('selectedDeviceID', btn.textContent);
            
            // Redirigir a la página de detalles
            window.location.href = "/device";
        })
    });
}

export function add_new_ESP_card(espInfo){
    const container = document.querySelector('.esp-cards-container');

    // Crea una tarjeta para cada ESP
    const card = document.createElement('div');
    card.classList.add('esp-card');

    const idElement = document.createElement('p');
    idElement.innerHTML = `${espInfo.ID}<span class="estado base" id="esp-id-estado"></span><span data-open-modal class="open-modal">x</span>`;
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

    //aniade funcionalidad a los botones de la tarjeta
    botones();

    if (espInfo.type == "Sensor"){
        add_sensor_card(espInfo);
    }
    if (espInfo.type == "Actuador"){
        add_actuator_card(espInfo);
    }
}

export function add_sensor_card(espInfo){
    const container = document.querySelector('.sensor-cards-container');

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

export function add_actuator_card(espInfo){
    const container = document.querySelector('.actuator-cards-container');

    // Crea una tarjeta para cada ESP
    const card = document.createElement('div');
    card.classList.add('actuator-card');

    const idItem = document.createElement('h4');
    idItem.innerHTML = `${espInfo.ID}`;
    idItem.id = 'actuator-id';
    
    const btnItem = document.createElement('button');
    btnItem.textContent = `${espInfo.data['switch']}`; //FIXME: escribe siempre Off como vlaor inicial
    btnItem.id = `toggleButton`;
    btnItem.classList.add(espInfo.data['switch'] == "OFF" ? "statusOFF" : "statusON");
    btnItem.onclick = function() {
        toggleButtonState(this);
    };
    
    // Añade a la tarjeta la info correspondiente
    card.appendChild(idItem);
    card.appendChild(btnItem);

    // Añade la tarjeta al contenedor
    container.appendChild(card);
}

export function sensor_update(data){
    const listSensorID = document.querySelectorAll('#sensor-id');
    Array.from(listSensorID).find((h4) => {

        if (h4.textContent == data.ID){
            h4.parentElement.querySelector("#sensor-temp").innerHTML = data.data['temperatura'];
            h4.parentElement.querySelector("#sensor-hum").innerHTML = data.data['humedad'];
        }
    });
}