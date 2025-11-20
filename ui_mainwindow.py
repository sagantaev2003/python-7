# ui_mainwindow.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QTableWidget,
    QTableWidgetItem, QComboBox, QMessageBox, QTabWidget, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QScrollArea, QGridLayout, QSpinBox
import requests
import json
from datetime import datetime
from api import get_character, get_random_character, get_episode, get_location, get_all_episodes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rick & Morty Explorer")
        self.setGeometry(100, 100, 1000, 700)
        self.history = []

        self.current_battle = []      # Текущие два персонажа
        self.current_winner = None    # Победитель раунда
        self.tournament_chars = []    # Все персонажи для турнира

    

        # Главный виджет и компоновка
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # ------------------ Стилизация вкладок и блоков ------------------
        self.setStyleSheet("""
            /* Основное окно */
            QMainWindow {
                background-color: #1e1e2f;
            }

            /* Вкладки */
            QTabWidget::pane {
                border: 2px solid #61dafb;
                border-radius: 8px;
                padding: 5px;
                margin-top: 5px;
                background-color: #2c2c3e;
            }

            QTabBar::tab {
                background: #2c2c3e;
                padding: 8px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background: #61dafb;
                color: #000000;
            }

            /* Кнопки */
            QPushButton {
                background-color: #61dafb;
                color: #000000;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: #21a1f1;
            }

            /* Общие виджеты */
            QLabel, QTextEdit, QLineEdit, QListWidget, QComboBox {
                color: #ffffff;
                font-size: 14px;
            }

            /* Поля ввода */
            QLineEdit {
                background-color: #2c2c3e;
                border: 2px solid #61dafb;
                border-radius: 6px;
                padding: 4px;
            }

            /* Текстовые поля */
            QTextEdit {
                background-color: #2c2c3e;
                border: 2px solid #61dafb;
                border-radius: 6px;
                padding: 5px;
            }

            /* Списки */
            QListWidget {
                background-color: #2c2c3e;
                border: 2px solid #61dafb;
                border-radius: 6px;
                padding: 2px;
            }

            /* Таблицы */
            QTableWidget {
                background-color: #2c2c3e;
                border: 2px solid #61dafb;
                border-radius: 6px;
            }

            QComboBox {
                background-color: #2c2c3e;
                border: 2px solid #61dafb;
                border-radius: 6px;
                padding: 3px;
            }
        """)
       
        # Вкладки
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
   
        # Создаём вкладки
        self.create_character_tab()
        self.create_random_tab()
        self.create_episode_tab()
        self.create_location_tab()
        self.create_all_episodes_tab()
        self.create_encyclopedia_tab()
        self.create_history_tab()
        self.create_battle_tab()
        self.create_guess_tab()

