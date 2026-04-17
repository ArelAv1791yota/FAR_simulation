#!/usr/bin/env python3
"""
Точка входа в приложение проектировщика ФАР
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем приложение
from URA_design import main

if __name__ == "__main__":
    main()