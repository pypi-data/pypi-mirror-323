
import typing as _typing
import types as _types

try:
    import KeyisBClient
except ImportError:
    pass

try:
    from PyQt6 import QtWidgets as _QtWidgets
    from PyQt6.QtCore import QByteArray, QDateTime
except ImportError:
    pass

from .core import _EventTarget, Url
from enum import Enum


class __engine:
    """
    Класс engine
    ~~~~~~~~~~~~~~

    Класс, содержащий методы для управления окнами и специфическими для языка Python функциями
    в контексте веб-страницы. Этот класс предназначен для интеграции с браузером и управления
    отображением пользовательского интерфейса.
    """
    
    def setWidget(self, widget: '_QtWidgets.QWidget') -> None: # type: ignore
        """
        Установка виджета страницы в окно браузера.

        Этот метод устанавливает указанный виджет в окно браузера, позволяя отображать
        интерфейс страницы в браузере. Виджет должен быть объектом типа QWidget и будет
        использоваться для представления интерфейса веб-страницы.

        :param widget QWidget: Виджет, представляющий интерфейс страницы.
        """
        ...
engine = __engine() # dw > 0.0.2
"""
Управление движком
~~~~~~~~~~~~~~~~~~

Класс, содержащий методы для управления окнами и специфическими для языка Python и движка
`KeyisBPythonEngine` через `MMBDWMidleEngine` функциями в контексте веб-страницы. Этот класс предназначен для
интеграции с браузером и управления
отображением пользовательского интерфейса.
"""
PyEngine = __engine() # совместимость с dw < 0.0.2
"""
❗☠️ Устаревший метод.❗ Новый метод engine
~~~~
* (будет удален примерно в версии dw > 1.0.0)
"""



