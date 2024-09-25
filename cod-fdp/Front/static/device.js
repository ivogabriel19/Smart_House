const device_id = "ESP_from_sessionS";
const addEventBtn = document.getElementById("add-event-btn");
const event_modal = document.querySelector("[data-modal]");
const confirmBtn = document.querySelector("[confirm-btn]");
const closeBtn = document.querySelector(".close-modal");
const espSelect = document.getElementById("esp-id-select");
const typeSelect = document.getElementById("event-type");
const optionsContainer = document.querySelector(".options");
const form = document.getElementById("event-form");

addEventBtn.addEventListener("click", () => {
    event_modal.showModal();
    //console.log("open!");
    const op = document.createElement('option');
    op.innerHTML = `<option value="ESP_from_sessionS">ESP_from_sessionS</option>`;
    espSelect.appendChild(op);
    espSelect.value = device_id;
    espSelect.disabled = true;
})

closeBtn.addEventListener("click", () => {
    event_modal.close();
})

confirmBtn.addEventListener("click", (i) =>{
    // Obtener los valores de los campos
    const eventType = document.getElementById('event-type').value;

    // Obtener los valores según el tipo de evento
    if (eventType === 'horario') {
        const time = document.getElementById('time').value;
        eventData = { eventType, time };
    } else if (eventType === 'fecha') {
        const date = document.getElementById('date').value;
        const time = document.getElementById('time').value;
        eventData = { eventType, date, time };
    } else if (eventType === 'intervalo') {
        const interval = document.getElementById('interval').value;
        eventData = { eventType, interval };
    }

    //TODO fetchCrearEvento(esp_id, eventData)
    console.log(eventData);
    event_modal.close();
});

// Event Listener para el formulario
// form.addEventListener('submit', function(event) {
//     // Evitar que el formulario se envíe automáticamente
//     event.preventDefault();

//     // Obtener los valores de los campos
//     const eventType = document.getElementById('event-type').value;

//     // Obtener los valores según el tipo de evento
//     if (eventType === 'horario') {
//         const time = document.getElementById('time').value;
//         eventData = { eventType, time };
//     } else if (eventType === 'fecha') {
//         const date = document.getElementById('date').value;
//         const time = document.getElementById('time').value;
//         eventData = { eventType, date, time };
//     } else if (eventType === 'intervalo') {
//         const interval = document.getElementById('interval').value;
//         eventData = { eventType, interval };
//     }

//     //TODO fetchCrearEvento(esp_id, eventData)
//     console.log(eventData);
//     event_modal.close();
// });

typeSelect.addEventListener("change", () => {
    // Obtener el valor de la opción seleccionada
    const selectedOption = typeSelect.value;
    // console.log(selectedOption);

    const div = document.createElement('div');
    div.classList.add('form-group');
    
    optionsContainer.innerHTML= ``;
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