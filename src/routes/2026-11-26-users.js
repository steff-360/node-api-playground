// Router de usuarios con validacion basica
const express = require('express');
const router  = express.Router();
let users = [], nextId = 1;

function validate(body) {
  const errors = [];
  if (!body.name?.trim())                       errors.push('name requerido');
  if (!body.email?.includes('@'))               errors.push('email invalido');
  if (!body.password || body.password.length < 8) errors.push('password minimo 8 caracteres');
  return errors;
}

router.get('/', (req, res) => res.json(users.map(({ password, ...u }) => u)));
router.post('/', (req, res) => {
  const errors = validate(req.body);
  if (errors.length) return res.status(400).json({ errors });
  const { name, email, password } = req.body;
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email en uso' });
  const user = { id: nextId++, name, email, password, createdAt: new Date() };
  users.push(user);
  const { password: _, ...safeUser } = user;
  res.status(201).json(safeUser);
});
module.exports = router;