class Cookie:
    """
    Объект Cookie
    ~~~~~~~~~~~~~

    Предназначен для создания записей в cookieStore

    Для получения доступа к cookieStore используйте document.cookieStore
    """
    class SameSite(Enum):
        Default = 0
        None_ = 1
        Lax = 2
        Strict = 3

    class DnsType(Enum):
        Www = 0
        """Www: World Wide Web (default)"""

        Gw = 1
        """GW"""

    class RawForm(Enum):
        NameAndValueOnly = 0
        Full = 1

    @_typing.overload
    def __init__(self, cookie: 'Cookie') -> None: ...

    @_typing.overload
    def __init__(self, name: str, value: _typing.Any) -> None: ...

    @_typing.overload
    def __init__(self, name: _typing.Union['QByteArray', bytes, bytearray, memoryview] = b"", 
                 value: _typing.Union['QByteArray', bytes, bytearray, memoryview] = b"") -> None: ...

    def __init__(self,  # type: ignore
                 name_or_cookie: _typing.Union['QByteArray', bytes, bytearray, memoryview, 'Cookie', str] = b"", 
                 value: _typing.Union['QByteArray', bytes, bytearray, memoryview, _typing.Any] = b"") -> None:
        """
        Инициализирует объект cookie с заданным именем и значением,
        или создает копию другого объекта `Cookie`.

        :param name_or_other: Имя cookie или другой объект `Cookie`.
        :param value: Значение cookie (если используется имя).
        """
        ...
    def setSameSitePolicy(self, sameSite: 'Cookie.SameSite') -> None:
        """
        Устанавливает политику SameSite для cookie.

        :param sameSite: Политика SameSite.
        """
        ...

    def sameSitePolicy(self) -> 'Cookie.SameSite':
        """
        Возвращает текущую политику SameSite для cookie.

        :return: Политика SameSite.
        """
        ...

    def normalize(self, url: Url) -> None:
        """
        Нормализует cookie в соответствии с заданным URL.

        :param url: URL для нормализации.
        """
        ...

    def hasSameIdentifier(self, cookie: 'Cookie') -> bool:
        """
        Проверяет, имеет ли cookie такой же идентификатор, как и другой cookie.

        :param other: Другой объект `Cookie`.
        :return: True, если идентификаторы совпадают, иначе False.
        """
        ...

    def swap(self, other: 'Cookie') -> None:
        """
        Обменивает содержимое текущего cookie с другим объектом `Cookie`.

        :param other: Другой объект `Cookie`.
        """
        ...

    def setHttpOnly(self, enable: bool) -> None:
        """
        Устанавливает флаг `HttpOnly` для cookie.

        :param enable: True для включения, False для отключения.
        """
        ...

    def isHttpOnly(self) -> bool:
        """
        Проверяет, является ли cookie HttpOnly.

        :return: True, если HttpOnly, иначе False.
        """
        ...

    @staticmethod
    def parseCookies(cookieString: _typing.Union['QByteArray', bytes, bytearray, memoryview]) -> _typing.List['Cookie']:
        """
        Разбирает строку cookie и возвращает список объектов `Cookie`.

        :param cookieString: Строка cookie для разбора.
        :return: Список объектов `Cookie`.
        """
        ...

    def toRawForm(self, form: 'Cookie.RawForm' = RawForm.Full) -> 'QByteArray':
        """
        Преобразует cookie в строковое представление.

        :param form: Формат представления (NameAndValueOnly или Full).
        :return: Строковое представление cookie.
        """
        ...

    def setValue(self, value: _typing.Union['QByteArray', bytes, bytearray, memoryview, str, _typing.Any]) -> None:
        """
        Устанавливает значение cookie.

        :param value: Значение cookie.
        """
        ...

    def value(self) -> _typing.Union['QByteArray', bytes, bytearray, memoryview, str, _typing.Any]:
        """
        Возвращает значение cookie.

        :return: Значение cookie.
        """
        ...

    def setName(self, cookieName: _typing.Union['QByteArray', bytes, bytearray, memoryview, str]) -> None:
        """
        Устанавливает имя cookie.

        :param cookieName: Имя cookie.
        """
        ...

    @_typing.overload
    def name(self) -> str:
        ...
    @_typing.overload
    def name(self, returntype: str) -> str:
        ...
    @_typing.overload
    def name(self, returntype: 'QByteArray') -> 'QByteArray':
        ...

    def name(self, returntype: _typing.Union['QByteArray', 'str'] = 'str') -> _typing.Union[str, 'QByteArray']:
        """
        Возвращает имя cookie.

        :return: Имя cookie.
        """
        ...
    
    def setDnsType(self, dnsType: 'DnsType') -> None:
        """
        Устанавливает DNS-тип cookie.
        :param dnsType: DNS-тип cookie ('internet' или 'gw').
        """
        ...

    def dnsType(self) -> 'DnsType':
        ...

    def setPath(self, path: _typing.Optional[str]) -> None:
        """
        Устанавливает путь cookie.

        :param path: Путь для cookie.
        """
        ...

    def path(self) -> str:
        """
        Возвращает путь cookie.

        :return: Путь cookie.
        """
        ...

    def setDomain(self, domain: _typing.Optional[str]) -> None:
        """
        Устанавливает домен cookie.

        :param domain: Домен для cookie.
        """
        ...

    def domain(self) -> str:
        """
        Возвращает домен cookie.

        :return: Домен cookie.
        """
        ...

    def setExpirationDate(self, date: _typing.Union['QDateTime', _typing.Any]) -> None:
        """
        Устанавливает дату истечения срока действия cookie.

        :param date: Дата истечения срока действия.
        """
        ...

    def expirationDate(self) -> _typing.Optional['QDateTime']:
        """
        Возвращает дату истечения срока действия cookie.

        :return: Дата истечения срока действия или None, если cookie сессионный.
        """
        ...

    def isSessionCookie(self) -> bool:
        """
        Проверяет, является ли cookie сессионным.

        :return: True, если сессионный, иначе False.
        """
        ...

    def setSecure(self, enable: bool) -> None:
        """
        Устанавливает флаг безопасности (Secure) для cookie.

        :param enable: True для включения, False для отключения.
        """
        ...

    def isSecure(self) -> bool:
        """
        Проверяет, является ли cookie безопасным (Secure).

        :return: True, если Secure, иначе False.
        """
        ...


class __document(_EventTarget):
    """
    Класс Document

    Класс, содержащий методы для управления заголовком и описанием страницы
    в контексте веб-страницы. Этот класс предназначен для интеграции с браузером
    и управления метаданными страницы.
    """

    def setTitle(self, title: str) -> None:
        """
        Установка заголовка страницы.

        Этот метод устанавливает указанный заголовок для веб-страницы.

        :param title str: Заголовок страницы.
        """
        ...

    def setDescription(self, description: str) -> None:
        """
        ❗☠️ Устаревший метод.❗ Будет полностью удален
        ~~~~
        * (будет удален примерно в версии dw > 1.0.0)
        """



