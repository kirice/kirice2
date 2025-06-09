const express = require('express');
const router = express.Router();
const db = require('../db');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// Регистрация
router.post('/register', async (req, res) => {
  try {
    const { username, password, firstName, lastName, phone } = req.body;

    console.log('Полученные данные:', req.body); // Логируем данные

    if (!username || !password) {
      return res.status(400).json({ error: 'Email и пароль обязательны' });
    }

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(username)) {
      return res.status(400).json({ error: 'Некорректный email' });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: 'Пароль должен быть не менее 6 символов' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await db.query(
      `INSERT INTO users 
       (username, password_hash, first_name, last_name, phone) 
       VALUES ($1, $2, $3, $4, $5) 
       RETURNING id, username, first_name, last_name, phone`,
      [username, hashedPassword, firstName || null, lastName || null, phone || null]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Ошибка регистрации:', err);
    res.status(500).json({ error: 'Ошибка регистрации', details: err.message });
  }
});

// Вход
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await db.query('SELECT * FROM users WHERE username = $1', [username]);
    
    if (user.rows.length === 0) {
      return res.status(401).json({ error: 'Неверные данные' });
    }
    
    const isValid = await bcrypt.compare(password, user.rows[0].password_hash);
    if (!isValid) {
      return res.status(401).json({ error: 'Неверные данные' });
    }
    
    const token = jwt.sign(
      { userId: user.rows[0].id, role: user.rows[0].role },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
    
    res.json({ token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Ошибка входа' });
  }
});

module.exports = router;