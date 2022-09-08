from random import randint

class Dot:
    def __init__(self, x, y): # инициализируем точки на поле
        self.x = x
        self.y = y
    
    def __eq__(self, other): # определяет поведение оператора равенства, упрощает сравнения точек, чтобы можно было писать x == y
        return self.x == other.x and self.y == other.y
    
    def __repr__(self): # отвечает за вывод точек в консоль, а также нам будет необходимо проверять,если точка в списке
        return f"({self.x}, {self.y})"


class BoardException(Exception): # общий класс для всех исключений, нужен для того, чтобы программа не останавливалась, в случае появления ошибки
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, bow, l, o):# инициализация  точек корабля
        self.bow = bow # координаты
        self.l = l # длина
        self.o = o # ориентация корабля 0- вертикальный 1- горизонтальный
        self.lives = l #
    
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y
            
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))  # получаем список точек корабля
        
        return ship_dots
    
    def shooten(self, shot): # 
        return shot in self.dots

class Board:  # игровое поле
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        
        self.count = 0  #количество пораженных кораблей
        
        self.field = [ ["O"]*size for _ in range(size) ] # поле которое будет содержать сетку
        
        self.busy = [] # занятые точки либо корблем, либо выстрелом
        self.ships = []  # список кораблей, сперва создаем пустым потом будем добавлять
    
    def add_ship(self, ship):# размещение корабля на доске
        
        for d in ship.dots:
            if self.out(d) or d in self.busy: # проверяем, что каждая точка корабля не выходит за границы и не занята
                raise BoardWrongShipException()
        for d in ship.dots: # проставляем квадратики, где есть корабль
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False): # при попадании просталяем точки вокруг подбитого корабля
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy: # если точка не выходит за границы и не занята
                    if verb:
                        self.field[cur.x][cur.y] = "." # добавляем точку
                    self.busy.append(cur) # добавляем в список занятых точек
    
    def __str__(self):
        res = "" # переменная в которую будем записывать доску
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid: # отвечает нужно ли скрывать корабли на доске
            res = res.replace("■", "O")
        return res
    
    def out(self, d):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def shot(self, d): # метод делает выстрел
        if self.out(d): # проверяем выходит ли точка за границы, если да выкидываем исключение
            raise BoardOutException()
        
        if d in self.busy:# проверяем выходит ли точка занята, если да выкидываем исключение
            raise BoardUsedException()
        
        self.busy.append(d) # говорим, что точка занята
        
        for ship in self.ships: #
            if ship.shooten(d):
                ship.lives -= 1 #  уменьшаем количество жизней корабля
                self.field[d.x][d.y] = "X" # на место корабля ставим крестик
                if ship.lives == 0: # если корабль имеет 0 жизней
                    self.count += 1
                    self.contour(ship, verb = True) # обводим корабль
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    
    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self): # бесконечный цикл для выстрела
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player): #класс игрок-компьютер
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5)) # случайно генерируем две точки от 0 до 5
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player): # класс игрок-пользователь
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split() # запрос двух координат
            
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()): # , проверяем, чтобы были числа
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1) # вычитаем еденицу так как индексация идет с  0

class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board
    
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
    
    
    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print("-"*20)
                print("Пользователь выиграл!")
                break
            
            if self.us.board.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
            
g = Game()
g.start()