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
