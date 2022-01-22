#################################################################
import random
import time
import math

COUNT_COLUMNS = 6
COUNT_ROWS = 6
SYMBOL_VOID_CELL = 'O'
SYMBOL_MISMATCH = 'T'
SYMBOL_HIT = 'X'
SYMBOL_PLACE_SHIP = '.'
SYMBOL_CELL_DELIMITER = '|'
MIN_SPACE_BETWEEN_SHIPS = 1
SHIPS_LIST = [3, 2, 2, 1, 1, 1, 1]
AUTOMATIC_PLACEMENT = 'auto'
CLEAR_USER_SHIPS = 'clear'
EXIT_WORD = 'exit'

flag_exit = False

game_table_gamer = None
game_table_computer = None


def main():
    global game_table_computer
    global game_table_gamer
    global flag_exit

    # приветствие
    hello()

    flag_exit = False
    if game_init():

        if not flag_exit:
            # Здесь начинается сама игра
            # Игра идет до тех пор, пока один из игроков не проиграет, либо не будет подан запрос на окончание игры

            print("Игра начинается!")

            lst = []
            step_counter = 1
            while not (game_table_gamer.is_losing() or game_table_computer.is_losing() or flag_exit):
                print('=' * 60)

                if step_counter % 2:  # ход игрока
                    print("Ваш ход!\nПосмотрите на доску компьютера и сделайте свой ход:")
                    game_table_computer.show()

                    while True:
                        str_ = input(
                            "Введите через пробел координаты ячейки, куда хотите сделать ход (горизонталь и вертикаль). Для выхода введите %s : " % (
                                EXIT_WORD))

                        try:
                            if str_.upper() == EXIT_WORD.upper():
                                flag_exit = True
                                break
                            else:
                                lst = list(map(int, str.split(str_)))

                                if len(lst) != 2:
                                    raise Exception
                        except Exception:
                            print('Ошибка ввода координат. Попробуйте еще раз...')
                            print("")
                        else:
                            ret_val = game_table_computer.make_move(lst[0] - 1, lst[1] - 1)
                            if ret_val == 1:  # если успех
                                print("Доска компьютера с учетом Вашего хода:")
                                game_table_computer.show()
                                time.sleep(3)
                                break
                            elif ret_val == 0:
                                print("Ход в ячейку с этими координатами уже был сделан. Введите координаты другой ячейки...")
                            elif ret_val == -1:
                                print('Координаты ячейки выходят за пределы игровой доски. Введите корректные координаты...')
                            print("")

                else:  # ход компьютера
                    print("Ход компьютера...")
                    time.sleep(1)

                    game_table_gamer.make_random_move()

                    print("Ход сделан...")
                    print("Состояние доски игрока:")
                    game_table_gamer.show(True)

                    time.sleep(3)

                step_counter += 1

        result_game()
    else:
        print("Произошла ошибка инициализации игры... Попробуйте перезапустить игру...")


def hello():
    rules = """Напомним некоторые правила игры Морской Бой.
 Игрок играет с компьютером. Игровые доски игроков заполняются кораблями. 
 Задача игры - потопить все корабли противника первым.
 Ходить в одну и ту же клетку дважды запрещено.\n"""

    print("+++ Добро пожаловать в игру Морской Бой! +++\n")
    print(rules)
    print("Условные обозначения:\n"
          " пустая клетка -  %s\n"
          " корабль - %s\n"
          " подбитый корабль - %s\n"
          " промах - %s\n"
          % (SYMBOL_VOID_CELL, SYMBOL_PLACE_SHIP, SYMBOL_HIT, SYMBOL_MISMATCH))

    print("Ниже приведен список кораблей, участвующих в игре:")
    for i in SHIPS_LIST:
        print(" %d-палубный" % i)

    print('-+' * 30)


