const express = require('express');
const router  = express.Router();

// Almacenamiento en memoria (reemplazar con DB en produccion)
let notes = [];
let nextId = 1;

// GET /api/notes
router.get('/', (req, res) => {
  const { q } = req.query;
  const result = q
    ? notes.filter(n => n.title.includes(q) || n.content.includes(q))
    : notes;
  res.json({ total: result.length, data: result });
});

// GET /api/notes/:id
router.get('/:id', (req, res) => {
  const note = notes.find(n => n.id === parseInt(req.params.id));
  if (!note) return res.status(404).json({ error: 'Nota no encontrada' });
  res.json(note);
});

// POST /api/notes
router.post('/', (req, res) => {
  const { title, content } = req.body;
  if (!title || !content) {
    return res.status(400).json({ error: 'title y content son requeridos' });
  }
  const note = { id: nextId++, title, content, createdAt: new Date().toISOString() };
  notes.push(note);
  res.status(201).json(note);
});

// PUT /api/notes/:id
router.put('/:id', (req, res) => {
  const idx = notes.findIndex(n => n.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Nota no encontrada' });
  notes[idx] = { ...notes[idx], ...req.body, updatedAt: new Date().toISOString() };
  res.json(notes[idx]);
});

// DELETE /api/notes/:id
router.delete('/:id', (req, res) => {
  const idx = notes.findIndex(n => n.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Nota no encontrada' });
  notes.splice(idx, 1);
  res.json({ message: 'Nota eliminada' });
});

module.exports = router;
