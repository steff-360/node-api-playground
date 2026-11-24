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
