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