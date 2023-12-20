import {
  getRedirectLink,
} from "./utils.js";

const overlay = document.querySelector('.overlay');
const loginForm = document.getElementById('loginForm');
const errorMessageContainer = document.querySelector('.error');
const successMessageContainer = document.querySelector('.success');
const redirectLink = document.getElementById('redirectLink');

// Function to show message container with animation
function showMessage(name='success') {
    overlay.style.display = 'block';
    let container = successMessageContainer;
    if (name === 'error') {
        container = errorMessageContainer;
        setTimeout(() => {
            overlay.style.display = 'none';
            container.style.display = 'none';
        }, 3000);

        document.addEventListener('click', function closeMessage() {
            overlay.style.display = 'none';
            container.style.display = 'none';
            document.removeEventListener('click', closeMessage);
        });
    }
    container.style.display = 'block';
    container.classList.add('animate-show');
}

loginForm.addEventListener('submit', function(e) {
    e.preventDefault();

    // Getting form data
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Send a POST request
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username, password})
    })
    .then(response => response.json())
    .then(data => {
        // Jump page based on response
        if (data.success) {
            showMessage();
            const redirectTo = getRedirectLink();
            redirectLink.href = redirectTo;
            setTimeout(() => {
                window.location.href = redirectTo;
            }, 3000); // Redirect after 3 seconds
            
        } else {
            showMessage('error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Empty form
    e.target.reset();
});
