function take_snapshot() {
    console.log("Snapshot")
    fetch('/take_snapshot', {
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
    console.log("record_clip")
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

document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const query = document.getElementById('search').value; // Get the value from the input

    // Send the query to the Flask backend using fetch
    fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => response.text())
        .then(data => {
            document.getElementById('results').innerHTML = data; // Display the results in the 'results' div
        })
        .catch(error => console.error('Error:', error));
});