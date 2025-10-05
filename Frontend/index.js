document.getElementById('generateButton').addEventListener('click', async function() {
    const userId = document.getElementById('userIdInput').value;

    if (!userId) {
        alert('Please enter a User ID.');
        return;
    }

    // First, check if the roadmap already exists
    try {
        const checkResponse = await fetch(`http://127.0.0.1:5000/check_roadmap/${userId}`);
        const checkData = await checkResponse.json();

        if (checkData.exists) {
            // If roadmap exists, fetch it and go directly to roadmap page
            const roadmapResponse = await fetch('http://127.0.0.1:5000/generate_roadmap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId }),
            });
            const roadmapData = await roadmapResponse.json();
            if (roadmapResponse.ok) {
                sessionStorage.setItem('roadmapData', JSON.stringify(roadmapData));
                window.location.href = `roadmap.html?user_id=${userId}`;
            } else {
                alert('Error fetching existing roadmap: ' + (roadmapData.error || 'Unknown error'));
            }
        } else {
            // If roadmap does not exist, go to loading page to generate
            window.location.href = `loading.html?user_id=${userId}`;
        }
    } catch (error) {
        console.error('Error checking roadmap existence:', error);
        alert('Error connecting to backend to check roadmap.');
    }
});