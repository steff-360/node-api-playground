import datetime, os, sys

colombia_tz = datetime.timezone(datetime.timedelta(hours=-5))
now_col = datetime.datetime.now(colombia_tz)
today = now_col.date()
date_str = today.isoformat()
idx = (now_col.timetuple().tm_yday - 1) % 15

challenges = [
    ("src/routes", "tasks.js", """\
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
"""),
    ("src/middleware", "auth.js", """\
// Middleware de autenticacion basico con Bearer token
const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET || 'dev-secret';

function auth(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token requerido' });
  }
  const token = header.split(' ')[1];
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    res.status(401).json({ error: 'Token invalido o expirado' });
  }
}

function generateToken(payload, expiresIn = '1d') {
  return jwt.sign(payload, SECRET, { expiresIn });
}

module.exports = { auth, generateToken };
"""),
    ("src/middleware", "rate-limiter.js", """\
// Rate limiter en memoria: max N requests por ventana de tiempo
function rateLimiter({ max = 100, windowMs = 60_000 } = {}) {
  const store = new Map();
  return (req, res, next) => {
    const key = req.ip;
    const now = Date.now();
    const entry = store.get(key) || { count: 0, start: now };
    if (now - entry.start > windowMs) {
      entry.count = 0; entry.start = now;
    }
    entry.count++;
    store.set(key, entry);
    res.setHeader('X-RateLimit-Limit', max);
    res.setHeader('X-RateLimit-Remaining', Math.max(0, max - entry.count));
    if (entry.count > max) {
      return res.status(429).json({ error: 'Too many requests' });
    }
    next();
  };
}
module.exports = rateLimiter;
"""),
    ("src/helpers", "pagination.js", """\
// Paginacion estandar para cualquier coleccion
function paginate(items, page = 1, limit = 10) {
  const total = items.length;
  const pages = Math.ceil(total / limit);
  const offset = (page - 1) * limit;
  return {
    data: items.slice(offset, offset + limit),
    meta: { total, page, limit, pages, hasNext: page < pages, hasPrev: page > 1 },
  };
}

function paginateQuery(query, page, limit) {
  const offset = (page - 1) * limit;
  return { ...query, limit, offset };
}

module.exports = { paginate, paginateQuery };
"""),
    ("src/helpers", "response.js", """\
// Wrapper estandar de respuestas HTTP
const ok     = (res, data, msg = 'OK', code = 200) =>
  res.status(code).json({ success: true,  message: msg, data });

const created = (res, data, msg = 'Created') =>
  res.status(201).json({ success: true,  message: msg, data });

const error  = (res, msg = 'Error', code = 500, errors = null) =>
  res.status(code).json({ success: false, message: msg, ...(errors && { errors }) });

const notFound = (res, msg = 'Not found')  => error(res, msg, 404);
const badReq   = (res, msg, errors)        => error(res, msg, 400, errors);
const unauth   = (res, msg = 'Unauthorized') => error(res, msg, 401);

module.exports = { ok, created, error, notFound, badReq, unauth };
"""),
    ("src/middleware", "error-handler.js", """\
// Manejador global de errores para Express
class AppError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
  }
}

function errorHandler(err, req, res, next) {
  const code = err.statusCode || 500;
  const msg  = err.isOperational ? err.message : 'Error interno del servidor';
  if (process.env.NODE_ENV !== 'production') {
    console.error('[ERROR]', err.stack);
  }
  res.status(code).json({ success: false, error: msg });
}

function notFoundHandler(req, res) {
  res.status(404).json({ success: false, error: `Ruta ${req.originalUrl} no encontrada` });
}

module.exports = { AppError, errorHandler, notFoundHandler };
"""),
    ("src/middleware", "logger.js", """\
// Logger de requests HTTP con duracion y codigo de respuesta
function requestLogger(req, res, next) {
  const start  = Date.now();
  const { method, originalUrl, ip } = req;
  res.on('finish', () => {
    const duration = Date.now() - start;
    const { statusCode } = res;
    const color = statusCode >= 500 ? '\\x1b[31m' : statusCode >= 400 ? '\\x1b[33m' : '\\x1b[32m';
    const reset = '\\x1b[0m';
    const ts    = new Date().toISOString();
    console.log(`${ts} ${color}${statusCode}${reset} ${method} ${originalUrl} - ${duration}ms [${ip}]`);
  });
  next();
}
module.exports = requestLogger;
"""),
    ("src/helpers", "cache.js", """\
// Cache en memoria con TTL (time-to-live) configurable
class MemoryCache {
  constructor(defaultTtl = 300_000) {
    this.store = new Map();
    this.defaultTtl = defaultTtl;
  }
  set(key, value, ttl = this.defaultTtl) {
    const expiresAt = Date.now() + ttl;
    this.store.set(key, { value, expiresAt });
  }
  get(key) {
    const entry = this.store.get(key);
    if (!entry) return null;
    if (Date.now() > entry.expiresAt) { this.store.delete(key); return null; }
    return entry.value;
  }
  has(key)    { return this.get(key) !== null; }
  delete(key) { this.store.delete(key); }
  clear()     { this.store.clear(); }
  size()      { return this.store.size; }
}
module.exports = new MemoryCache();
"""),
    ("src/helpers", "token.js", """\
// Generador de tokens seguros para reset, verificacion, etc.
const crypto = require('crypto');

function generateToken(length = 32) {
  return crypto.randomBytes(length).toString('hex');
}

function generateNumericCode(digits = 6) {
  const max = Math.pow(10, digits);
  return String(crypto.randomInt(max)).padStart(digits, '0');
}

function hashToken(token) {
  return crypto.createHash('sha256').update(token).digest('hex');
}

module.exports = { generateToken, generateNumericCode, hashToken };
"""),
    ("src/helpers", "health.js", """\
// Endpoint de health check con info del sistema
const os = require('os');

function healthHandler(req, res) {
  const uptime = process.uptime();
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: `${Math.floor(uptime / 60)}m ${Math.floor(uptime % 60)}s`,
    memory: {
      used: `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`,
      total: `${Math.round(os.totalmem() / 1024 / 1024)}MB`,
    },
    node: process.version,
    env: process.env.NODE_ENV || 'development',
  });
}
module.exports = healthHandler;
"""),
    ("src/helpers", "query-builder.js", """\
// Constructor de queries SQL dinamicas con pg (PostgreSQL)
class QueryBuilder {
  constructor(table) { this.table = table; this.conditions = []; this.params = []; this.counter = 1; }

  where(field, value) {
    this.conditions.push(`${field} = $${this.counter++}`);
    this.params.push(value);
    return this;
  }

  whereIn(field, values) {
    const placeholders = values.map(() => `$${this.counter++}`).join(', ');
    this.conditions.push(`${field} IN (${placeholders})`);
    this.params.push(...values);
    return this;
  }

  build(fields = '*') {
    const where = this.conditions.length ? `WHERE ${this.conditions.join(' AND ')}` : '';
    return { text: `SELECT ${fields} FROM ${this.table} ${where}`.trim(), values: this.params };
  }
}
module.exports = QueryBuilder;
"""),
    ("src/helpers", "search.js", """\
// Busqueda y filtrado de colecciones en memoria
function search(items, query, fields) {
  if (!query) return items;
  const q = query.toLowerCase();
  return items.filter(item => fields.some(f => String(item[f] ?? '').toLowerCase().includes(q)));
}

function filterBy(items, filters) {
  return items.filter(item =>
    Object.entries(filters).every(([k, v]) => v === undefined || item[k] === v)
  );
}

function sortBy(items, field, direction = 'asc') {
  return [...items].sort((a, b) => {
    if (a[field] < b[field]) return direction === 'asc' ? -1 : 1;
    if (a[field] > b[field]) return direction === 'asc' ?  1 : -1;
    return 0;
  });
}

module.exports = { search, filterBy, sortBy };
"""),
    ("src/helpers", "sort.js", """\
// Helpers de ordenamiento multi-campo para arrays de objetos
function sortMulti(items, ...criteria) {
  return [...items].sort((a, b) => {
    for (const { field, dir = 'asc' } of criteria) {
      const valA = a[field], valB = b[field];
      if (valA < valB) return dir === 'asc' ? -1 :  1;
      if (valA > valB) return dir === 'asc' ?  1 : -1;
    }
    return 0;
  });
}

const data = [
  { name: 'Ana',  age: 25, dept: 'Dev' },
  { name: 'Luis', age: 30, dept: 'QA'  },
  { name: 'Sara', age: 25, dept: 'Dev' },
];
console.log(sortMulti(data, { field: 'age' }, { field: 'name' }));
"""),
    ("src/helpers", "filter.js", """\
// Filtrado avanzado con operadores de comparacion
const OPERATORS = {
  eq:  (a, b) => a === b,
  ne:  (a, b) => a !== b,
  gt:  (a, b) => a > b,
  gte: (a, b) => a >= b,
  lt:  (a, b) => a < b,
  lte: (a, b) => a <= b,
  in:  (a, b) => b.includes(a),
  nin: (a, b) => !b.includes(a),
  contains: (a, b) => String(a).toLowerCase().includes(String(b).toLowerCase()),
};

function advancedFilter(items, filters) {
  return items.filter(item =>
    filters.every(({ field, op = 'eq', value }) => {
      const fn = OPERATORS[op];
      return fn ? fn(item[field], value) : true;
    })
  );
}

const products = [{ name: 'Laptop', price: 1200 }, { name: 'Mouse', price: 25 }];
console.log(advancedFilter(products, [{ field: 'price', op: 'gt', value: 100 }]));
"""),
    ("src/routes", "users.js", """\
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
"""),
]

folder, name, content = challenges[idx]
os.makedirs(folder, exist_ok=True)
base_target = os.path.join(folder, f"{date_str}-{name}")
target = base_target
v = 2
while os.path.exists(target):
    target = os.path.join(folder, f"{date_str}-v{v}-{name}")
    v += 1
with open(target, "w") as f:
    f.write(content)
print(f"Created: {target}")
