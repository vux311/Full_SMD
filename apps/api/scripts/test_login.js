const axios = require('axios');

axios.post('http://localhost:9999/auth/login', { username: 'gv1', password: '123456' })
  .then(res => {
    console.log('status', res.status);
    console.log('data', res.data);
  })
  .catch(err => {
    if (err.response) {
      console.error('status', err.response.status);
      console.error(err.response.data);
    } else {
      console.error('error', err.message);
    }
    process.exit(1);
  });
