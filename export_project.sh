#!/bin/bash

# Имя файла, куда всё сохранится
OUTPUT_FILE="project_export.txt"

# Очищаем старый файл или создаём новый пустой
> "$OUTPUT_FILE"

# Заголовок для структуры
echo "=== ДЕРЕВО ПРОЕКТА ===" >> "$OUTPUT_FILE"

# Рисуем структуру, игнорируя мусор по шаблонам через вертикальную черту
tree -I "__pycache__|*.pyc|.venv|.git|*.log|*.tmp|*.swp|*.DS_Store|*.egg-info" >> "$OUTPUT_FILE"

# Пустые строки для разделения
echo -e "\n\n" >> "$OUTPUT_FILE"

echo "=== СОДЕРЖИМОЕ ФАЙЛОВ ===" >> "$OUTPUT_FILE"

# Ищем только обычные файлы, исключаем мусорные папки и типы файлов
find . -type f \
    -not -path "*/__pycache__/*" \
    -not -name "*.pyc" \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -not -name "*.log" \
    -not -name "*.tmp" \
    -not -name "*.swp" \
    -not -name "*.DS_Store" \
    -not -name "*.egg-info" \
    | sort \
    | while IFS= read -r file; do
        # Рисуем разделитель
        echo "--------------------------------------------------" >> "$OUTPUT_FILE"
        # Пишем путь к файлу
        echo "ФАЙЛ: $file" >> "$OUTPUT_FILE"
        echo "--------------------------------------------------" >> "$OUTPUT_FILE"
        # Выводим содержимое файла в итоговый документ
        cat "$file" >> "$OUTPUT_FILE"
        # Добавляем пустую строку после содержимого
        echo -e "\n" >> "$OUTPUT_FILE"
    done

echo "Готово! Весь проект сохранён в файл: $OUTPUT_FILE"