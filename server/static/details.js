const device_id = sessionStorage.getItem('selectedDeviceID');
const homeBtn = document.getElementById("btnHome");

homeBtn.addEventListener("click", () => {
    window.location.href = "/";
})

function getEsp(){
    console.log(device_id);
}

window.onload = getEsp();