document = __document()
"""
Управление страницей
~~~~~~~~~~~~~~~~~~~~

Класс, содержащий методы для управления заголовком и описанием страницы
в контексте веб-страницы. Этот класс предназначен для интеграции с браузером
и управления метаданными страницы.
"""


class __browser:
    def __init__(self) -> None:
        self.cookieStore = self.__cookieStore()
        """
        Управление хранилищем Cookie
        ~~~~~~~~~~~~~~

        Класс browser.cookieStore предоставляет методы для работы с cookie. Создание, удаление и изменение.
        """

        self.location = self.__location()
        """
        Управление URL
        ~~~~~~~~~~~~~~

        Класс browser.location предоставляет методы для работы с URL страницы, включая получение текущего
        URL и другие операции, связанные с навигацией.
        """

        self.user = self.__user()
        """
        Управление пользователем
        ~~~~~~~~~~

        Класс, предоставляющий методы для работы с текущим пользователем в контексте страницы.
        Этот класс обеспечивает доступ к информации о пользователе, такой как его ID, никнейм и тд.
        Позволяет создавать и упарвлять токенами аутентификации.
        Информация берется из текущего окна и активной сессии пользователя.
        """
    class __cookieStore:
        @_typing.overload
        def setCookie(self, cookie: Cookie) -> None: ...

        @_typing.overload
        def setCookie(self, name: str, value: str) -> None: ...

        @_typing.overload
        def setCookie(self, name: str, value: str, path: str = "") -> None: ...

        def setCookie(self, name_or_cookie: _typing.Union[Cookie, str], value: _typing.Optional[str] = None, path: str = "/") -> None: # type: ignore
            """Сохраняет или обновляет cookie в хранилища"""
            ...

        def getCookie(self, name: str) -> _typing.Optional[Cookie]:
            """Получает cookie из хранилища."""
            ...

        @_typing.overload
        def removeCookie(self, cookie: Cookie) -> None: ...

        @_typing.overload
        def removeCookie(self, name: str) -> None: ...

        def removeCookie(self, name_or_cookie: _typing.Union[Cookie, str]) -> None: # type: ignore
            """Удаляет cookie из хранилища и синхронизирует с QWebEngine."""
            ...
    class __location:
        def currentUrl(self) -> Url:
            """
            Возвращает текущий URL.

            Этот метод возвращает обьект URL, представляющий текущий URL адресной строки.
            Это полезно для получения информации о том, на каком адресе в данный момент
            находится пользователь.

            :return Url: Текущий URL страницы.
            """
            ...
        def currentPageUrl(self) -> Url:
            """
            Возвращает URL страницы.

            Этот метод возвращает обьект URL, представляющий URL веб-страницы.
            Этот метод отличается от currentUrl() в том, он возвращает конкретный начальный url страницы, а не адресную строку.

            :return Url: Текущий URL страницы.
            """
            ...
        def changeUrl(self, url: _typing.Union[Url, str], complete: bool = True) -> None:
            """
            Переходит на новый URL.


            :param url:  новый URL.
            :param complete: Если True, дозаполнит относительный URL на полный URL, если он относительный.
            """
            ...
        def addTab(self, url: _typing.Union[Url, str]) -> None:
            """
            Этот метод добавляет новую вкладку с указанным URL.
            
            :param url: новый URL.
            """
            ...
        def replaceUrl(self, url: _typing.Union[Url, str]) -> None:
            """
            Этот метод заменяет текущий URL на новый.
            
            :param url: новый URL.
            """
            ...
        def reload(self) -> None:
            """
            Этот метод перезагружает текущую веб-страницу.
            """
            ...
        def completeUrl(self, url: _typing.Union[Url, str], originUrl: _typing.Optional[_typing.Union[Url, str]] = None) -> Url:
            """
            Дополняет URL недостающими частями из originUrl или текущего URL.

            Если в URL не хватает схемы или хоста, они будут взяты из originUrl. Если originUrl не указан, 
            используются данные из текущего URL страницы.

            Пример использования:
            ```python
                complete_url = window.location.completeUrl('/some/path')
                # Дополнит схему и хост из текущего URL.

                complete_url = window.location.completeUrl('/some/path', originUrl='https://example.com')
                # Дополнит схему и хост из https://example.com.
            ```

            :param url _typing.Union[Url, str]: URL, который нужно дополнить.
            :param originUrl _typing.Optional[_typing.Union[Url, str]]: URL для дополнения недостающих частей. 
                                                        Если не указан, используется текущий URL.
            :return Url: Дополненный URL.
            """
            ...
    class __user:
        def getUserId(self) -> _typing.Optional[int]:
            """
            Получение ID пользователя.

            Этот метод возвращает идентификатор текущего пользователя, если пользователь аутентифицирован.
            Если пользователь не найден или не аутентифицирован, метод возвращает None.

            :return _typing.Optional[int]: Идентификатор пользователя или None, если пользователь не аутентифицирован.
            """
            ...
        def getNickname(self) -> _typing.Optional[str]:
            """
            Получение никнейма пользователя.

            Этот метод возвращает никнейм (username) текущего пользователя, если пользователь аутентифицирован.
            Если пользователь не найден или не аутентифицирован, метод возвращает None.

            :return _typing.Optional[str]: Никнейм пользователя или None, если пользователь не аутентифицирован.
            """
            ...
        def getToken(self) -> _typing.Optional[str]:
            """
            Получение токена пользователя.

            Этот метод возвращает токен текущего пользователя, если пользователь аутентифицирован.
            Если пользователь не найден или не аутентифицирован, метод возвращает None.

            :return _typing.Optional[str]: Токен пользователя или None, если пользователь не аутентифицирован.
            """
            ...
        def createAuthToken(self) -> _typing.Optional[str]:
            """
            Создает серсисный токен дял пользователя.

            Сервисный токен может быть сохранен на стороне сервера, и использоваться для идентификации пользователя по аккануту MMB.
            Для получения информации по сервисному токену используйте POST 'mmbps://auth.gw/tokens/verify/service' json={'token': token}
            """
            ...