# Функция инициализации игры (создание объектов игровых досок, объектов кораблей, их заполнение)
# возвращает True в случае успешной инициализации, False - в случае ошибки
def game_init():
    global game_table_gamer
    global game_table_computer
    global AUTOMATIC_PLACEMENT

    global flag_exit
    fl_error = False

    # создание объекта для хранения кораблей игрока
    ships_gamer = Ships(COUNT_ROWS, COUNT_COLUMNS)

    # создание объекта для хранения кораблей компьютера
    ships_computer = Ships(COUNT_ROWS, COUNT_COLUMNS, MIN_SPACE_BETWEEN_SHIPS)

    # создание объекта игровой доски для игрока
    game_table_gamer = GameTable(row_count=COUNT_ROWS, columns_count=COUNT_COLUMNS, symbol_void_cell_=SYMBOL_VOID_CELL, symbol_cell_delimiter_=SYMBOL_CELL_DELIMITER,
                                 symbol_hit_=SYMBOL_HIT, symbol_mismatch=SYMBOL_MISMATCH, symbol_place_ship_=SYMBOL_PLACE_SHIP)

    # создание игровой доски для компьютера, добавление кораблей компьютера на доску
    game_table_computer = GameTable(row_count=COUNT_ROWS, columns_count=COUNT_COLUMNS, symbol_void_cell_=SYMBOL_VOID_CELL, symbol_cell_delimiter_=SYMBOL_CELL_DELIMITER,
                                    symbol_hit_=SYMBOL_HIT, symbol_mismatch=SYMBOL_MISMATCH, symbol_place_ship_=SYMBOL_PLACE_SHIP)

    print("Перед началом игры Вам необходимо расположить свои корабли на игровой доске.\n"
          "На текущий момент Ваша доска пуста:")
    game_table_gamer.show(True)
    print("Необходимо добавить корабли на Вашу игровую доску!\n"
          "Каждый корабль может располагаться либо по горизонтали, либо по вертикали. Диагональное расположение корабля недопустимо.\n"
          "Приступим к заполнению!\n")

    coord = []  # список введенных координат
    fl_auto = False  # флаг признака запроса на автозаполнение доски
    i = 0
    while i < len(SHIPS_LIST) and not fl_auto and not flag_exit:
        while True:
            str_ = input("Введите через пробел координаты начала и конца %d-палубного корабля (строка_начала столбец_начала строка_конца столбец_конца).\n"
                         "Если предполагается, что корабль занимает одну клетку, можно допускается ввод одной из координат (строка столбец).\n"
                         "Если же хотите использовать автозаполнение доски (ранее добавленные корабли будут потеряны), введите '%s',"
                         " для очистки игровой доски введите '%s',"
                         " для выхода из игры введите '%s': " % (SHIPS_LIST[i], AUTOMATIC_PLACEMENT, CLEAR_USER_SHIPS, EXIT_WORD))
            try:
                if str_.upper() == AUTOMATIC_PLACEMENT.upper():
                    fl_auto = True
                    break
                elif str_.upper() == CLEAR_USER_SHIPS.upper():
                    game_table_gamer.clear_game_table() # очищаем игровую доску
                    ships_gamer.clear()  # очищаем объект кораблей
                    print("Доска игрока очищена...")
                    game_table_gamer.show(True)
                    i = 0
                    break
                elif str_.upper() == EXIT_WORD.upper():
                    flag_exit = True
                    break
                else:
                    coord = list(map(int, str.split(str_)))
            except Exception:
                print("Ошибка в введенных данных. Попробуйте снова...")
            else:
                if len(coord) == 2:  # если координат только одна (строка столбец), то расширяем их до двух дублированием
                    coord.append(coord[0])
                    coord.append(coord[1])

                if len(coord) == 4:
                    ship_size = ships_gamer.add_ship_by_coordinates(coord[0] - 1, coord[1] - 1, coord[2] - 1,
                                                                    coord[3] - 1, (SHIPS_LIST[i]))
                    if ship_size != SHIPS_LIST[i]:

                        if ship_size == -2:
                            print("Габариты корабля выходят за пределы игрового поля. Попробуйте еще раз...")
                        elif ship_size == -1:
                            print("Корабль расположен по диагонали. Располагаться корабль может либо по горизонтали, либо по вертикали. Попробуйте еще раз...")
                        elif ship_size == 0:
                            print("Корабль находится слишком близко к другому кораблю. Попробуйте еще раз...")
                        else:
                            print(
                                "Ошибка. Размер Вашего корабля: %d-палубный. Ожидаются координаты %d-палубного корабля. Попробуйте еще раз..." % (
                                ship_size, SHIPS_LIST[i]))
                        print("")

                        continue
                    else:
                        game_table_gamer.add_ship(ships_gamer, ships_gamer.count_ships - 1)
                        game_table_gamer.show(True)
                        i += 1
                        break
                else:
                    print("Некорректное количество параметров координат. Попробуйте снова...")
            print("")

    if not flag_exit:
        if fl_auto:  # если выбрано автозаполнение доски игрока
            print("Выбрано автозаполнение кораблей пользователя...")
            if ships_gamer.auto_fill_ships(SHIPS_LIST):  # производим автозаполнение кораблями (ранее добавленные корабли затрутся)
                game_table_gamer.load_ships(ships_gamer)  # загружаем корабли в игровую доску
                print("Корабли успешно добавлены на Вашу игровую доску\n")
            else:
                fl_error = True

        if not fl_error:
            if ships_computer.auto_fill_ships(SHIPS_LIST):
                game_table_computer.load_ships(ships_computer)

                #game_table_computer.show(True)  # для отладки

                time.sleep(1)
                print("Итак... Все подготовительные действия к игре завершены.\n"
                      "Ваша доска выглядит следующим образом:")
                game_table_gamer.show(True)  # показываем результат
                time.sleep(2)

                print('-' * 60)
            else:
                print("Ошибка генерации кораблей для компьютера...")
                fl_error = True

    return not fl_error


