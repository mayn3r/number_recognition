# Number recognition
Система для автоматического распознавания автомобильных номеров.

## Требования
- Python >= 3.10
- uv
- Tesseract OCR

## Установка
### 1. Клонирование удаленного рапозитория на локальный ПК
```bash
git clone https://github.com/mayn3r/number_recognition.git
```

### 2. [Установка Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### 3. Установка всех зависимостей (uv)
```bash
uv venv
uv pip install .
```

### 4. Запуск программы
```bash
uv run python -m src.parser
```

## Примчания

1. После установки Tesseract OCR, необходимо в `parser.py` указать путь на `tesseract.exe`
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```
<br>

2. Изображение хранятся в `src/images`, обработанные изображения в `src/images/processed`