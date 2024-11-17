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
            #'Материал передней панели': 'front_panel_material',
            '?Наличие окна на боковой стенке': 'side_window',
            #'?Передняя дверь': 'front_door',
            'Материал окна': 'window_material',
            #'?LCD дисплей': 'lcd_display',
            '?Внутренние 3,5': 'internal_3_5',
            '?2,5': 'internal_2_5',
            'комбинированный 2.5/3.5': 'combined_2_5_3_5',
            '?Безвинтовое крепление в отсеках 3,5 и 5,25': 'tool_less_mounting',
            '?Док-станция для HDD': 'hdd_dock_station',
            '?Максимальная высота процессорного кулера': 'max_cpu_cooler_height',
            '?Максимальная длина видеокарты': 'max_gpu_length',
            #'Съёмная корзина жестких дисков': 'removable_hdd_basket',
            #'?Количество слотов расширения': 'expansion_slots',
            #'?Низкопрофильные платы расширения': 'low_profile_expansion_cards',
            'Макс. длина блока питания': 'max_psu_length',
            #'Шумоизоляция': 'soundproofing',
            '?Расположение БП': 'psu_location',
            #'Вентиляторы в комплекте': 'included_fans',
            '?Возможность установки системы жидкостного охлаждения': 'liquid_cooling_support',
            #'?Блок управления вентиляторами': 'fan_control_unit',
            #'?Съемный воздушный фильтр': 'removable_air_filter',
            #'Пылевые фильтры': 'dust_filters',
            #'Количество встроенных вентиляторов': 'built_in_fans',
            #'Количество мест для вентиляторов': 'fan_mounts',
            'USB 2.0': 'usb_2_0_ports',
            '?USB 3.0': 'usb_3_0_ports',
            #'?Выход на наушники': 'headphone_out',
            #'?Вход микрофонный': 'microphone_in',
            #'USB 3.2 Gen1 Type-A': 'usb_3_2_gen1_type_a',
            #'?Встроенный кард-ридер': 'built_in_card_reader',
            #'Контроллер подсветки': 'lighting_controller',
            #'Цвет подсветки кулера': 'fan_lighting_color',
            #'Подсветка корпуса': 'case_lighting',
            #'Крепление VESA': 'vesa_mount',
            #'Замок': 'lock',
            #'?Высота': 'height',
            #'?Ширина': 'width',
            #'?Глубина': 'depth',
            #'?Вес': 'weight'
        },
        'cpu': {
            '?Линейка': 'line',
            '?Сокет': 'socket',
            'Год выхода на рынок': 'release_year',
            #'?Ядро': 'core',
            '?Количество ядер': 'core_count',
            #'Количество производительных ядер': 'performance_core_count',
            'Количество потоков': 'thread_count',
            '?Техпроцесс': 'process_technology',
            '?Интегрированное графическое ядро': 'integrated_graphics',
            '?Частота процессора': 'processor_clock',
            #'Мин. частота производительных ядер': 'min_performance_core_clock',
            #'Макс. частота производительных ядер': 'max_performance_core_clock',
            #'?Частота с Turbo Boost': 'turbo_boost_clock',
            '?Количество каналов памяти': 'memory_channels',
            'Частота памяти': 'memory_clock',
            '?Объем кэша L2': 'l2_cache_size',
            '?Объем кэша L3': 'l3_cache_size',
            '?Тепловыделение': 'tdp',
            'Тип памяти': 'memory_type',
            #'Встроенный контроллер PCI Express': 'pci_express_controller',
            '?Комплектация': 'packaging',
            #'Виртуализация Intel VT-x': 'intel_vt_x',
            #'Виртуализация Intel VT-d': 'intel_vt_d',
            #'Защищенная платформа Intel TXT': 'intel_txt'
        },
        'gpu': {
            #'?Тип видеокарты': 'gpu_type',
            '?Тип подключения': 'connection_type',
            '?Код производителя': 'manufacturer_code',
            '?Видеопроцессор': 'video_processor',
            '?Производитель': 'manufacturer',
            '?Линейка': 'series',
            '?Название': 'name',
            #'?Количество': 'quantity',
            #'?Частота': 'frequency',
            #'Кодовое название': 'code_name',
            #'?Версия PCI Express': 'pci_express_version',
            #'?Число поддерживаемых мониторов': 'supported_monitors_count',
            #'?Макс. разрешение': 'max_resolution',
            '?Количество занимаемых слотов': 'slots_count',
            '?Низкопрофильная карта (Low Profile)': 'low_profile',
            '?Пассивное охлаждение': 'passive_cooling',
            '?Количество вентиляторов': 'fans_count',
            #'?Дизайн системы охлаждения': 'cooling_design',
            #'?Встроенный TV-тюнер': 'built_in_tv_tuner',
            '?Тип памяти': 'memory_type',
            '?Объем памяти': 'memory_size',
            '?Частота памяти': 'memory_frequency',
            '?Шина обмена с памятью': 'memory_bus',
            '?SLI/CrossFire': 'sli_crossfire',
            '?CrossFire X': 'crossfire_x',
            #'?3-Way SLI': 'three_way_sli',
            #'?Quad SLI': 'quad_sli',
            '?NVLink': 'nvlink',
            #'?TurboCache/HyperMemory': 'turbo_cache_hyper_memory',
            #'?Поддержка CUDA': 'cuda_support',
            #'?Поддержка AMD APP (ATI Stream)': 'amd_app_support',
            'Трассировка лучей': 'ray_tracing',
            #'?Математический блок': 'math_unit',
            #'?Число универсальных процессоров': 'universal_processors_count',
            '?Версия DirectX': 'directx_version',
            '?Версия OpenGL': 'opengl_version',
            #'?Число RT ядер': 'rt_cores_count',
            #'?Выход VGA': 'vga_output',
            #'?Выход видео компонентный': 'component_video_output',
            #'?Выход HDMI': 'hdmi_output',
            #'?Количество выходов HDMI': 'hdmi_outputs_count',
            #'?Выход Mini HDMI': 'mini_hdmi_output',
            #'?Выход Micro HDMI': 'micro_hdmi_output',
            #'?Тип HDMI': 'hdmi_type',
            #'?Выход DisplayPort': 'displayport_output',
            #'?Количество выходов DisplayPort': 'displayport_outputs_count',
            #'?Выход Mini DisplayPort': 'mini_displayport_output',
            #'?Версия DisplayPort': 'displayport_version',
            #'?USB Type-C': 'usb_type_c',
            #'?HDCP': 'hdcp',
            #'?VIVO': 'vivo',
            #'?VESA Stereo (Mini-DIN)': 'vesa_stereo',
            #'?TV-out': 'tv_out',
            '?Необходимость дополнительного питания': 'additional_power_required',
            '?Разъем дополнительного питания': 'additional_power_connector',
            '?Рекомендуемая мощность блока питания': 'recommended_power_supply',
            'Ширина': 'width',
            #'?Высота': 'height',
            #'?Толщина': 'thickness'
        },
        'motherboard': {
            '?Производитель': 'manufacturer',
            #'?Игровая': 'gaming',
            #'Серверная': 'server',
            '?Socket': 'socket',
            'Поддерживаемые процессоры': 'supported_cpus',
            '?Количество сокетов': 'socket_count',
            '?Предустановленный процессор': 'preinstalled_cpu',
            '?Тип': 'memory_type',
            '?Поддержка буферизованной (RDIMM) памяти': 'buffered_memory_support',
            '?Макс. объем': 'max_memory',
            '?Количество слотов': 'memory_slots',
            '?Максимальная': 'max_memory_frequency',
            '?Двухканальный': 'dual_channel',
            '?Трехканальный': 'triple_channel',
            '?Четырехканальный': 'quad_channel',
            '?Шестиканальный': 'hexa_channel',
            #'?Производитель': 'chipset_manufacturer',
            '?Название': 'chipset_name',
            '?SLI/CrossFire': 'sli_crossfire',
            #'?BIOS': 'bios',
            #'?Восстановление BIOS': 'bios_recovery',
            #'?Поддержка UEFI': 'uefi_support',
            '?PCI-E 16x': 'pci_e_16x_slots',
            '?PCI-E 1x': 'pci_e_1x_slots',
            '?PCI Express 2.0': 'pci_express_2_0',
            '?PCI Express 3.0': 'pci_express_3_0',
            'PCI Express 4.0': 'pci_express_4_0',
            'PCI Express 5.0': 'pci_express_5_0',
            '?Режимы PCI-E': 'pci_e_modes',
            '?Контроллер IDE': 'ide_controller',
            '?Контроллер SATA': 'sata_controller',
            #'?Режим работы SATA RAID': 'sata_raid_modes',
            '?Количество разъемов SATA 6Gb/s': 'sata_6gbps_ports',
            '?Количество слотов M.2': 'm2_slots',
            'Тип интерфейса M.2': 'm2_interface',
            'Тип слотов M.2': 'm2_slot_type',
            #'?Контроллер SCSI': 'scsi_controller',
            #'?Контроллер SAS': 'sas_controller',
            '?Ethernet': 'ethernet',
            '?Тип Wi-Fi': 'wifi_type',
            '?Bluetooth': 'bluetooth',
            #'?Производитель звукового чипа': 'audio_chip_manufacturer',
            '?Звуковой чип': 'audio_chip',
            '?Звуковая схема': 'audio_channels',
            '?Встроенная графика': 'integrated_graphics',
            '?Количество разъемов USB': 'usb_ports_total',
            #'?Число разъемов USB на задней панели': 'usb_ports_rear',
            #'?Коаксиальный выход на задней панели': 'coaxial_output',
            #'?Оптический выход на задней панели': 'optical_output',
            #'?LPT на задней панели': 'lpt_port',
            #'?S-Video-выход на задней панели': 's_video_output',
            #'?Компонентный видеовыход на задней панели': 'component_video_output',
            #'?D-Sub на задней панели': 'd_sub_output',
            #'?DVI на задней панели': 'dvi_output',
            #'?HDMI на задней панели': 'hdmi_output',
            #'?PS/2 (клавиатура) на задней панели': 'ps2_keyboard',
            #'?PS/2 (мышь) на задней панели': 'ps2_mouse',
            #'?DisplayPort': 'displayport',
            #'?Разъем для подключения ленты RGB': 'rgb_connector',
            #'?Выход S/PDIF': 'spdif_output',
            #'?GAME/MIDI': 'game_midi',
            #'?LPT': 'lpt',
            #'?TV-out': 'tv_out',
            #'?PS/2 (клавиатура)': 'ps2_keyboard',
            #'?PS/2 (мышь)': 'ps2_mouse',
            '?Основной разъем питания': 'main_power_connector',
            '?Разъем питания процессора': 'cpu_power_connector',
            '?Форм-фактор': 'form_factor',
            '?Тип системы охлаждения': 'cooling_type',
            #'Подсветка': 'backlight'
        },
        'psu': {
            '?Форм-фактор': 'form_factor',
            '?Мощность': 'power',
            #'?Система охлаждения': 'cooling_system',
            '?Диаметр вентилятора': 'fan_diameter',
            '?PFC': 'pfc',
            '?Сертификат 80 PLUS': '80_plus_certificate',
            '?Стандарт эффективности': 'efficiency_standard',
            '?Ток по линии +12V': 'current_12v_line',
            #'?Назначение': 'designation',
            'Количество отдельных линий +12V': 'separate_12v_lines',
            'Комбинированная нагрузка по +12V': 'combined_12v_load',
            'КПД': 'efficiency',
            #'?Длина кабеля питания 12В': '12v_power_cable_length',
            #'?Длина кабеля питания': 'power_cable_length',
            '?Отстегивающиеся кабели': 'detachable_cables',
            '?Тип разъема для материнской платы': 'motherboard_connector_type',
            '?Число разъемов 4-pin CPU': '4_pin_cpu_connectors_count',
            '?Число разъемов 4+4 pin CPU': '4_plus_4_pin_cpu_connectors_count',
            '?Число разъемов 8-pin CPU': '8_pin_cpu_connectors_count',
            '?Число разъемов 6+2-pin PCI-E': '6_plus_2_pin_pci_e_connectors_count',
            '?Число разъемов 8-pin PCI-E': '8_pin_pci_e_connectors_count',
            '?Число разъемов 4-pin IDE': '4_pin_ide_connectors_count',
            '?Число разъемов 15-pin SATA': '15_pin_sata_connectors_count',
            #'?Минимальное': 'min_input_voltage',
            #'?Максимальное': 'max_input_voltage',
            #'?Максимальный уровень шума': 'max_noise_level',
            '?Ширина': 'width',
            #'?Высота': 'height',
            #'?Глубина': 'depth',
            '?Вес': 'weight'
        },
        'ram': {
            '?Тип': 'type',
            '?Форм-фактор': 'form_factor',
            '?Объем одного модуля': 'module_capacity',
            '?Количество модулей': 'module_count',
            #'Общий объем': 'total_capacity',
            #'?Количество рангов': 'rank_count',
            '?Тактовая частота': 'clock_frequency',
            #'?Пропускная способность': 'bandwidth',
            '?Поддержка ECC': 'ecc_support',
            '?Буферизованная (Registered)': 'registered',
            '?Низкопрофильная (Low Profile)': 'low_profile',
            '?Радиатор': 'heat_spreader',
            '?Поддержка XMP': 'xmp_support',
            #'CAS Latency': 'cas_latency',
            'Подсветка': 'lighting',
            #'?Тайминги': 'timings',
            #'?CL': 'cl',
            #'?tRCD': 'trcd',
            #'?tRP': 'trp',
            #'?tRAS': 'tras',
            #'?Дополнительная информация': 'additional_info',
            #'?Напряжение питания': 'voltage',
            #'?Чипы': 'chips',
            #'?Количество': 'chip_count',
            #'?Упаковка': 'packaging',
            #'Объем': 'chip_capacity',
            #'Тип микросхем': 'chip_type',
            #'Количество ранков': 'rank_count_chip'
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
    elif 'utility-graphicscards' in url:
        return 'gpu'
    elif 'utility-motherboards' in url:
        return 'motherboard'    
    elif 'utility-powermodules' in url:
        return 'psu'    
    elif 'utility-memory' in url:
        return 'ram' 
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
        elif product_type == 'gpu':
            title = ''.join(raw_title[11:])    
        elif product_type == 'motherboard':
            title = ''.join(raw_title[18:]) 
        elif product_type == 'psu':
            title = ''.join(raw_title[13:]) 
        elif product_type == 'ram':
            title = ''.join(raw_title[14:])   
            title = title.replace('/', '_')       
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