# Выводит результат игры
def result_game():
    global flag_exit
    global game_table_gamer
    global game_table_computer

    if flag_exit:
        print("Игра прервана!")
    elif game_table_gamer.is_losing():
        print("Победил компьютер! Вы проиграли!")
    elif game_table_computer.is_losing():
        print("Поздравляем с победой! Вы потопили все корабли противника!")
    else:
        # в нормальной ситуации эта ветвь срабатывать не должна
        print("Непредвиденный результат! Вы умудрились чудом потопить друг друга!")

# Класс генерации и хранения кораблей
class Ships:

    def __init__(self, row_count, col_count, min_space_between_ships=1):
        self._row_count = row_count
        self._col_count = col_count
        self._min_space_between_ships = min_space_between_ships
        self._coordinates = []

    # Автозаполняет объект кораблей по кораблями из списка ship_list, содержащим размеры кораблей, необходимых для генерации
    # При этом все прежние корабли удаляются
    # В случае успешной генерации возвращает True, в случае ошибки возвращает False
    def auto_fill_ships(self, ship_list):
        attempt_count = 100  # количество допустимых попыток автозаполнения

        self.clear()

        fl_error = False
        attempt_num = 0
        while attempt_num < attempt_count:  # даем всего attempt_count попыток автозаполнения
            for i in range(len(SHIPS_LIST)):
                ship_size = self.generate_ship(SHIPS_LIST[i])
                if ship_size != SHIPS_LIST[i]:
                    # Ошибка генерации корабля
                    fl_error = True
                    break

            if fl_error:
                self.clear()
                if attempt_count - attempt_num > 1:  # если это не последняя попытка генерации, то сбрасываем флаг и делаем еще одну попытку
                    fl_error = False
            else:
                break  # в противном случае выходим из цикла не сбрасывая флаг

            attempt_num += 1

        return not fl_error

    # Генерирует корабль с псевдослучайными координатами с размером ship_size
    # Возвращает размер созданного корабля, либо 0 либо -1 в случае неудачи
    def generate_ship(self, ship_size=0):
        size = 0  # размер корабля на очередной попытке генерации
        iter_limit = 100  # лимит итераций генерации корабля (на всякий случай)
        end_coord_row = None  # координаты конечной точки корабля - строка
        end_coord_column = None  # координаты конечной точки корабля - столбец

        # итерации попыток генерации корабля
        i = 0
        while size != ship_size and i < iter_limit:
            start_coord_column = random.randint(0, COUNT_COLUMNS - 1)
            start_coord_row = random.randint(0, COUNT_ROWS - 1)
            dir_hor = (bool)(random.randint(0, 1))  # если True, то корабль располагается по горизонтали

            # вычисляем конечную точку корабля с учетом его размера
            # пусть конечная точка будет всегда либо правее стартовой, либо ниже (зависит от направления корабля)
            # если корабль будет расположен по горизонтали
            if dir_hor == True:
                end_coord_column = start_coord_column + ship_size - 1
                end_coord_row = start_coord_row
            else:  # если же по вертикали
                end_coord_column = start_coord_column
                end_coord_row = start_coord_row + ship_size - 1

            size = self.add_ship_by_coordinates(start_coord_row, start_coord_column, end_coord_row, end_coord_column, ship_size)
            i += 1

        return size

    # Добавляет пользовательский корабль по координатам.
    # В случае успеха возвращает размер добавленного корабля.
    # В противном случае возвращает 0
    def add_ship_by_coordinates(self, start_coord_row, start_coord_column, end_coord_row, end_coord_column, ship_size = 0):
        ship_ = []

        # если корабль расположен по горизонтали
        if start_coord_row == end_coord_row:
            if start_coord_column > end_coord_column:
                start_coord_column, end_coord_column = end_coord_column, start_coord_column
            ship_ = [[start_coord_row, column] for column in range(start_coord_column, end_coord_column + 1)]

        # если же корабль расположен по вертикали
        elif start_coord_column == end_coord_column:
            if start_coord_row > end_coord_row:
                start_coord_row, end_coord_row = end_coord_row, start_coord_row
            ship_ = [[row, start_coord_column] for row in range(start_coord_row, end_coord_row + 1)]

        else:  # в третьем случае, передаем координаты как есть
            ship_ = [[start_coord_row, start_coord_column], [end_coord_row, end_coord_column]]

        return self._add_ship(ship_, ship_size)

    # добавляет корабль с координатами coordinates при условии, что размер корабля с координатами равен ship_size
    # если размер корабля ship_size не указан или равен 0, то корабль будет добавлен независимо от его размера, при условии соблюдения все остальных правил для корабля
    def _add_ship(self, coordinates, ship_size=0):
        # проверка кораблю условиям соответствия (корабль не должен быть расположен по диагонали, выходить за пределы поля)
        lst = list(coordinates)
        set1 = set(map(lambda x: x[0], lst))
        set2 = set(map(lambda x: x[1], lst))

        # Проверяем крайние координаты на факт попадания в поле игровой доски
        if 0 <= (coordinates[0])[0] < self._row_count and 0 <= (coordinates[0])[1] < self._col_count and \
                0 <= (coordinates[-1])[0] < self._row_count and 0 <= (coordinates[-1])[1] < self._col_count:

            # Убеждаемся, что корабль не расположен по диагонали
            if len(set1) == 1 or len(set2) == 1:

                # проходим по всем уже имеющимся кораблям и проверяем соответствие расстояниям
                for i in range(self.count_ships):

                    # неприемлемо, если расстояние между кораблями меньше _min_space_between_ships
                    if self._calculate_min_space_between_two_ships(coordinates,
                                                                   self.get_ship(
                                                                       i)) < self._min_space_between_ships:
                        return 0

                if ship_size == len(
                        coordinates) or ship_size == 0:  # если размеры корабля совпадают с желаемым размером корабля
                    self._coordinates.append(coordinates)  # то добавляем координаты корабля
                    return len(coordinates)
                else:
                    # в противном случае координаты корабля не добавляем, возвращаем размер корабля с неподошедшими координатами
                    return len(coordinates)
            else:
                return -1  # Ошибка. Корабль располагается по диагонали

        return -2  # Ошибка. Координаты корабля выходят за пределы игрового поля

    # функция вычисления между двумя произвольными точками с координатами (горизонталь, вертикаль)
    def _calculate_space_between_two_points(self, coord1: list, coord2: list):
        # для наглядности...
        y1 = coord1[0]
        x1 = coord1[1]

        y2 = coord2[0]
        x2 = coord2[1]

        # теорема Пифагора, возврат вычисленной (длины гипотенузы - 1) в качестве расстояния между двумя точками
        # вычитание 1 сделаем для компенсации того факта, что по этой формуле вплотную стоящие точки имеют все же расстояние 1, что неприемлемо в нашем случае
        # (ведь это расстояние мы принимаем за 0 - вплотную)
        return math.trunc(math.sqrt(math.pow(math.fabs(y1 - y2), 2) + math.pow(math.fabs(x1 - x2), 2))) - 1

    def _calculate_min_space_between_two_ships(self, ship1_: list, ship2_: list):
        min_space = self._calculate_space_between_two_points([0, 0], [self._row_count, self._col_count])

        for coord1 in ship1_:
            for coord2 in ship2_:
                space = self._calculate_space_between_two_points(coord1, coord2)

                if space < min_space:
                    min_space = space

        return min_space

    # очищает список кораблей
    def clear(self):
        if self._coordinates:  # если список координат не пустой
            self._coordinates.clear()

    # возвращает список координат корабля по заданному индексу item_index
    def get_ship(self, item_index):
        if 0 <= item_index < self.count_ships:
            return self._coordinates[item_index]

    # возвращает количество кораблей
    @property
    def count_ships(self):
        return len(self._coordinates)


