import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import time

# URL страницы с результатами поиска на Avito
url = "https://www.avito.ru/sankt-peterburg/avtomobili/nevskiy?pmax=1500000&pmin=1000000&s=104"

# Заголовки, чтобы имитировать браузер
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
}



# Отправляем GET-запрос с заголовками
try:
    response = requests.get(url, headers=headers)
    # Проверка, успешен ли запрос
    if response.status_code != 200:
        print("Ошибка при получении страницы:", response.status_code)
    else:
        # Создаем объект BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все объявления на странице
        items = soup.find_all('div', class_='iva-item-root-_lk9K')  # Убедитесь, что класс верный

        # Открываем CSV файл для записи результатов
        with open('avito_cars.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Название', 'Цена', 'Дата публикации', 'URL'])

            # Текущая дата
            current_date = datetime.now()

            # Флаг для проверки наличия объявлений
            found_items = False

            # Обрабатываем каждое объявление
            for item in items:
                # Извлекаем название автомобиля
                title = item.find('h3', class_='title-root-zZCwT')
                if title:
                    title_text = title.text.strip()
                else:
                    continue  # Пропускаем, если нет названия

                # Извлекаем цену
                price = item.find('span', class_='price-text-_YGDY')
                if price:
                    price_text = price.text.strip()
                else:
                    continue  # Пропускаем, если нет цены

                # Извлекаем дату публикации
                date_str = item.find('div', class_='date-text-KmWDf')
                if date_str:
                    date_str = date_str.text.strip()
                else:
                    continue  # Пропускаем, если нет даты публикации

                # Преобразуем строку даты в объект datetime
                if 'минут' in date_str or 'час' in date_str:
                    publish_date = current_date.date()
                elif 'вчера' in date_str:
                    publish_date = (current_date - timedelta(days=1)).date()
                elif 'дней' in date_str:
                    days_ago = int(date_str.split()[0])
                    publish_date = (current_date - timedelta(days=days_ago)).date()
                else:
                    continue  # Пропускаем, если дата не подходит

                # Проверяем, что объявление не старше 3 дней
                if (current_date.date() - publish_date).days > 3:
                    continue

                # Извлекаем URL объявления
                url_item = item.find('a', class_='link-link-MbQDP')
                if url_item:
                    url_item = 'https://www.avito.ru' + url_item['href']
                else:
                    continue  # Пропускаем, если нет URL

                # Записываем данные в CSV файл
                writer.writerow([title_text, price_text, publish_date, url_item])
                found_items = True

                # Задержка между запросами
                time.sleep(1)  # Задержка в 1 секунду

            if found_items:
                print("Данные успешно сохранены в файл avito_cars.csv")
            else:
                print("Не найдено ни одного объявления, соответствующего критериям.")

except Exception as e:
    print("Произошла ошибка:", str(e))
