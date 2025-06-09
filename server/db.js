require('dotenv').config();
const { Pool } = require('pg');

console.log('DB_PASSWORD type:', typeof process.env.DB_PASSWORD);
console.log('DB_PASSWORD value:', process.env.DB_PASSWORD);

const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'stair_calculator',
  password: 'Kirillser02',
  port: 5432,
});

// Проверка подключения
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('Ошибка подключения к БД:', err);
  } else {
    console.log('Успешное подключение к БД. Текущее время:', res.rows[0].now);
  }
});

module.exports = {
  query: (text, params) => pool.query(text, params),
};