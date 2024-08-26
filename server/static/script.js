function fetchESPList() {
    fetch('/api/esp/list')
        .then(response => response.json())
        .then(data => {
            const espList = document.getElementById('espList');
            espList.innerHTML = ''; // Limpiar la lista actual
            data.keys(ESP).forEach(key => {
                const details = ESP[key];
                const li = document.createElement('li');
                li.textContent = `ESP ID: ${key}, IP: ${details.ip}, Status: ${details.status}`;
                espList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = fetchESPList;