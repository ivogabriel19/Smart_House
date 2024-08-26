function fetchESPList() {
    fetch('/api/esp/list')
        .then(response => response.json())
        .then(data => {
            const espList = document.getElementById('espList');
            espList.innerHTML = ''; // Limpiar la lista actual
            data.forEach(esp => {
                const li = document.createElement('li');
                li.textContent = `ESP ID: ${esp.id}, IP: ${esp.ip}`;
                espList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching ESP list:', error);
        });
}

// Llamar a la función para obtener la lista de ESP al cargar la página
window.onload = fetchESPList;