import requests
from bs4 import BeautifulSoup
import json

def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537/36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f'Ошибка при запросе: {response.status_code}')
    
    return BeautifulSoup(response.text, 'html.parser')

def parse_product_info(soup):
    try:
        title = soup.find('div', class_='heading').get_text(strip=True)
        price = soup.find('div', class_='spec-about__price').get_text(strip=True).split(' –')[0]
        return title, price
    except AttributeError:
        raise Exception('Не удалось найти необходимые элементы на странице.')

def parse_tables(soup, product_type):
    tables_container = soup.find('div', class_='spec-info__main')
    
    if not tables_container:
        raise Exception('Контейнер с таблицами не найден.')
    
    tables = tables_container.find_all('table')
    
    if not tables:
        raise Exception('Таблицы не найдены.')
    
    combined_data = {}  # Новый словарь для объединенных данных
    
    # Словари для замены названий полей
    field_mapping = {
        'case': {
            '?Типоразмер': 'form_factor',
            'Форм-фактор': 'motherboard_format',
            'Макс. размер материнской платы': 'max_motherboard_size',
            '?Игровой': 'gaming',
            '?Цвет корпуса': 'case_color',
            '?Материал корпуса': 'case_material',
            'Материал передней панели': 'front_panel_material',
            '?Наличие окна на боковой стенке': 'side_window',
            '?Передняя дверь': 'front_door',
            'Материал окна': 'window_material',
            '?LCD дисплей': 'lcd_display',
            '?Внутренние 3,5': 'internal_3_5',
            '?2,5': 'internal_2_5',
            'комбинированный 2.5/3.5': 'combined_2_5_3_5',
            '?Безвинтовое крепление в отсеках 3,5 и 5,25': 'tool_less_mounting',
            '?Док-станция для HDD': 'hdd_dock_station',
            '?Максимальная высота процессорного кулера': 'max_cpu_cooler_height',
            '?Максимальная длина видеокарты': 'max_gpu_length',
            'Съёмная корзина жестких дисков': 'removable_hdd_basket',
            '?Количество слотов расширения': 'expansion_slots',
            '?Низкопрофильные платы расширения': 'low_profile_expansion_cards',
            'Макс. длина блока питания': 'max_psu_length',
            'Шумоизоляция': 'soundproofing',
            '?Расположение БП': 'psu_location',
            'Вентиляторы в комплекте': 'included_fans',
            '?Возможность установки системы жидкостного охлаждения': 'liquid_cooling_support',
            '?Блок управления вентиляторами': 'fan_control_unit',
            '?Съемный воздушный фильтр': 'removable_air_filter',
            'Пылевые фильтры': 'dust_filters',
            'Количество встроенных вентиляторов': 'built_in_fans',
            'Количество мест для вентиляторов': 'fan_mounts',
            'USB 2.0': 'usb_2_0_ports',
            '?USB 3.0': 'usb_3_0_ports',
            '?Выход на наушники': 'headphone_out',
            '?Вход микрофонный': 'microphone_in',
            'USB 3.2 Gen1 Type-A': 'usb_3_2_gen1_type_a',
            '?Встроенный кард-ридер': 'built_in_card_reader',
            'Контроллер подсветки': 'lighting_controller',
            'Цвет подсветки кулера': 'fan_lighting_color',
            'Подсветка корпуса': 'case_lighting',
            'Крепление VESA': 'vesa_mount',
            'Замок': 'lock',
            '?Высота': 'height',
            '?Ширина': 'width',
            '?Глубина': 'depth',
            '?Вес': 'weight'
        },
        'cpu': {
            'Частота': 'frequency',
            'Количество ядер': 'core_count',
            'Кэш': 'cache'
        }
    }
    
    for table in tables:
        table_data = [
            [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
            for row in table.find_all('tr')
            if row.find_all(['td', 'th'])
        ]
        
        # Сохранение данных в зависимости от типа продукта
        if product_type in field_mapping:
            for row in table_data:
                if len(row) >= 2 and row[0] in field_mapping[product_type]:
                    new_key = field_mapping[product_type][row[0]]

                    if '+' in row[1]:
                        combined_data[new_key] = True
                    elif '-' in row[1]:
                        combined_data[new_key] = False
                    elif 'мм' in row[1]:
                        combined_data[new_key] = row[1].split(' ')[0]
                    else:
                        combined_data[new_key] = row[1]

    return combined_data  # Возвращаем объединенные данные

def save_to_json(data, product_type, title):
    filename = f'{product_type}_{title.lower().replace(" ", "_")}.json'
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f'Данные успешно сохранены в {filename}')

def determine_type_from_url(url):
    if 'utility-cases' in url:
        return 'case'
    elif 'utility-cpu' in url:
        return 'cpu'
    else:
        return 'unknown'

def parse_product_and_tables(url):
    try:
        product_type = determine_type_from_url(url)
        soup = fetch_page(url)
        raw_title, price = parse_product_info(soup)
        
        # Передаем тип продукта в функцию парсинга таблиц
        tables = parse_tables(soup, product_type)

        if product_type == 'case':
            title = ''.join(raw_title[22:])
        elif product_type == 'cpu':
            title = ''.join(raw_title[10:])

        result = {
            'type': product_type,
            'title': title,
            'price': price,
            'data': tables  # Объединенные данные теперь здесь
        }

        save_to_json(result, product_type, title)

    except Exception as e:
        print(e)

if __name__ == '__main__':
    product_url = input('Введите ссылку на товар: ')
    parse_product_and_tables(product_url)
