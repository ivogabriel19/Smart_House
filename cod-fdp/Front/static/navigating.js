const btnHome = document.getElementById("btnHome");
const btnDevices = document.getElementById("btnDevices");
const btnRooms = document.getElementById("btnRooms");
const btnLights = document.getElementById("btnLights");

function mostrarTodos(){
    btnHome.style.display = "block"
    btnDevices.style.display = "block"
    btnRooms.style.display = "block"
    btnLights.style.display = "block"
}

function ocultarTodos(){
    btnHome.style.display = "none"
    btnDevices.style.display = "none"
    btnRooms.style.display = "none"
    btnLights.style.display = "none"
}

btnDevices.addEventListener("click", ()=>{
    ocultarTodos();
    btnDevices.style.display = "block"
})

btnRooms.addEventListener("click", ()=>{
    ocultarTodos();
    btnRooms.style.display = "block"
})

btnLights.addEventListener("click", ()=>{
    ocultarTodos();
    btnLights.style.display = "block"
})