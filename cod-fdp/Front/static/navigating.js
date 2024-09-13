const btnHome = document.getElementById("btnHome");
const btnDevices = document.getElementById("btnDevices");
const btnRooms = document.getElementById("btnRooms");
const btnLights = document.getElementById("btnLights");
const sctDevices = document.getElementById("esp-list-sct");
const sctRooms =  document.getElementById("sensor-container-sct");
const sctLigth =  document.getElementById("ON-OFF_button-cont");

function mostrarTodos(){
    sctDevices.style.display = "block";
    sctRooms.style.display = "block";
    sctLigth.style.display = "block";
}

function ocultarTodos(){
    sctDevices.style.display = "none";
    sctRooms.style.display = "none";
    sctLigth.style.display = "none";
}

btnHome.addEventListener("click", ()=>{
    mostrarTodos();
})

btnDevices.addEventListener("click", ()=>{
    ocultarTodos();
    sctDevices.style.display = "block"
})

btnRooms.addEventListener("click", ()=>{
    ocultarTodos();
    sctRooms.style.display = "block"
})

btnLights.addEventListener("click", ()=>{
    ocultarTodos();
    sctLigth.style.display = "block"
})