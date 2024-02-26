// script.js

const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

function onGoogleSignIn() {
    gapi.auth2.getAuthInstance().signIn().then(
        function(googleUser) {
            // Handle successful Google sign-in
            onGoogleSignInSuccess(googleUser);
        },
        function(error) {
            // Handle failed Google sign-in
            console.error('Error signing in with Google:', error);
        }
    );
}

function onGoogleSignInSuccess(googleUser) {
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId());
    console.log('Name: ' + profile.getName());
    console.log('Email: ' + profile.getEmail());
    // You can send the user's data to your server for further processing
}

// Initialize the Google Sign-In API
function initializeGoogleSignIn() {
    gapi.load('auth2', function() {
        gapi.auth2.init({
            client_id: '14653485362-l0c3rn72l7bfouivmqeqq04ikrotrec5.apps.googleusercontent.com', // Replace with your actual client ID
        });
    });
}

// Call the initialization function when the page is loaded
window.onload = initializeGoogleSignIn;
