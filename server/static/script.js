function fetchESPList() {
    fetch('/api/esp/list')
        .then(response => response.json())
        .then(data => {

            const espList = document.getElementById('espList');
            espList.innerHTML = ''; // Limpiar la lista actual

            // Para cada objeto en el array, obtenemos la clave (nombre del ESP32)
            Object.keys(data).forEach(key => {
                const details = data[key];
                console.log(`Device: ${key}`);
                console.log(`IP: ${details.ip}`);
                console.log(`Status: ${details.status}`);
                console.log('-------------');
                
                const li = document.createElement('li');
                li.textContent = `ESP ID: ${key} || IP: ${details.ip}, Status: ${details.status}`;
                espList.appendChild(li);
            });
            
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = fetchESPList;