# Netbox plugin 'IS Risks'

Добавляет:
- в Netbox объект "Risk"
- в карточки объектов virtual machine, device секцию "Risks"

Позволяет связывать активы с рисками ИБ и недопустимыми событиями.

## Установка

1. Установить плагин `pip3 install netbox-is-risks`
2. Добавить плагин в `netbox/netbox/netbox/configuration.py` (обновить или добавить переменную):

```
PLUGINS=['risks']
```

3. Перейти в каталог с файлом `manage.py` и выполнить миграцию БД `python3 manage.py migrate`
4. Перезапустить сервер netbox
5. Проверить, что плагин появился в списке установленных плагинов в административном интерфейсе Django.

