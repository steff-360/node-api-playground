// Router de tareas con CRUD completo
const express = require('express');
const router  = express.Router();
let tasks = [], nextId = 1;

router.get('/',    (req, res) => {
  const { done, q } = req.query;
  let result = tasks;
  if (done !== undefined) result = result.filter(t => String(t.done) === done);
  if (q)                  result = result.filter(t => t.title.includes(q));
  res.json({ total: result.length, data: result });
});
router.get('/:id', (req, res) => {
  const t = tasks.find(t => t.id === +req.params.id);
  t ? res.json(t) : res.status(404).json({ error: 'Not found' });
});
router.post('/', (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(400).json({ error: 'title required' });
  const task = { id: nextId++, title, done: false, createdAt: new Date() };
  tasks.push(task);
  res.status(201).json(task);
});
router.patch('/:id', (req, res) => {
  const t = tasks.find(t => t.id === +req.params.id);
  if (!t) return res.status(404).json({ error: 'Not found' });
  Object.assign(t, req.body, { updatedAt: new Date() });
  res.json(t);
});
router.delete('/:id', (req, res) => {
  const idx = tasks.findIndex(t => t.id === +req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  tasks.splice(idx, 1);
  res.json({ message: 'Deleted' });
});
module.exports = router;
