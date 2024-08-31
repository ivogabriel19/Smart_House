const data = {
        "Dummy_ESP1": {
            "IP": "0.0.0.1",
            "MAC" : "00:00:00:00:00:01",
            "status": "non-existent"
        },
        "Dummy_ESP2": {
            "IP": "0.0.0.2",
            "MAC" : "00:00:00:00:00:02",
            "status": "non-existent"
        },
        "Dummy_ESP3": {
            "IP": "0.0.0.3",
            "MAC" : "00:00:00:00:00:03",
            "status": "non-existent"
        }
    }

    const container = document.querySelector('.cards-container');
    container.innerHTML = ''; // Limpia el contenedor antes de añadir las nuevas tarjetas
    console.log(container);

    // Recorre cada ESP en el JSON
    for (const espId in data) {
        if (data.hasOwnProperty(espId)) {
            const espInfo = data[espId];

            // Crea una tarjeta para cada ESP
            const card = document.createElement('div');
            card.classList.add('card');

            const idElement = document.createElement('p');
            idElement.innerText = espId;
            idElement.id = 'esp-id';
            
            const list = document.createElement('ul');
            
            const ipItem = document.createElement('li');
            ipItem.innerHTML = `<strong>IP:</strong> <span id="esp-ip">${espInfo.IP}</span>`;
            
            const macItem = document.createElement('li');
            macItem.innerHTML = `<strong>MAC:</strong> <span id="esp-mac">${espInfo.MAC}</span>`;
            
            const statusItem = document.createElement('li');
            statusItem.innerHTML = `<strong>Status:</strong> <span id="esp-status">${espInfo.status}</span>`;
            
            list.appendChild(ipItem);
            list.appendChild(macItem);
            list.appendChild(statusItem);
            
            card.appendChild(idElement);
            card.appendChild(list);
            
            // Añade la tarjeta al contenedor
            container.appendChild(card);
        }
    }