# ------------------ Поиск персонажа ------------------
# ------------------ Поиск персонажа с фильтрами ------------------
    def create_character_tab(self):
        self.character_tab = QWidget()
        layout = QVBoxLayout()

        # Поле ввода имени
        self.char_name_input = QLineEdit()
        self.char_name_input.setPlaceholderText("Введите имя персонажа")
        layout.addWidget(self.char_name_input)

        # Кнопка поиска
        btn_find = QPushButton("Найти")
        btn_find.clicked.connect(self.find_character)
        layout.addWidget(btn_find)

        # Фильтр по статусу
        self.status_filter = QComboBox()
        self.status_filter.addItem("Все статусы")
        self.status_filter.addItem("Alive")
        self.status_filter.addItem("Dead")
        self.status_filter.addItem("unknown")
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self.status_filter)

        # Фильтр по виду
        self.species_filter = QComboBox()
        self.species_filter.addItem("Все виды")
        self.species_filter.addItem("Human")
        self.species_filter.addItem("Alien")
        self.species_filter.addItem("Robot")
        self.species_filter.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self.species_filter)

        # ScrollArea для карточек
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(10)
        self.cards_widget.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_widget)
        layout.addWidget(self.scroll_area)

        self.character_tab.setLayout(layout)
        self.tabs.addTab(self.character_tab, "Поиск персонажа")

    # ------------------ Поиск персонажей ------------------
    def find_character(self):
        name = self.char_name_input.text()
        self.found_chars = get_character(name)  # Получаем список персонажей
        if not self.found_chars:
            QMessageBox.warning(self, "Ошибка", "Персонаж не найден")
            return
        self.apply_filters()
        self.history.append(f"Найдены персонажи: {len(self.found_chars)}")
        self.update_history_tab()

    # ------------------ Применение фильтров ------------------
    def apply_filters(self):
        if not hasattr(self, "found_chars"):
            return

        status = self.status_filter.currentText()
        species = self.species_filter.currentText()

        # Фильтруем персонажей
        filtered_chars = [
            char for char in self.found_chars
            if (status == "Все статусы" or char["status"] == status) and
            (species == "Все виды" or char["species"] == species)
        ]

        if not filtered_chars:
            filtered_chars = self.found_chars
            filter_note = f"Фильтр слишком строгий — показываем всех ({len(filtered_chars)})"
        else:
            filter_note = f"Показано {len(filtered_chars)} из {len(self.found_chars)}"

        # Очищаем старые карточки
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        row = 0
        col = 0
        max_columns = 3

        # Сообщение о фильтре
        info_label = QLabel(filter_note)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        self.cards_layout.addWidget(info_label, row, 0, 1, max_columns)
        row += 1

        for char in filtered_chars:
            card = QWidget()
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(5, 5, 5, 5)
            card_layout.setSpacing(5)
            card.setLayout(card_layout)
            card.setMaximumWidth(200)

            # Аватарка
            pixmap = QPixmap()
            try:
                response = requests.get(char["image"])
                pixmap.loadFromData(response.content)
            except:
                pass
            label_img = QLabel()
            label_img.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
            label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(label_img)

            # Информация
            info = QLabel(
                f"Имя: {char['name']}\n"
                f"Статус: {char['status']}\n"
                f"Вид: {char['species']}\n"
                f"Локация: {char['location']}\n"
                f"Эпизодов: {char['episodes_count']}"
            )
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info.setWordWrap(True)
            card_layout.addWidget(info)

            # Рейтинг
            rating_label = QLabel("Рейтинг (1-5):")
            rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(rating_label)

            rating_spin = QSpinBox()
            rating_spin.setRange(1, 5)
            rating_spin.setValue(char.get("rating", 3))
            card_layout.addWidget(rating_spin)

            btn_save_rating = QPushButton("Подтвердить рейтинг")
            card_layout.addWidget(btn_save_rating)

            # Кнопка "Добавить в энциклопедию"
            btn_add_encyclopedia = QPushButton("Добавить в энциклопедию")
            card_layout.addWidget(btn_add_encyclopedia)

            # Сохраняем рейтинг
            def make_save_rating(character, spin_box):
                def save_rating():
                    try:
                        with open("encyclopedia.json", "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if not isinstance(data, list):
                                data = []
                    except:
                        data = []

                    found = False
                    for i, item in enumerate(data):
                        if isinstance(item, dict) and item.get("name") == character.get("name"):
                            data[i]["rating"] = spin_box.value()
                            found = True
                            break

                    if not found:
                        new_char = character.copy()
                        new_char["rating"] = spin_box.value()
                        data.append(new_char)

                    with open("encyclopedia.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    QMessageBox.information(
                        None, "Сохранено", f"Рейтинг {character.get('name')} установлен на {spin_box.value()}"
                    )
                return save_rating

            btn_save_rating.clicked.connect(make_save_rating(char, rating_spin))

            # Добавление персонажа в энциклопедию
            def make_add_to_encyclopedia(character):
                def add():
                    try:
                        with open("encyclopedia.json", "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if not isinstance(data, list):
                                data = []
                    except:
                        data = []

                    # Проверяем, есть ли персонаж уже
                    if not any(item.get("name") == character.get("name") for item in data if isinstance(item, dict)):
                        data.append(character)

                    with open("encyclopedia.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                     # ✅ Обновляем вкладку энциклопедии сразу
                    self.update_encyclopedia_tab()

                    QMessageBox.information(None, "Добавлено", f"{character.get('name')} добавлен в энциклопедию")
                return add

            btn_add_encyclopedia.clicked.connect(make_add_to_encyclopedia(char))

            self.cards_layout.addWidget(card, row, col)
            col += 1
            if col >= max_columns:
                col = 0
                row += 1

        # Убедимся, что прокрутка работает корректно
        self.cards_widget.adjustSize()



    # ------------------ Случайный персонаж ------------------
    def create_random_tab(self):
        self.random_tab = QWidget()
        layout = QVBoxLayout()

        btn_random = QPushButton("🎲 Получить случайного персонажа")
        btn_random.clicked.connect(self.find_random_character)
        layout.addWidget(btn_random)

        self.random_image = QLabel()
        self.random_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.random_image)

        self.random_info = QTextEdit()
        self.random_info.setReadOnly(True)
        layout.addWidget(self.random_info)

        btn_add = QPushButton("Добавить в энциклопедию")
        btn_add.clicked.connect(self.add_to_encyclopedia_from_random)
        layout.addWidget(btn_add)

        self.random_tab.setLayout(layout)
        self.tabs.addTab(self.random_tab, "Случайный персонаж")

    def find_random_character(self):
        char = get_random_character()
        if char:
            self.random_info.setText(
                f"Имя: {char['name']}\n"
                f"Статус: {char['status']}\n"
                f"Вид: {char['species']}\n"
                f"Локация: {char['location']}\n"
                f"Эпизодов: {char['episodes_count']}"
            )
            pixmap = QPixmap()
            response = requests.get(char["image"])
            pixmap.loadFromData(response.content)
            self.random_image.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))

            self.history.append(f"Случайный персонаж: {char['name']}")
            self.update_history_tab()
            self.last_random_character = char

    def add_to_encyclopedia_from_random(self):
        try:
            with open("encyclopedia.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []

        if hasattr(self, "last_random_character"):
            if not any(c["name"] == self.last_random_character["name"] for c in data):
                data.append(self.last_random_character)
                with open("encyclopedia.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Сохранено", "Персонаж добавлен в энциклопедию")
                self.history.append(f"Добавлен в энциклопедию: {self.last_random_character['name']}")
                self.update_history_tab()
                self.update_encyclopedia_tab()
            else:
                QMessageBox.information(self, "Инфо", "Персонаж уже в энциклопедии")

    # ------------------ Эпизод ------------------
    def create_episode_tab(self):
        self.episode_tab = QWidget()
        layout = QVBoxLayout()

        self.episode_input = QLineEdit()
        self.episode_input.setPlaceholderText("Введите номер эпизода (например 1)")
        layout.addWidget(self.episode_input)

        btn_find = QPushButton("Найти эпизод")
        btn_find.clicked.connect(self.find_episode)
        layout.addWidget(btn_find)

        self.episode_info = QTextEdit()
        self.episode_info.setReadOnly(True)
        layout.addWidget(self.episode_info)

        self.episode_tab.setLayout(layout)
        self.tabs.addTab(self.episode_tab, "Поиск эпизода")

    #Поиск эпизод
    def find_episode(self):
        num = self.episode_input.text().strip()
        if not num:
            QMessageBox.warning(self, "Ошибка", "Введите номер эпизода!")
            return

        try:
            ep = get_episode(num)
        except Exception as e:
            ep = None
            print(f"Ошибка при получении эпизода: {e}")

        if ep is None:
            QMessageBox.information(self, "Не найдено", f"Эпизод {num} не найден")
            return

        # Вывод информации о эпизоде
        chars_display = ', '.join(ep.get("characters", []))
        self.episode_info.setText(
            f"Название: {ep.get('name', 'Неизвестно')}\n"
            f"Дата выхода: {ep.get('air_date', 'Неизвестно')}\n"
            f"Код: {ep.get('episode', 'Неизвестно')}\n"
            f"Персонажи: {chars_display if chars_display else 'Нет данных'}"
        )

        self.history.append(f"Просмотрен эпизод: {ep.get('name', num)}")
        self.update_history_tab()


    # ------------------ Локация ------------------
    def create_location_tab(self):
        self.location_tab = QWidget()
        layout = QVBoxLayout()

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Введите название локации")
        layout.addWidget(self.location_input)

        btn_find = QPushButton("Найти локацию")
        btn_find.clicked.connect(self.find_location)
        layout.addWidget(btn_find)

        self.location_info = QTextEdit()
        self.location_info.setReadOnly(True)
        layout.addWidget(self.location_info)

        self.location_tab.setLayout(layout)
        self.tabs.addTab(self.location_tab, "Поиск локации")

    def find_location(self):
        name = self.location_input.text()
        loc = get_location(name)
        if loc:
            self.location_info.setText(
                f"Название: {loc['name']}\n"
                f"Тип: {loc['type']}\n"
                f"Измерение: {loc['dimension']}\n"
                f"Жителей: {loc['residents_count']}"
            )
            self.history.append(f"Найдена локация: {loc['name']}")
            self.update_history_tab()
        else:
            QMessageBox.warning(self, "Ошибка", "Локация не найдена")

    # ------------------ Все эпизоды ------------------
    def create_all_episodes_tab(self):
        self.all_episodes_tab = QWidget()
        layout = QVBoxLayout()

        self.season_filter = QComboBox()
        self.season_filter.addItem("Все сезоны")
        for i in range(1, 6):
            self.season_filter.addItem(f"Сезон {i}")
        self.season_filter.currentIndexChanged.connect(self.update_all_episodes)
        layout.addWidget(self.season_filter)

        btn_load = QPushButton("📥 Загрузить эпизоды")
        btn_load.clicked.connect(self.update_all_episodes)
        layout.addWidget(btn_load)

        self.episodes_table = QTableWidget()
        self.episodes_table.setColumnCount(4)
        self.episodes_table.setHorizontalHeaderLabels(["№", "Название", "Код", "Дата выхода"])
        layout.addWidget(self.episodes_table)

        self.all_episodes_tab.setLayout(layout)
        self.tabs.addTab(self.all_episodes_tab, "Список эпизодов")

    def update_all_episodes(self):
        episodes = get_all_episodes()
        season = self.season_filter.currentIndex()
        filtered = []
        for ep in episodes:
            try:
                ep_season = int(ep["code"][1:3])  # ключ "code" вместо "episode"
            except:
                ep_season = 0
            if season == 0 or ep_season == season:
                filtered.append(ep)

        self.episodes_table.setRowCount(len(filtered))
        for i, ep in enumerate(filtered):
            self.episodes_table.setItem(i, 0, QTableWidgetItem(str(ep["id"])))
            self.episodes_table.setItem(i, 1, QTableWidgetItem(ep["name"]))
            self.episodes_table.setItem(i, 2, QTableWidgetItem(ep["code"]))
            self.episodes_table.setItem(i, 3, QTableWidgetItem(ep["air_date"]))

        self.history.append("Просмотрен список эпизодов")
        self.update_history_tab()

    # ------------------ Энциклопедия ------------------
    def create_encyclopedia_tab(self):
        self.encyclopedia_tab = QWidget()
        layout = QVBoxLayout()

        self.encyclopedia_list = QListWidget()
        self.encyclopedia_list.itemClicked.connect(self.show_encyclopedia_character)
        layout.addWidget(self.encyclopedia_list)

        btn_delete = QPushButton("Удалить выбранного")
        btn_delete.clicked.connect(self.delete_selected_character)
        layout.addWidget(btn_delete)

        btn_clear = QPushButton("Очистить энциклопедию")
        btn_clear.clicked.connect(self.clear_encyclopedia)
        layout.addWidget(btn_clear)

        self.encyclopedia_tab.setLayout(layout)
        self.tabs.addTab(self.encyclopedia_tab, "Энциклопедия")
        self.update_encyclopedia_tab()

    def update_encyclopedia_tab(self):
        self.encyclopedia_list.clear()
        try:
            with open("encyclopedia.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []

        for char in data:
            self.encyclopedia_list.addItem(char["name"])

    def show_encyclopedia_character(self, item):
        name = item.text()
        try:
            with open("encyclopedia.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []

        for char in data:
            if char["name"] == name:
                rating = char.get("rating", "не установлен")
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(char["name"])
                msg_box.setText(
                    f"Имя: {char['name']}\n"
                    f"Статус: {char['status']}\n"
                    f"Вид: {char['species']}\n"
                    f"Локация: {char['location']}\n"
                    f"Эпизодов: {char['episodes_count']}\n"
                    f"Рейтинг: {rating}"
                )
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()
                break



    def delete_selected_character(self):
        selected = self.encyclopedia_list.currentItem()
        if not selected:
            return
        name = selected.text()
        try:
            with open("encyclopedia.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []

        data = [c for c in data if c["name"] != name]
        with open("encyclopedia.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.update_encyclopedia_tab()

    def clear_encyclopedia(self):
        with open("encyclopedia.json", "w", encoding="utf-8") as f:
            json.dump([], f)
        self.update_encyclopedia_tab()

    # ------------------ История ------------------
# ------------------ История ------------------
    def create_history_tab(self):
        self.history_tab = QWidget()
        layout = QVBoxLayout()

        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        btn_export = QPushButton("💾 Экспорт истории")
        btn_export.clicked.connect(self.export_history)
        layout.addWidget(btn_export)

        self.history_tab.setLayout(layout)
        self.tabs.addTab(self.history_tab, "История действий")

    def update_history_tab(self):
        self.history_list.clear()
        for h in self.history:
            self.history_list.addItem(h)

    def export_history(self):
        if not self.history:
            QMessageBox.information(self, "Экспорт", "История пуста!")
            return

        # Диалог выбора файла и формата
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить историю действий",
            "",
            "JSON (*.json);;Text (*.txt)"
        )

        if not file_path:
            return  # Пользователь отменил

        try:
            if file_path.endswith(".json"):
                data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "actions": self.history
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Экспорт", f"История экспортирована в JSON:\n{file_path}")

            else:  # TXT
                with open(file_path, "w", encoding="utf-8") as f:
                    for h in self.history:
                        f.write(h + "\n")
                QMessageBox.information(self, "Экспорт", f"История экспортирована в TXT:\n{file_path}")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось экспортировать историю:\n{e}")


# ------------------ Турнир персонажей / Сравнение ------------------
# ------------------ Вкладка Турнира ------------------
    def create_battle_tab(self):
        self.battle_tab = QWidget()
        layout = QVBoxLayout()

        self.btn_start_tournament = QPushButton("Начать турнир")
        self.btn_start_tournament.clicked.connect(self.start_tournament)
        layout.addWidget(self.btn_start_tournament)

        # Блок для двух персонажей
        self.battle_widget = QWidget()
        battle_layout = QHBoxLayout()
        self.battle_widget.setLayout(battle_layout)

        # Персонаж 1
        self.battle_img1 = QLabel()
        self.battle_img1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_info1 = QLabel()  # информация
        self.battle_info1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_info1.setWordWrap(True)
        self.battle_btn1 = QPushButton("Кнопка 1")
        self.battle_btn1.clicked.connect(lambda: self.choose_winner(0))
        layout1 = QVBoxLayout()
        layout1.addWidget(self.battle_img1)
        layout1.addWidget(self.battle_info1)
        layout1.addWidget(self.battle_btn1)
        battle_layout.addLayout(layout1)

        # Персонаж 2
        self.battle_img2 = QLabel()
        self.battle_img2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_info2 = QLabel()  # информация
        self.battle_info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.battle_info2.setWordWrap(True)
        self.battle_btn2 = QPushButton("Кнопка 2")
        self.battle_btn2.clicked.connect(lambda: self.choose_winner(1))
        layout2 = QVBoxLayout()
        layout2.addWidget(self.battle_img2)
        layout2.addWidget(self.battle_info2)
        layout2.addWidget(self.battle_btn2)
        battle_layout.addLayout(layout2)


        layout.addWidget(self.battle_widget)
        self.battle_tab.setLayout(layout)
        self.tabs.addTab(self.battle_tab, "Турнир")

    # ------------------ Старт турнира ------------------
    def start_tournament(self):
        self.history.append("Начат турнир")
        self.update_history_tab()

        # Берём первых двух случайных персонажей
        self.current_battle = []
        while len(self.current_battle) < 2:
            char = get_random_character()
            if char and not any(c["name"] == char["name"] for c in self.current_battle):
                self.current_battle.append(char)

        self.next_round = []
        self.load_battle()

    # ------------------ Загрузка текущей пары ------------------
    def load_battle(self):
        char1, char2 = self.current_battle

        # Кнопки под аватарками
        self.battle_btn1.setText("Кнопка 1")
        self.battle_btn2.setText("Кнопка 2")

        # Создаём виджеты с аватаркой и информацией
        for i, char in enumerate([char1, char2]):
            pixmap = QPixmap()
            response = requests.get(char["image"])
            pixmap.loadFromData(response.content)
            img_label = self.battle_img1 if i == 0 else self.battle_img2
            img_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

            # Информация под аватаркой
            info_text = (
                f"Имя: {char['name']}\n"
                f"Статус: {char['status']}\n"
                f"Вид: {char['species']}\n"
                f"Локация: {char['location']}\n"
                f"Эпизодов: {char['episodes_count']}"
            )
            if i == 0:
                self.battle_info1.setText(info_text)
            else:
                self.battle_info2.setText(info_text)


    # ------------------ Выбор победителя ------------------
    def choose_winner(self, winner_index):
        loser_index = 1 if winner_index == 0 else 0
        winner = self.current_battle[winner_index]

        self.next_round.append(winner)  # Победитель идёт в следующий раунд
        self.history.append(f"Победитель раунда: {winner['name']}")
        self.update_history_tab()

        # Новый случайный персонаж вместо проигравшего
        while True:
            new_char = get_random_character()
            if new_char and new_char["name"] != winner["name"]:
                break

        self.current_battle[loser_index] = new_char
        self.load_battle()

    # ------------------ Все эпизоды ------------------
    def create_all_episodes_tab(self):
        self.all_episodes_tab = QWidget()
        layout = QVBoxLayout()

        # Выпадающий фильтр по сезону
        self.season_filter = QComboBox()
        self.season_filter.addItem("Все сезоны")
        for i in range(1, 6):
            self.season_filter.addItem(f"Сезон {i}")
        self.season_filter.currentIndexChanged.connect(self.update_all_episodes)
        layout.addWidget(self.season_filter)

        # Поле для ручного ввода сезона, например S01
        self.season_input = QLineEdit()
        self.season_input.setPlaceholderText("Введите сезон (например S01)")
        layout.addWidget(self.season_input)

        btn_filter = QPushButton("Фильтровать по сезону")
        btn_filter.clicked.connect(self.filter_by_season_input)
        layout.addWidget(btn_filter)

        # Кнопка загрузки всех эпизодов
        btn_load = QPushButton("📥 Загрузить эпизоды")
        btn_load.clicked.connect(self.update_all_episodes)
        layout.addWidget(btn_load)

        # Таблица эпизодов
        self.episodes_table = QTableWidget()
        self.episodes_table.setColumnCount(4)
        self.episodes_table.setHorizontalHeaderLabels(["№", "Название", "Код", "Дата выхода"])
        layout.addWidget(self.episodes_table)

        self.all_episodes_tab.setLayout(layout)
        self.tabs.addTab(self.all_episodes_tab, "Список эпизодов")

    # ------------------ Обновление таблицы по выпадающему списку ------------------
    def update_all_episodes(self):
        episodes = get_all_episodes()
        season = self.season_filter.currentIndex()
        filtered = []
        for ep in episodes:
            try:
                ep_season = int(ep["code"][1:3])  # ключ "code" вместо "episode"
            except:
                ep_season = 0
            if season == 0 or ep_season == season:
                filtered.append(ep)

        self.episodes_table.setRowCount(len(filtered))
        for i, ep in enumerate(filtered):
            self.episodes_table.setItem(i, 0, QTableWidgetItem(str(ep["id"])))
            self.episodes_table.setItem(i, 1, QTableWidgetItem(ep["name"]))
            self.episodes_table.setItem(i, 2, QTableWidgetItem(ep["code"]))
            self.episodes_table.setItem(i, 3, QTableWidgetItem(ep["air_date"]))

        self.history.append("Просмотрен список эпизодов")
        self.update_history_tab()

    # ------------------ Фильтрация по вводу сезона S01, S02 ------------------
    def filter_by_season_input(self):
        season_text = self.season_input.text().strip().upper()  # например "S01"
        if not season_text.startswith("S") or not season_text[1:].isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите сезон в формате S01, S02 и т.д.")
            return

        episodes = get_all_episodes()
        filtered = []

        for ep in episodes:
            if ep["code"].upper().startswith(season_text):
                filtered.append(ep)

        self.episodes_table.setRowCount(len(filtered))
        for i, ep in enumerate(filtered):
            self.episodes_table.setItem(i, 0, QTableWidgetItem(str(ep["id"])))
            self.episodes_table.setItem(i, 1, QTableWidgetItem(ep["name"]))
            self.episodes_table.setItem(i, 2, QTableWidgetItem(ep["code"]))
            self.episodes_table.setItem(i, 3, QTableWidgetItem(ep["air_date"]))

        self.history.append(f"Фильтр эпизодов по сезону {season_text}")
        self.update_history_tab()

# ------------------ Вкладка мини-квеста ------------------
    def create_guess_tab(self):
        self.guess_tab = QWidget()
        layout = QVBoxLayout()

        # Кнопка для начала нового раунда
        self.btn_new_guess = QPushButton("Начать новый раунд")
        self.btn_new_guess.clicked.connect(self.start_new_guess)
        layout.addWidget(self.btn_new_guess)

        # Подсказки
        self.guess_hint = QLabel("Подсказки появятся здесь")
        self.guess_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.guess_hint)

        # Поле ввода ответа
        self.guess_input = QLineEdit()
        self.guess_input.setPlaceholderText("Введите имя персонажа")
        layout.addWidget(self.guess_input)

        # Кнопка проверки
        self.btn_check_guess = QPushButton("Проверить")
        self.btn_check_guess.clicked.connect(self.check_guess)
        layout.addWidget(self.btn_check_guess)

        # Результат
        self.guess_result = QLabel("")
        self.guess_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.guess_result)

        self.guess_tab.setLayout(layout)
        self.tabs.addTab(self.guess_tab, "Угадай персонажа")

    # ------------------ Новый раунд ------------------
    def start_new_guess(self):
        self.current_guess_char = get_random_character()
        if self.current_guess_char:
            hints = (
                f"Статус: {self.current_guess_char['status']}\n"
                f"Вид: {self.current_guess_char['species']}\n"
                f"Локация: {self.current_guess_char['location']}"
            )
            self.guess_hint.setText(hints)
            self.guess_input.clear()
            self.guess_result.setText("")
            self.history.append(f"Начат мини-квест с персонажем {self.current_guess_char['name']}")
            self.update_history_tab()

    # ------------------ Проверка ответа ------------------
    def check_guess(self):
        user_input = self.guess_input.text().strip()
        if not hasattr(self, "current_guess_char"):
            return
        if user_input.lower() == self.current_guess_char["name"].lower():
            self.guess_result.setText("✅ Правильно!")
            self.history.append(f"Угадал персонажа: {self.current_guess_char['name']}")
        else:
            self.guess_result.setText(f"❌ Неправильно! Это {self.current_guess_char['name']}")
            self.history.append(f"Не угадал персонажа: {self.current_guess_char['name']}")
        self.update_history_tab()
