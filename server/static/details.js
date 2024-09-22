const device_id = sessionStorage.getItem('selectedDeviceID');
const homeBtn = document.getElementById("btnHome");

homeBtn.addEventListener("click", () => {
    window.location.href = "/";
})

function getEsp(){
    fetch('/leer_item/'+device_id)
        .then(response => response.json())
        .then(data => {
            add_ESP_card(data);
            add_sensor_card(data);
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

function add_ESP_card(esp){
    
    const containerESP = document.querySelector('.cards-container');
    containerESP.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas

    const espInfo = esp;

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
}

function add_sensor_card(esp){
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

window.onload = getEsp();