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
