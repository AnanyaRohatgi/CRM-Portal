document.getElementById('loginForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const username = e.target[0].value;
  const password = e.target[1].value;
  console.log("Username:", username);
  console.log("Password:", password);
  alert("Login submitted (not functional yet)");
});
