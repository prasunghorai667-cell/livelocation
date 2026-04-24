document.getElementById('loginBtn').addEventListener('click', async () => {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const error = document.getElementById('error');
  const btn = document.getElementById('loginBtn');
  
  if (!username || !password) {
    error.textContent = 'Please enter username and password';
    error.classList.remove('hidden');
    return;
  }
  
  btn.disabled = true;
  btn.textContent = 'Logging in...';
  
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await res.json();
    
    if (res.ok && data.success) {
      window.location.href = data.redirect;
    } else {
      error.textContent = data.error || 'Login failed';
      error.classList.remove('hidden');
    }
  } catch (err) {
    error.textContent = 'Login failed. Please try again.';
    error.classList.remove('hidden');
  }
  
  btn.disabled = false;
  btn.textContent = 'Login';
});