# build_spec.py
import PyInstaller.__main__
import os
import sys

# Пути к вашим файлам
current_dir = os.path.dirname(os.path.abspath(__file__))
main_script = os.path.join(current_dir, "URA_design.py")
icon_path = os.path.join(current_dir, "icon.ico")  # опционально: создайте иконку

# Формируем строку для добавления данных
# Windows использует ';', Linux/Mac использует ':'
if sys.platform == 'win32':
    separator = ';'
else:
    separator = ':'

# Параметры сборки
args = [
    main_script,                      # Основной скрипт
    '--name=Визуализатор геометрии ФАР',           # Имя приложения (без пробелов)
    '--windowed',                    # Без консоли (GUI приложение)
    '--onefile',                     # Один исполняемый файл
    '--clean',                       # Очистить кэш сборки
    '--noconfirm',                   # Не спрашивать подтверждения
    f'--add-data={current_dir}{separator}.',  # Добавить все файлы из текущей директории
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=matplotlib.backends.backend_qt5agg',
    '--hidden-import=matplotlib.backends.backend_qt5',
    '--hidden-import=matplotlib.figure',
    '--hidden-import=mpl_toolkits.mplot3d',
    '--hidden-import=mpl_toolkits.mplot3d.axes3d',
    '--hidden-import=mpl_toolkits',
    '--hidden-import=typing',
]

# Альтернативный вариант - явно указать все необходимые файлы
# args = [
#     main_script,
#     '--name=FAR_Designer',
#     '--windowed',
#     '--onefile',
#     '--clean',
#     '--noconfirm',
#     f'--add-data=URA_math.py{separator}.',
#     f'--add-data=main.py{separator}.',
#     # Добавляем необходимые скрытые импорты
#     '--hidden-import=PyQt5.sip',
#     '--hidden-import=matplotlib.backends.backend_qt5agg',
#     '--hidden-import=matplotlib.backends.backend_qt5',
#     '--hidden-import=matplotlib.backends.backend_agg',
#     '--hidden-import=matplotlib.figure',
#     '--hidden-import=mpl_toolkits.mplot3d',
#     '--hidden-import=mpl_toolkits',
# ]

# Добавить иконку, если она существует
if os.path.exists(icon_path):
    args.append(f'--icon={icon_path}')

# Оптимизация для Windows
if sys.platform == 'win32':
    args.append('--upx-dir=upx')  # Если установлен UPX для сжатия

print("Параметры сборки:")
for arg in args:
    print(f"  {arg}")

print(f"\nСборка из директории: {current_dir}")
print(f"Основной скрипт: {main_script}")

# Запустить сборку
PyInstaller.__main__.run(args)