const homeBtn = document.getElementById("btnHome");
const jobListContainer = document.getElementById('job-list');

homeBtn.addEventListener("click", () => {
    window.location.href = "/";
})

// Función para obtener los eventos
function fetchJobs() {
    fetch('/get-events')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(jobs => {
            // Limpiar el contenedor
            jobListContainer.innerHTML = '';

            // Si no hay trabajos
            if (jobs.length === 0) {
                jobListContainer.innerHTML = '<p>No jobs scheduled.</p>';
                return;
            }

            // Crear una tabla para mostrar los trabajos
            const table = document.createElement('table');
            const headerRow = document.createElement('tr');
            const idHeader = document.createElement('th');
            const nameHeader = document.createElement('th');

            idHeader.textContent = 'Job ID';
            nameHeader.textContent = 'Job Name';
            headerRow.appendChild(idHeader);
            headerRow.appendChild(nameHeader);
            table.appendChild(headerRow);

            // Agregar cada trabajo a la tabla
            jobs.forEach(job => {
                const row = document.createElement('tr');

                const idCell = document.createElement('td');
                const nameCell = document.createElement('td');

                idCell.textContent = job.id; // Acceder al ID del trabajo
                nameCell.textContent = job.name; // Acceder al nombre del trabajo

                row.appendChild(idCell);
                row.appendChild(nameCell);
                table.appendChild(row);
            });

            // Agregar la tabla al contenedor
            jobListContainer.appendChild(table);
        })
        .catch(error => {
            console.error('Error fetching jobs:', error);
            jobListContainer.innerHTML = '<p>Error fetching jobs. Please try again later.</p>';
        });
}

// Llamar a la función para obtener los trabajos al cargar la página
window.onload = fetchJobs();
