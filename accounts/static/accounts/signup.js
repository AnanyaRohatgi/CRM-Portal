// Wait for the entire HTML document to be fully loaded and parsed.
document.addEventListener('DOMContentLoaded', (event) => {

    // Find the sign-up button by its ID.
    const signUpButton = document.getElementById('signup-btn');

    // Check if the button exists on the page to avoid errors.
    if (signUpButton) {
        // Add a 'click' event listener to the button.
        signUpButton.addEventListener('click', redirectToLogin);
    }

});

/**
 * This function redirects the user to the login page.
 * In a real-world scenario, you would first send the form data to the server
 * for validation and user creation before redirecting.
 */
function redirectToLogin() {
    console.log("Sign Up button clicked. Redirecting to the login page...");
    
    // IMPORTANT: Change '/login/' to the actual URL of your login page in your Django urls.py.
    window.location.href = '/login/'; 
}