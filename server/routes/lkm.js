const express = require('express');
const router = express.Router();

router.post('/calculate/lkm', (req, res) => {
  const { lacName, stepWidth, stepLength, numSteps, layers, consumption, price } = req.body;

  // Проверка данных
  if (!stepWidth || !stepLength || !numSteps || !consumption || !price) {
    return res.status(400).json({ error: 'Все поля обязательны' });
  }

  // Формулы из диплома
  const areaPerStep = stepWidth * stepLength;
  const totalArea = areaPerStep * numSteps;
  const totalVolume = totalArea * consumption * layers;
  const totalPrice = totalVolume * price;

  // Ответ клиенту
  res.json({
    lacName,
    totalArea: totalArea.toFixed(2),
    totalVolume: totalVolume.toFixed(2),
    totalPrice: totalPrice.toFixed(2)
  });
});

module.exports = router;