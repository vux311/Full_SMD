(async () => {
  const base = process.env.API_BASE || 'http://localhost:9999';
  console.log('Testing API at', base);
  try {
    const loginRes = await fetch(`${base}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'admin', password: '123456' }),
    });

    let loginBody = null;
    try { loginBody = await loginRes.json(); } catch (e) { /* ignore */ }
    console.log('LOGIN status=', loginRes.status);
    console.log('LOGIN body=', loginBody);

    if (loginBody && loginBody.access_token) {
      const token = loginBody.access_token;
      const meRes = await fetch(`${base}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      let meBody = null;
      try { meBody = await meRes.json(); } catch (e) { /* ignore */ }
      console.log('/users/me status=', meRes.status);
      console.log('/users/me body=', meBody);
    } else {
      console.log('No access_token returned from login. Cannot test /users/me.');
    }
  } catch (err) {
    console.error('Error during API test:', err);
  }
})();