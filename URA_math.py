import numpy as np
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt  # Добавить эту строку


class PhasedArrayDesigner:
    """
    Класс для проектирования геометрии ФАР (Фазированной Антенной Решетки)
    Аналог MATLAB phased.URA с расширенным функционалом
    """

    def __init__(self, frequency: float = 3e9):
        """
        Инициализация проектировщика ФАР

        Parameters:
        -----------
        frequency : float
            Рабочая частота в Гц (по умолчанию 3 ГГц)
        """
        self.frequency = frequency
        self.c = 3e8  # Скорость света
        self.lambda_ = self.c / self.frequency  # Длина волны

    def calculate_defaults(self) -> Dict:
        """Рассчитать параметры по умолчанию"""
        return {
            'element_spacing': self.lambda_ / 2,  # Шаг по умолчанию
            'element_width': self.lambda_ / 4,  # Ширина элемента
            'element_height': self.lambda_ / 4,  # Высота элемента
        }

    def create_linear_array(self,
                            num_elements: int,
                            spacing: Optional[float] = None,
                            element_size: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Создание линейной ФАР

        Изменение: теперь первый элемент начинается в (0, 0)
        """
        # Параметры по умолчанию
        defaults = self.calculate_defaults()
        if spacing is None:
            spacing = defaults['element_spacing']
        if element_size is None:
            element_size = (defaults['element_width'], defaults['element_height'])

        # Создание позиций элементов вдоль оси X (начинается с 0, 0)
        positions = np.zeros((3, num_elements))
        for i in range(num_elements):
            # Изменение: начинаем с (0, 0) и увеличиваем координату X
            positions[0, i] = i * spacing

        # Расчет границ элементов
        element_bounds = self._calculate_element_bounds(positions, element_size)

        return {
            'type': 'linear',
            'num_elements': num_elements,
            'positions': positions,
            'spacing': spacing,
            'element_size': element_size,
            'element_bounds': element_bounds,
            'frequency': self.frequency,
            'wavelength': self.lambda_
        }

    def create_rectangular_array(self,
                                 rows: int,
                                 cols: int,
                                 row_spacing: Optional[float] = None,
                                 col_spacing: Optional[float] = None,
                                 element_size: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Создание прямоугольной ФАР (аналог phased.URA в MATLAB)

        Изменение: теперь нижний левый элемент начинается в (0, 0)
        """
        # Параметры по умолчанию
        defaults = self.calculate_defaults()
        if row_spacing is None:
            row_spacing = defaults['element_spacing']
        if col_spacing is None:
            col_spacing = defaults['element_spacing']
        if element_size is None:
            element_size = (defaults['element_width'], defaults['element_height'])

        # Создание позиций элементов
        positions = np.zeros((3, rows * cols))

        index = 0
        for i in range(rows):
            for j in range(cols):
                # Изменение: начинаем с (0, 0) в нижнем левом углу
                # i=0, j=0 -> нижний левый элемент
                # Увеличиваем X вправо, Y вверх
                x = j * col_spacing
                y = i * row_spacing  # i=0 -> нижний ряд
                positions[0, index] = x
                positions[1, index] = y
                index += 1

        # Расчет границ элементов
        element_bounds = self._calculate_element_bounds(positions, element_size)

        return {
            'type': 'rectangular',
            'rows': rows,
            'cols': cols,
            'positions': positions,
            'row_spacing': row_spacing,
            'col_spacing': col_spacing,
            'element_size': element_size,
            'element_bounds': element_bounds,
            'frequency': self.frequency,
            'wavelength': self.lambda_,
            'total_elements': rows * cols
        }

    def create_triangular_array(self,
                                rows: int,
                                cols: int,
                                spacing: Optional[float] = None,
                                element_size: Optional[Tuple[float, float]] = None) -> Dict:
        """
        Создание треугольной (гексагональной) ФАР
        Исправленная версия: одинаковое количество элементов в каждой строке

        Изменение: теперь нижний левый элемент начинается в (0, 0)
        """
        # Параметры по умолчанию
        defaults = self.calculate_defaults()
        if spacing is None:
            spacing = defaults['element_spacing']
        if element_size is None:
            element_size = (defaults['element_width'], defaults['element_height'])

        # Расстояние между строками (0.85 от шага по X)
        row_spacing = spacing * 0.85

        # Создание позиций элементов
        positions_list = []

        for i in range(rows):
            # Одинаковое количество элементов в каждой строке
            num_in_row = cols

            # Смещение для нечетных строк (i=0 - четная строка - без смещения)
            x_offset = spacing / 2 if i % 2 == 1 else 0

            for j in range(num_in_row):
                # Изменение: начинаем с (0, 0) в нижнем левом углу
                x = j * spacing + x_offset
                y = i * row_spacing  # i=0 -> нижний ряд
                positions_list.append([x, y, 0])

        positions = np.array(positions_list).T

        # Расчет границ элементов
        element_bounds = self._calculate_element_bounds(positions, element_size)

        return {
            'type': 'triangular',
            'rows': rows,
            'cols': cols,
            'positions': positions,
            'spacing': spacing,
            'row_spacing': row_spacing,  # Добавляем расстояние между строками
            'element_size': element_size,
            'element_bounds': element_bounds,
            'frequency': self.frequency,
            'wavelength': self.lambda_,
            'total_elements': positions.shape[1]
        }

    def _calculate_element_bounds(self, positions: np.ndarray,
                                  element_size: Tuple[float, float]) -> List[np.ndarray]:
        """
        Расчет границ каждого элемента для визуализации

        Изменение: теперь нижний левый угол элемента находится в позиции элемента
        """
        width, height = element_size
        element_bounds = []

        for i in range(positions.shape[1]):
            x, y, z = positions[:, i]

            # Изменение: позиция элемента - это его нижний левый угол
            corners = np.array([
                [x, y, z],  # Нижний левый
                [x + width, y, z],  # Нижний правый
                [x + width, y + height, z],  # Верхний правый
                [x, y + height, z],  # Верхний левый
                [x, y, z]  # Замыкаем прямоугольник
            ])
            element_bounds.append(corners)

        return element_bounds

    def plot_array_geometry(self, array_data: Dict, ax=None, figsize: Tuple[int, int] = (8, 6)):
        """
        Визуализация геометрии ФАР в заданных осях
        """
        if ax is None:
            fig = Figure(figsize=figsize)
            ax = fig.add_subplot(111, projection='3d')
        else:
            ax.clear()
            fig = ax.figure

        positions = array_data['positions']
        element_bounds = array_data['element_bounds']

        # Отображение элементов
        if element_bounds:
            for bounds in element_bounds:
                # Конвертируем метры в миллиметры для отображения
                bounds_mm = bounds * 1000
                ax.plot(bounds_mm[:, 0], bounds_mm[:, 1], bounds_mm[:, 2],
                        'b-', linewidth=1.0, alpha=0.8, zorder=2)

                # Добавляем диагонали для лучшего восприятия формы
                ax.plot([bounds_mm[0, 0], bounds_mm[2, 0]],
                        [bounds_mm[0, 1], bounds_mm[2, 1]],
                        [bounds_mm[0, 2], bounds_mm[2, 2]],
                        'b:', linewidth=0.5, alpha=0.5, zorder=1)
                ax.plot([bounds_mm[1, 0], bounds_mm[3, 0]],
                        [bounds_mm[1, 1], bounds_mm[3, 1]],
                        [bounds_mm[1, 2], bounds_mm[3, 2]],
                        'b:', linewidth=0.5, alpha=0.5, zorder=1)

        # Отображение центров элементов в миллиметрах
        centers_x = (positions[0, :] + array_data['element_size'][0] / 2) * 1000
        centers_y = (positions[1, :] + array_data['element_size'][1] / 2) * 1000
        centers_z = positions[2, :] * 1000

        ax.scatter(centers_x, centers_y, centers_z,
                   c='red', s=30, marker='o', label='Центры элементов', zorder=5)

        # Настройки графика с метками в миллиметрах
        ax.set_xlabel('X (мм)', fontsize=10)
        ax.set_ylabel('Y (мм)', fontsize=10)
        ax.set_zlabel('Z (мм)', fontsize=10)

        # Заголовок с информацией
        title = f"Геометрия {array_data['type']} ФАР\n"
        title += f"Частота: {self.frequency / 1e9:.2f} ГГц, λ = {self.lambda_ * 1000:.1f} мм\n"

        if array_data['type'] == 'linear':
            title += f"Элементов: {array_data['num_elements']}, "
            title += f"Шаг: {array_data['spacing'] / self.lambda_:.2f}λ"
        elif array_data['type'] == 'rectangular':
            title += f"Размер: {array_data['rows']}×{array_data['cols']}, "
            title += f"Всего: {array_data['total_elements']} элементов"
        elif array_data['type'] == 'triangular':
            title += f"Размер: {array_data['rows']}×{array_data['cols']}, "
            title += f"Всего: {array_data['total_elements']} элементов"
            title += f", dY/dX = 0.85"

        ax.set_title(title, fontsize=12, pad=15)

        # Расчет границ для КВАДРАТНОГО отображения
        # Получаем все координаты в миллиметрах
        all_x_mm, all_y_mm = [], []

        if element_bounds:
            for bounds in element_bounds:
                bounds_mm = bounds * 1000
                all_x_mm.extend(bounds_mm[:, 0])
                all_y_mm.extend(bounds_mm[:, 1])

        if all_x_mm and all_y_mm:
            x_min, x_max = min(all_x_mm), max(all_x_mm)
            y_min, y_max = min(all_y_mm), max(all_y_mm)

            # Делаем область квадратной: берем максимальный диапазон
            x_range = x_max - x_min
            y_range = y_max - y_min
            max_range = max(x_range, y_range)

            # Добавляем отступы
            margin = max_range * 0.1

            # Если диапазон по X больше - центрируем по Y
            if x_range > y_range:
                y_center = (y_min + y_max) / 2
                y_min = y_center - max_range / 2
                y_max = y_center + max_range / 2
            # Если диапазон по Y больше - центрируем по X
            else:
                x_center = (x_min + x_max) / 2
                x_min = x_center - max_range / 2
                x_max = x_center + max_range / 2

            ax.set_xlim([x_min - margin, x_max + margin])
            ax.set_ylim([y_min - margin, y_max + margin])
        else:
            # По умолчанию, если нет элементов
            ax.set_xlim([-10, 10])
            ax.set_ylim([-10, 10])

        # Z-ось всегда маленькая
        ax.set_zlim([-5, 5])

        # Настраиваем пропорции осей для квадратного вида
        ax.set_box_aspect([1, 1, 0.1])  # X:Y:Z = 1:1:0.1

        # Устанавливаем сетку
        ax.grid(True, alpha=0.3)

        # Добавляем сетку с шагом, соответствующим масштабу в миллиметрах
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}'))

        # Настраиваем расположение легенды
        ax.legend(fontsize=8, loc='upper right')

        return fig, ax

    # def print_array_info(self, array_data: Dict):
    #     """Вывод информации о решетке"""
    #     print("=" * 60)
    #     print("ИНФОРМАЦИЯ О ФАР")
    #     print("=" * 60)
    #     print(f"Тип решетки: {array_data['type']}")
    #     print(f"Рабочая частота: {self.frequency / 1e9:.2f} ГГц")
    #     print(f"Длина волны: {self.lambda_ * 1000:.2f} мм")
    #
    #     if array_data['type'] == 'linear':
    #         print(f"Количество элементов: {array_data['num_elements']}")
    #         print(f"Шаг между элементами: {array_data['spacing']:.4f} м "
    #               f"({array_data['spacing'] / self.lambda_:.2f}λ)")
    #         spacing_for_ratio = array_data['spacing']
    #
    #     elif array_data['type'] == 'rectangular':
    #         print(f"Размер решетки: {array_data['rows']}×{array_data['cols']}")
    #         print(f"Общее количество элементов: {array_data['total_elements']}")
    #         print(f"Шаг по строкам: {array_data['row_spacing']:.4f} м "
    #               f"({array_data['row_spacing'] / self.lambda_:.2f}λ)")
    #         print(f"Шаг по столбцам: {array_data['col_spacing']:.4f} м "
    #               f"({array_data['col_spacing'] / self.lambda_:.2f}λ)")
    #         spacing_for_ratio = array_data['row_spacing']  # Используем row_spacing для отношения
    #
    #     elif array_data['type'] == 'triangular':
    #         print(f"Строк: {array_data['rows']}, Столбцов: {array_data['cols']}")
    #         print(f"Общее количество элементов: {array_data['total_elements']}")
    #         print(f"Шаг по X: {array_data['spacing']:.4f} м "
    #               f"({array_data['spacing'] / self.lambda_:.2f}λ)")
    #         print(f"Шаг по Y: {array_data['row_spacing']:.4f} м "
    #               f"({array_data['row_spacing'] / self.lambda_:.2f}λ)")
    #         print(f"Отношение шагов (Y/X): {array_data['row_spacing'] / array_data['spacing']:.2f}")
    #         spacing_for_ratio = array_data['spacing']
    #
    #     print(f"Размер элемента: {array_data['element_size'][0] * 100:.1f}×"
    #           f"{array_data['element_size'][1] * 1000:.1f} мм")
    #     print(f"Отношение шаг/размер: {spacing_for_ratio / array_data['element_size'][0]:.2f}")
    #     print("=" * 60)