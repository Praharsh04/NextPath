document.addEventListener('DOMContentLoaded', async function() {
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');
    const loadingSpinner = document.getElementById('loadingSpinner');

    if (!userId) {
        alert('Error: User ID not provided.');
        window.location.href = 'index.html'; // Redirect back to initial page
        return;
    }

    // Show loading spinner
    loadingSpinner.classList.remove('spinner-hidden');

    try {
        const response = await fetch('http://127.0.0.1:5000/generate_roadmap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }),
        });

        const data = await response.json();

        if (response.ok) {
            sessionStorage.setItem('roadmapData', JSON.stringify(data));
            window.location.href = `roadmap.html?user_id=${userId}`;
        } else {
            alert('Error generating roadmap: ' + (data.error || 'Unknown error'));
            window.location.href = 'index.html'; // Redirect back to initial page on error
        }
    } catch (error) {
        console.error('Fetch error:', error);
        alert('Error: Could not connect to the backend server.');
        window.location.href = 'index.html'; // Redirect back to initial page on connection error
    } finally {
        // Hide loading spinner (though page redirect will happen before this is visible)
        loadingSpinner.classList.add('spinner-hidden');
    }
});