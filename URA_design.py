import sys
import numpy as np

# PyQt5 импорты
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Matplotlib импорты
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Импорт класса проектировщика
from URA_math import PhasedArrayDesigner


class MplCanvas(FigureCanvas):
    """Холст для matplotlib графики"""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)


class FARDesignerUI(QMainWindow):
    """Основное окно приложения"""

    def __init__(self):
        super().__init__()
        self.designer = PhasedArrayDesigner()
        self.current_array = None
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Визуализатор геометрии ФАР")
        self.setGeometry(100, 100, 1400, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QHBoxLayout(central_widget)

        # Левая панель - параметры
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)

        # Правая панель - график
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        right_layout = QVBoxLayout(right_panel)

        # Добавляем панели в основной layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)

        # ===== ЛЕВАЯ ПАНЕЛЬ - ПАРАМЕТРЫ =====

        # Заголовок
        title_label = QLabel("Параметры ФАР")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_layout.addWidget(title_label)

        left_layout.addSpacing(10)

        # Тип решетки
        type_group = QGroupBox("Тип решетки")
        type_layout = QVBoxLayout()

        self.array_type_combo = QComboBox()
        self.array_type_combo.addItems(["Линейная", "Прямоугольная", "Треугольная"])
        self.array_type_combo.currentIndexChanged.connect(self.on_array_type_changed)
        type_layout.addWidget(QLabel("Выберите тип решетки:"))
        type_layout.addWidget(self.array_type_combo)

        # Информация о типах решеток
        info_label = QLabel(
            "Треугольная: равное количество элементов в строках,\nрасстояние между строками = 0.85 × шаг по X")
        info_label.setStyleSheet("font-size: 10px; color: #666;")
        type_layout.addWidget(info_label)

        type_group.setLayout(type_layout)
        left_layout.addWidget(type_group)

        left_layout.addSpacing(10)

        # Параметры решетки
        params_group = QGroupBox("Параметры решетки")
        params_layout = QGridLayout()

        # Частота (всегда видна)
        params_layout.addWidget(QLabel("Частота (ГГц):"), 0, 0)
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.1, 100)
        self.freq_spin.setValue(3.0)
        self.freq_spin.setDecimals(2)
        self.freq_spin.setSuffix(" ГГц")
        self.freq_spin.valueChanged.connect(self.on_frequency_changed)
        params_layout.addWidget(self.freq_spin, 0, 1)

        # Параметры для линейной решетки - Количество элементов
        self.linear_elements_label = QLabel("Количество элементов:")
        params_layout.addWidget(self.linear_elements_label, 1, 0)
        self.linear_elements_spin = QSpinBox()
        self.linear_elements_spin.setRange(1, 100)
        self.linear_elements_spin.setValue(8)
        params_layout.addWidget(self.linear_elements_spin, 1, 1)

        # Параметры для прямоугольной и треугольной решеток - Количество строк
        self.rows_label = QLabel("Количество строк (a):")
        params_layout.addWidget(self.rows_label, 2, 0)
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 101)
        self.rows_spin.setValue(6)
        params_layout.addWidget(self.rows_spin, 2, 1)

        # Параметры для прямоугольной и треугольной решеток - Количество столбцов
        self.cols_label = QLabel("Количество столбцов (b):")
        params_layout.addWidget(self.cols_label, 3, 0)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 101)
        self.cols_spin.setValue(6)
        params_layout.addWidget(self.cols_spin, 3, 1)

        params_group.setLayout(params_layout)
        left_layout.addWidget(params_group)

        left_layout.addSpacing(10)

        # Параметры элементов
        element_group = QGroupBox("Параметры элементов")
        element_layout = QGridLayout()

        # Шаг между элементами (по X)
        element_layout.addWidget(QLabel("Шаг по X (отн. λ):"), 0, 0)
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.1, 5.0)
        self.spacing_spin.setValue(0.5)
        self.spacing_spin.setDecimals(2)
        self.spacing_spin.setSuffix(" λ")
        element_layout.addWidget(self.spacing_spin, 0, 1)

        # Шаг по Y
        element_layout.addWidget(QLabel("Шаг по Y (отн. λ):"), 1, 0)
        self.row_spacing_spin = QDoubleSpinBox()
        self.row_spacing_spin.setRange(0.1, 5.0)
        self.row_spacing_spin.setValue(0.425)  # 0.5 * 0.85
        self.row_spacing_spin.setDecimals(2)
        self.row_spacing_spin.setSuffix(" λ")
        element_layout.addWidget(self.row_spacing_spin, 1, 1)

        # Размер элемента
        element_layout.addWidget(QLabel("Ширина элемента (отн. λ):"), 2, 0)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.01, 2.0)
        self.width_spin.setValue(0.25)
        self.width_spin.setDecimals(2)
        self.width_spin.setSuffix(" λ")
        element_layout.addWidget(self.width_spin, 2, 1)

        element_layout.addWidget(QLabel("Высота элемента (отн. λ):"), 3, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.01, 2.0)
        self.height_spin.setValue(0.25)
        self.height_spin.setDecimals(2)
        self.height_spin.setSuffix(" λ")
        element_layout.addWidget(self.height_spin, 3, 1)

        element_group.setLayout(element_layout)
        left_layout.addWidget(element_group)

        left_layout.addSpacing(10)

        # Кнопки управления
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Сгенерировать ФАР")
        self.generate_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        self.generate_btn.clicked.connect(self.generate_array)
        button_layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("Сохранить график")
        self.save_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.save_btn.clicked.connect(self.save_plot)
        button_layout.addWidget(self.save_btn)

        left_layout.addLayout(button_layout)

        left_layout.addSpacing(10)

        # Информационная панель
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        self.info_text.setStyleSheet("font-family: monospace;")
        info_layout.addWidget(self.info_text)

        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)

        left_layout.addStretch()

        # ===== ПРАВАЯ ПАНЕЛЬ - ГРАФИК =====

        # Создаем холст matplotlib
        self.canvas = MplCanvas(self, width=10, height=8, dpi=100)

        # Создаем панель инструментов для графика
        self.toolbar = NavigationToolbar(self.canvas, self)

        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)

        # Инициализируем видимость элементов в зависимости от типа решетки
        self.update_ui_for_array_type()

        # Автоматически генерируем первую решетку
        QTimer.singleShot(100, self.generate_array)

        # Инициализируем видимость элементов в зависимости от типа решетки
        self.update_ui_for_array_type()

    def update_ui_for_array_type(self):
        """Обновить UI в зависимости от выбранного типа решетки"""
        array_type = self.array_type_combo.currentText()

        # Скрываем/показываем соответствующие элементы
        if array_type == "Линейная":
            # Показываем только количество элементов
            self.linear_elements_label.setVisible(True)
            self.linear_elements_spin.setVisible(True)

            # Скрываем строки и столбцы
            self.rows_label.setVisible(False)
            self.rows_spin.setVisible(False)
            self.cols_label.setVisible(False)
            self.cols_spin.setVisible(False)

            # Для линейной решетки шаг по Y = шагу по X
            self.row_spacing_spin.setEnabled(False)
            self.row_spacing_spin.setValue(self.spacing_spin.value())

        elif array_type == "Прямоугольная":
            # Скрываем количество элементов
            self.linear_elements_label.setVisible(False)
            self.linear_elements_spin.setVisible(False)

            # Показываем строки и столбцы
            self.rows_label.setVisible(True)
            self.rows_spin.setVisible(True)
            self.cols_label.setVisible(True)
            self.cols_spin.setVisible(True)

            # Для прямоугольной решетки шаг по Y можно задавать вручную
            self.row_spacing_spin.setEnabled(True)

        elif array_type == "Треугольная":
            # Скрываем количество элементов
            self.linear_elements_label.setVisible(False)
            self.linear_elements_spin.setVisible(False)

            # Показываем строки и столбцы
            self.rows_label.setVisible(True)
            self.rows_spin.setVisible(True)
            self.cols_label.setVisible(True)
            self.cols_spin.setVisible(True)

            # Для треугольной решетки шаг по Y рассчитывается автоматически
            self.row_spacing_spin.setEnabled(False)
            self.row_spacing_spin.setValue(self.spacing_spin.value() * 0.85)

    def on_array_type_changed(self):
        """Обработчик изменения типа решетки"""
        self.update_ui_for_array_type()

    def on_frequency_changed(self):
        """Обработчик изменения частоты"""
        freq_ghz = self.freq_spin.value()
        self.designer = PhasedArrayDesigner(frequency=freq_ghz * 1e9)

        # Обновляем шаг по Y для треугольной решетки
        if self.array_type_combo.currentText() == "Треугольная":
            self.row_spacing_spin.setValue(self.spacing_spin.value() * 0.85)

    def generate_array(self):
        """Генерация ФАР по заданным параметрам"""
        try:
            # Получаем параметры
            array_type = self.array_type_combo.currentText()
            freq_ghz = self.freq_spin.value()
            spacing_lambda = self.spacing_spin.value()
            row_spacing_lambda = self.row_spacing_spin.value()
            width_lambda = self.width_spin.value()
            height_lambda = self.height_spin.value()

            # Обновляем дизайнер с новой частотой
            self.designer = PhasedArrayDesigner(frequency=freq_ghz * 1e9)

            # Конвертируем относительные значения в абсолютные (метры)
            spacing = spacing_lambda * self.designer.lambda_
            row_spacing = row_spacing_lambda * self.designer.lambda_
            element_size = (width_lambda * self.designer.lambda_,
                            height_lambda * self.designer.lambda_)

            # Создаем решетку в зависимости от типа
            if array_type == "Линейная":
                num_elements = self.linear_elements_spin.value()
                self.current_array = self.designer.create_linear_array(
                    num_elements=num_elements,
                    spacing=spacing,
                    element_size=element_size
                )
            elif array_type == "Прямоугольная":
                rows = self.rows_spin.value()
                cols = self.cols_spin.value()
                self.current_array = self.designer.create_rectangular_array(
                    rows=rows,
                    cols=cols,
                    row_spacing=row_spacing,
                    col_spacing=spacing,
                    element_size=element_size
                )
            elif array_type == "Треугольная":
                rows = self.rows_spin.value()
                cols = self.cols_spin.value()
                # Для треугольной решетки используем row_spacing = spacing * 0.85
                row_spacing = spacing * 0.85
                self.row_spacing_spin.setValue(spacing_lambda * 0.85)
                self.current_array = self.designer.create_triangular_array(
                    rows=rows,
                    cols=cols,
                    spacing=spacing,
                    element_size=element_size
                )

            # Отображаем график
            self.designer.plot_array_geometry(self.current_array, self.canvas.ax)
            self.canvas.draw()

            # Обновляем информационную панель
            self.update_info_panel()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def update_info_panel(self):
        """Обновление информационной панели"""
        if self.current_array is None:
            return

        info_text = ""
        info_text += f"Тип решетки: {self.current_array['type']}\n"
        info_text += f"Частота: {self.designer.frequency / 1e9:.2f} ГГц\n"
        info_text += f"Длина волны: {self.designer.lambda_ * 1000:.1f} мм\n"

        if self.current_array['type'] == 'linear':
            info_text += f"Количество элементов: {self.current_array['num_elements']}\n"
            info_text += f"Шаг между элементами: {self.current_array['spacing']*1000:.1f} мм "
            info_text += f"({self.current_array['spacing'] / self.designer.lambda_:.2f}λ)\n"
        elif self.current_array['type'] == 'rectangular':
            info_text += f"Размер решетки: {self.current_array['rows']}×{self.current_array['cols']}\n"
            info_text += f"Общее количество элементов: {self.current_array['total_elements']}\n"
            info_text += f"Шаг по строкам: {self.current_array['row_spacing']*1000:.1f} мм "
            info_text += f"({self.current_array['row_spacing'] / self.designer.lambda_:.2f}λ)\n"
            info_text += f"Шаг по столбцам: {self.current_array['col_spacing']*1000:.1f} мм "
            info_text += f"({self.current_array['col_spacing'] / self.designer.lambda_:.2f}λ)\n"
        elif self.current_array['type'] == 'triangular':
            info_text += f"Размер решетки: {self.current_array['rows']}×{self.current_array['cols']}\n"
            info_text += f"Общее количество элементов: {self.current_array['total_elements']}\n"
            info_text += f"Шаг по X: {self.current_array['spacing']*1000:.1f} мм "
            info_text += f"({self.current_array['spacing'] / self.designer.lambda_:.2f}λ)\n"
            info_text += f"Шаг по Y: {self.current_array['row_spacing']*1000:.1f} мм "
            info_text += f"({self.current_array['row_spacing'] / self.designer.lambda_:.2f}λ)\n"
            info_text += f"Отношение шагов (Y/X): {self.current_array['row_spacing'] / self.current_array['spacing']:.2f}\n"

        info_text += f"Размер элемента: {self.current_array['element_size'][0] * 1000:.1f}×"
        info_text += f"{self.current_array['element_size'][1] * 1000:.1f} мм\n"
        info_text += f"Отношение шаг/размер по X: "
        if self.current_array['type'] == 'linear':
            ratio = self.current_array['spacing'] / self.current_array['element_size'][0]
        elif self.current_array['type'] == 'rectangular':
            ratio = self.current_array['col_spacing'] / self.current_array['element_size'][0]
        else:
            ratio = self.current_array['spacing'] / self.current_array['element_size'][0]
        info_text += f"{ratio:.2f}\n"

        self.info_text.setPlainText(info_text)

    def save_plot(self):
        """Сохранение графика в файл"""
        if self.current_array is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала сгенерируйте ФАР!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "", "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)"
        )

        if file_path:
            try:
                # Создаем отдельную фигуру для сохранения
                fig, ax = self.designer.plot_array_geometry(self.current_array)
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                QMessageBox.information(self, "Успех", f"График сохранен в:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Устанавливаем стиль
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # Устанавливаем стиль для групп
    app.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            border-radius: 4px;
            padding: 5px;
        }
    """)

    window = FARDesignerUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()