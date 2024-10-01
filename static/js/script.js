function take_screenshot() {
    console.log("SCREENSHSHOT")
    fetch('/take_screenshot', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert(data.status);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function record_clip() {
    console.log("CLIP")
    fetch('/record_clip', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert(data.status);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function toggle_yolo() {
    console.log("Toggeling")
    fetch('/toggle_yolo', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.show_yolo) {
            document.getElementById('toggleButton').innerText = 'Switch to Plain';
        } else {
            document.getElementById('toggleButton').innerText = 'Switch to YOLO';
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function sendZoomValue() {
    // Get the zoom value from the slider
    let zoomValue = document.getElementById('zoomSlider').value;
    
    // Send the zoom value to the server using a POST request
    fetch('/set_zoom', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ zoom: zoomValue }),
    })
    .then(response => response.text())  // Get the response as text to see the actual response content
    .then(data => {
        console.log('Success:', data);  // Log the text to see if it's an error page or JSON
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}