const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// 🔐 Хэширование пароля
const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(10);
  return await bcrypt.hash(password, salt);
};

// 🔍 Сравнение пароля с хэшем
const comparePassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

// ✅ Проверка наличия токена
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.split(' ')[1];

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
      if (err) {
        return res.status(403).json({ error: 'Неверный токен' });
      }

      req.user = user;
      next();
    });
  } else {
    res.status(401).json({ error: 'Токен не предоставлен' });
  }
};

// 🔐 Проверка роли пользователя
const authorizeRole = (requiredRole) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Не авторизован' });
    }

    if (req.user.role !== requiredRole) {
      return res.status(403).json({ error: 'Недостаточно прав' });
    }

    next();
  };
};

module.exports = {
  hashPassword,
  comparePassword,
  authenticateJWT,
  authorizeRole
};