browser = __browser()
"""
Управление хранилищами и поведением браузера
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Класс, содержащий методы для управления браузером, вкладками и хранилищами.
"""




class __Console:
    """
    Класс Console

    Класс, предоставляющий методы для вывода логов и сообщений в консоль.
    Этот класс предназначен для интеграции с браузером и работы с выводом
    сообщений в консоль, аналогично объекту console в JavaScript.
    """

    def log(self, message: _typing.Any) -> None:
        """
        Выводит информационное сообщение в консоль.

        :param message _typing.Any: Сообщение, которое будет выведено в консоль.
        """
        ...

    def warn(self, message: _typing.Any) -> None:
        """
        Выводит предупреждающее сообщение в консоль.

        :param message _typing.Any: Сообщение, которое будет выведено в консоль.
        """
        ...

    def error(self, message: _typing.Any) -> None:
        """
        Выводит сообщение об ошибке в консоль.

        :param message _typing.Any: Сообщение, которое будет выведено в консоль.
        """
        ...

    def info(self, message: _typing.Any) -> None:
        """
        Выводит информационное сообщение в консоль.

        :param message _typing.Any: Сообщение, которое будет выведено в консоль.
        """
        ...
    def getLogs(self, level: _typing.Optional[str] = None) -> _typing.List[dict]:
        """
        Возвращает список логов с указанным уровнем.
        :param level: Уровень логов, по умолчанию None - все уровни.
        :return: Список логов с указанным уровнем.
        """
        ...

    def addLogListener(self, callback: _typing.Callable) -> None:
        """
        Добавляет слушателя для получения логов.
        :param callback: Функция, которая будет вызвана при получении логов.
        """
        ...

console = __Console()

"""
Управление консолью
~~~~~~~~~~~~~~~~~~~~

Класс, предоставляющий методы для вывода логов и сообщений в консоль.
Этот класс предназначен для интеграции с браузером и работы с выводом сообщений в консоль.
"""


class __window(_EventTarget):
    class Event:
        beforeunload = 'beforeunload'
window = __window()
"""
Управление событиями и вкладкой
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Класс представляет собой интерфейс для управления событиями и поведением страницы.
"""




