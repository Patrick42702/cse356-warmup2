// document.getElementById('login-button').addEventListener('click', ()  => {
//     const loginform = document.getElementById('login-section')
//     loginform.style.setProperty("--display", "flex")
//     const welcome_section = document.getElementById('welcome-section')
//     welcome_section.style.setProperty("--display", "none")
// })
//
// document.getElementById('signup-button').addEventListener('click', ()  => {
//     const registerform = document.getElementById('register-section')
//     registerform.style.setProperty("--display", "flex")
//     const welcome_section = document.getElementById('welcome-section')
//     welcome_section.style.setProperty("--display", "none")
// })
//
// document.getElementById('redir-login-button').addEventListener('click', ()  => {
//     const registerform = document.getElementById('register-section')
//     registerform.style.setProperty("--display", "none")
//     const login_section = document.getElementById('login-section')
//     login_section.style.setProperty("--display", "flex")
// })
//
// document.getElementById('redir-register-button').addEventListener('click', ()  => {
//     const loginform = document.getElementById('login-section')
//     loginform.style.setProperty("--display", "none")
//     const registerform = document.getElementById('register-section')
//     registerform.style.setProperty("--display", "flex")
// })

// document.getElementById('register-form').addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const username = document.getElementById('register-username').value;
//     const password = document.getElementById('register-password').value;
//     const email = document.getElementById('register-email').value;
//
//     const response = await fetch('/api/adduser', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ username, password, email })
//     });
//     const result = await response.json();
//     document.getElementById('message').innerText = result.message;
//     document.getElementById('message').style.display = "block";
// });

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
    const result = await response.json();
    if (result.status === "ERROR"){
        document.getElementById('message').innerText = result.message;
        document.getElementById('message').style.display = "block";
    }
    else{
        console.log(`Login response: ${result}`);
        document.getElementById('message').innerText = result.message;
        location.reload();
    }
});
