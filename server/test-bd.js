const db = require('./db');

db.query('SELECT NOW()', [])
  .then(res => console.log('Подключение к БД успешно:', res.rows[0]))
  .catch(err => console.error('Ошибка подключения:', err));