class __fileSystem(_EventTarget):
    """
    Класс Files
    ~~~~~~~~~~~

    Класс, содержащий методы для загрузки файлов с сайтов, а также для загрузки и управления
    библиотеками с сайтов. Класс предназначен для синхронной загрузки данных с удаленных источников.
    """
    def loadAsync(self, url: _typing.Union[Url, str], savePath: str = '/', fileName: _typing.Optional[str] = None, unpack: bool = False, version: str = '0.0.1') -> _typing.Optional[str]:
        """
        Загрузка файла с указанного URL.

        Этот метод загружает файл по указанному URL и возвращает путь к локально сохраненному файлу.

        Usage:
        ```python
            path = await fileSystem.loadAsync('https://example.com/file.txt')
            path = await fileSystem.loadAsync('https://example.com/file.txt', '/site_name/images')
        ```
        :param url str: URL файла, который необходимо загрузить.
        :param savePath str: Необязательный путь для сохранения файла.
                             Если не указан, используется путь из `self.getCurrentFilePath()`.
        :return str: Путь к локально сохраненному файлу, или None, если файл не уладось загрузить.
        """
        ...
    def getCurrentPath(self) -> str:
        """
        Возвращает текущий путь для сохранения файлов.

        Путь не уникален для пользователей!
        Для создания уникальных сохранений исользуйте класс `CookieStore`

        :return str: Текущий путь для сохранения файлов.
        """
        ...
fileSystem = __fileSystem()
"""
управление локальными файлами
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Класс, содержащий методы для загрузки файлов с сайтов, а также для загрузки и управления
библиотеками с сайтов. Класс предназначен для синхронной загрузки данных с удаленных источников.
"""








class __CookieStore:
    """
    Класс CookieStore
    ~~~~~~~~~~~~~~~~~

    Предназначен для хранения и управления заисями Cookie.

    CookieStore уникален для каждого пользователя.
    """
    @_typing.overload
    def setCookie(self, cookie: Cookie) -> None: ...

    @_typing.overload
    def setCookie(self, name: str, value: str) -> None: ...

    @_typing.overload
    def setCookie(self, name: str, value: str, path: str = "/") -> None: ...

    def setCookie(self, name_or_cookie: _typing.Union[Cookie, str], value: _typing.Optional[str] = None, path: str = "/") -> None: # type: ignore
        """Сохраняет или обновляет cookie в LocalVault и синхронизирует с QWebEngine."""
        ...

    def getCookie(self, name: str) -> _typing.Optional[Cookie]:
        """Получает cookie из LocalVault."""
        ...

    @_typing.overload
    def removeCookie(self, cookie: Cookie) -> None: ...

    @_typing.overload
    def removeCookie(self, name: str) -> None: ...

    def removeCookie(self, name_or_cookie: _typing.Union[Cookie, str]) -> None: # type: ignore
        """Удаляет cookie из LocalVault и синхронизирует с QWebEngine."""
        ...
CookieStore = __CookieStore()
"""
❗☠️ Устаревший метод.❗ Новый метод document.cookieStore
~~~~
* (будет удален примерно в версии dw > 0.0.0.1.0)
"""










def fetch(
        method: str,
        url: _typing.Union[Url, str],
        data: _typing.Mapping[str, _typing.Any] | None = None,
        json: dict | None = None,
        cookies: dict = {},
        protocolVersion: _typing.Optional[str] = None,
        **kwargs,
        ) -> 'KeyisBClient.Response':
    """
    Отправляет HTTP-запрос
    ~~~~~~~~~~~~~~~~~~~~~~
    """
    ...

async def fetchAsync(
        method: str,
        url: _typing.Union[Url, str],
        data: _typing.Mapping[str, _typing.Any] | None = None,
        json: dict | None = None,
        cookies: dict = {},
        protocolVersion: _typing.Optional[str] = None,
        **kwargs,
        ) -> 'KeyisBClient.Response':
    """
    Отправляет HTTP-запрос (асинхронно)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    ...


class __widgets:
    class IFrame(_QtWidgets.QWidget):
        """
        Создает контейнер для загрузки url
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        iframe (сокращение от inline frame) является контейнером для внешнего контента. Он позволяет загружать и отображать другие страницы, приложения или виджеты прямо внутри страницы, где был размещен этот элемент.
        

        ```python
        irame = IFrame('https://example.com')
        irame.setFixedSize(400, 200)
        ```

        :param url: URL страницы для загрузки.
        :return: IFrame

        *Не может быть наследован

        *Наследуется от QtWidgets.QWidget

        """
        def __init__(self, url: _typing.Union[Url, str]) -> None:
            ...



widgets = __widgets()

"""
Виджеты
~~~~~~~

Класс, предоставляющий кастомные виджеты.
"""

