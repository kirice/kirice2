const express = require('express');
const router = express.Router();
const db = require('../db');
// const multer = require('multer');
// const path = require('path');

// 🧠 Настройка хранилища для изображений
// const storage = multer.diskStorage({
//   destination: (req, file, cb) => {
//     cb(null, path.join(__dirname, '../images')); // ← путь к папке images
//   },
//   filename: (req, file, cb) => {
//     const uniqueName = Date.now() + '-' + file.originalname;
//     cb(null, uniqueName);
//   }
// });
// const upload = multer({ storage });

// ✅ ДОБАВЛЕНИЕ компонента
router.post('/',express.json(), async (req, res) => {

  const { type, name, price, description } = req.body;

  if (!type || !name) {
    return res.status(400).json({ error: 'Тип и название обязательны' });
  }

  try {
    const result = await db.query(
      `INSERT INTO components (type, name, price, description)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [type, name, price || null, description || null]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error('Ошибка добавления:', err);
    res.status(500).json({ error: 'Ошибка добавления компонента' });
  }
});

// 🔍 Получение всех компонентов
router.get('/', async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM components');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Ошибка загрузки компонентов' });
  }
});

// 🗑 Удаление
router.delete('/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await db.query('DELETE FROM components WHERE id = $1', [id]);
    res.status(204).send();
  } catch (err) {
    console.error('Ошибка удаления:', err);
    res.status(500).json({ error: 'Ошибка удаления компонента' });
  }
});

module.exports = router;
