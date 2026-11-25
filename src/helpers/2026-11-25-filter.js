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
