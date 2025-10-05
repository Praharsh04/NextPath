document.getElementById('generateButton').addEventListener('click', async function() {
    const userId = document.getElementById('userIdInput').value;
    const container = document.querySelector('.container');

    if (!userId) {
        alert('Please enter a User ID.');
        return;
    }

    // Create and display loading spinner
    let loadingSpinner = document.getElementById('loadingSpinner');
    if (!loadingSpinner) {
        loadingSpinner = document.createElement('div');
        loadingSpinner.id = 'loadingSpinner';
        loadingSpinner.innerHTML = '<div class="loader"></div><p>Generating Roadmap...</p>';
        container.appendChild(loadingSpinner);
    }
    loadingSpinner.classList.remove('spinner-hidden');

    // Clear previous roadmap data if any
    let roadmapDisplay = document.getElementById('roadmapDisplay');
    if (roadmapDisplay) {
        roadmapDisplay.remove();
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/generate_roadmap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }),
        });

        const data = await response.json();

        // Hide loading spinner
        loadingSpinner.classList.add('spinner-hidden');

        // Display roadmap data
        roadmapDisplay = document.createElement('pre');
        roadmapDisplay.id = 'roadmapDisplay';
        if (response.ok) {
            roadmapDisplay.textContent = JSON.stringify(data, null, 2);
        } else {
            roadmapDisplay.textContent = 'Error: ' + (data.error || 'Unknown error');
        }
        container.appendChild(roadmapDisplay);

    } catch (error) {
        console.error('Fetch error:', error);
        // Hide loading spinner
        loadingSpinner.classList.add('spinner-hidden');
        // Display error message
        roadmapDisplay = document.createElement('pre');
        roadmapDisplay.id = 'roadmapDisplay';
        roadmapDisplay.textContent = 'Error: Could not connect to the backend server.';
        container.appendChild(roadmapDisplay);
    }
});