# Класс игровой доски
class GameTable():

    def __init__(self, ship_: Ships = None, row_count=6, columns_count=6, symbol_void_cell_='O', symbol_cell_delimiter_='|', symbol_hit_='X', symbol_mismatch='T', symbol_place_ship_='.'):

        self._col_count = row_count
        self._row_count = columns_count
        self._symbol_void_cell = symbol_void_cell_
        self._symbol_cell_delimiter = symbol_cell_delimiter_
        self._symbol_hit = symbol_hit_
        self._symbol_mismatch = symbol_mismatch
        self._symbol_place_ship = symbol_place_ship_

        # генерируем игровую доску
        self._game_table = [[self._symbol_void_cell for x in range(self._col_count)] for y in
                            range(self._row_count)]

        # добавляем корабли
        if ship_:
            self.load_ships(ship_)

        # генерируется полный список возможных координат для шагов игрока
        self._moves_variants = [[y, x] for y in range(columns_count) for x in range(row_count)]

    # загружает все корабли из объекта Ship_. Все прежние корабли затираются
    def load_ships(self, Ship_: Ships):
        self.clear_game_table()

        count = Ship_.count_ships
        for i in range(0, count):
            self.add_ship(Ship_, i)

    # добавляет корабль с индексом (номером) item_index из объекта Ship_ на доску
    def add_ship(self, Ship_: Ships, item_index):
        coordinates = Ship_.get_ship(item_index)

        for x, y in coordinates:
            self._game_table[x][y] = self._symbol_place_ship

    # выводит содержимое доски на экран. Если show_ships == False, то корабли не отображаются
    def show(self, show_ships=False):
        header = ""
        string = ""

        for x in range(1, self._col_count + 1):
            header += " " + str(x) + " " + self._symbol_cell_delimiter
        header = "  " + self._symbol_cell_delimiter + header
        print(header)

        str_num = 1
        for y in self._game_table:
            for x in y:
                if show_ships or x != self._symbol_place_ship:
                    string += " " + x + " " + self._symbol_cell_delimiter
                else:
                    string += " " + self._symbol_void_cell + " " + self._symbol_cell_delimiter

            string = str(str_num) + " " + self._symbol_cell_delimiter + string
            print(string)
            string = ""
            str_num += 1

        print('')

    # генерируется случайный ход
    def make_random_move(self):
        coord = []

        len_ = len(self._moves_variants)

        if len_ > 1:
            rnd = random.randint(0, len(self._moves_variants) - 1)
            coord = self._moves_variants.pop(rnd)

        elif len_ == 1:
            coord = self._moves_variants.pop(0)
        else:  # этот вариант работать не должен, присутствует для логической завершенности
            coord = [-1, -1]  # если вариантов для хода не осталось, возвращаем координаты вне игровой доски
            print("Ошибка! Закончились варианты случайных ходов!")

        self._update(coord[0], coord[1])

    # фиксируется ход по координатам
    def make_move(self, coord_row, coord_column):
        try:
            #self._moves_variants.pop([coord_row, coord_column])
            self._moves_variants.remove([coord_row, coord_column])
        except ValueError:
            if 0 <= coord_row < self._row_count and 0 <= coord_column < self._col_count:
                return 0  # ход в ячейку с этими координатами уже был сделан
            else:
                return -1  # Координаты ячейки выходят за пределы игровой доски
        else:
            self._update(coord_row, coord_column)
            return 1

    # Вносит изменения на игровую доску
    def _update(self, row, column):

        if 0 <= column < self._col_count or 0 <= row < self._row_count:
            if self._game_table[row][column] == self._symbol_void_cell:
                self._game_table[row][column] = self._symbol_mismatch
            elif self._game_table[row][column] == self._symbol_place_ship:
                self._game_table[row][column] = self._symbol_hit

    # возвращает True, если на доске зафиксирован проигрыш
    def is_losing(self):
        # проходим построчно по всей игровой доске, ищем символ корабля. Если встретили хотя бы один, то проигрыша нет
        for y in self._game_table:
            if len(set(y).intersection(set([self._symbol_place_ship]))) > 0:
                return False  # проигрыша нет

        return True  # если не встретили ни одного символа корабля, то проигрыш

    # очистка игровой доски
    def clear_game_table(self):
        # просто реинициализируем игровую доску
        if self._game_table:
            self._game_table = [[self._symbol_void_cell for x in range(self._col_count)] for y in
                                range(self._row_count)]


if __name__ == '__main__':
    main()

#################################################################
