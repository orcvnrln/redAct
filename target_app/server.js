const express = require('express');
const app = express();
const port = 8000;

app.use(express.json());

// Intentional: hardcoded secret (Gitleaks should catch this)
const API_SECRET = 'sk_test_abc123def456ghi789';

const users = [
  { id: 1, name: 'User A', role: 'user' },
  { id: 2, name: 'User B', role: 'user' },
  { id: 3, name: 'Admin', role: 'admin' },
];

// Intentional: no auth check (auth bypass)
app.get('/api/users/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (user) {
    res.json(user);
  } else {
    res.status(404).json({ error: 'Not found' });
  }
});

// Intentional: IDOR - no ownership check
app.get('/api/profile/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (user) {
    res.json({ ...user, secret: 'PII-data-for-' + user.id });
  } else {
    res.status(404).json({ error: 'Not found' });
  }
});

// Intentional: secret exposure via debug endpoint
app.get('/api/debug/env', (req, res) => {
  res.json({ secret: API_SECRET });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`target_app listening on port ${port}`);
});