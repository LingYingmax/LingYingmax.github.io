const userLoginForm = document.querySelector('#user-login-form');
const userLoginMessage = document.querySelector('#user-login-message');

userLoginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(userLoginForm);
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.fromEntries(formData))
  });
  if (!response.ok) {
    userLoginMessage.textContent = 'Invalid username or password.';
    return;
  }
  const data = await response.json();
  localStorage.setItem('lingyingmax_admin_token', data.access_token);
  localStorage.setItem('lingyingmax_user_role', data.role || 'user');
  const next = new URLSearchParams(window.location.search).get('next');
  window.location.href = next || 'index.html';
});
