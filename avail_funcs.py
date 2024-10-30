import json
from db import session_scope, init_db, Items, Orders


init_db()


def show_items():
    """Возвращает список всех доступных товаров в магазине.

    Returns:
        list[dict]: Список товаров, где каждый товар представлен словарем:
            {
                "id": int,        # Уникальный идентификатор товара
                "name": str,      # Название товара
                "quantity": int,   # Доступное количество
                "price": int       # Цена товара
            }

    Raises:
        Exception: При ошибке подключения к базе данных
    
    Example:
         show_items()
        [
            {"id": 1, "name": "Ноутбук", "quantity": 5, "price": 10000},
            {"id": 2, "name": "Смартфон", "quantity": 10, "price": 5000 }
        ]
    """
    try:
        with session_scope() as session:
            items = session.query(Items).all()
            result = [{"id": item.id, "name": item.name, "quantity": item.quantity, "price": item.price} 
                     for item in items]
            if not result:
                print("Предупреждение: В магазине нет доступных товаров")
            return result
    except Exception as e:
        raise Exception(f"Ошибка при получении списка товаров: {str(e)}")


def create_order(username: str, item_id: int, quantity: int):
    """Создание нового заказа.

    Args:
        username (str): Имя пользователя, создающего заказ
        item_id (int): Идентификатор заказываемого товара
        quantity (int): Количество товара для заказа

    Returns:
        dict: Информация о созданном заказе:
            {
                "order_id": int,  # Уникальный идентификатор заказа
                "username": str,  # Имя пользователя
                "item_id": int,   # Идентификатор товара
                "quantity": int   # Количество товара в заказе
            }

    Raises:
        ValueError: 
            - Если товар с указанным ID не найден
            - Если запрошенное количество превышает доступное
            - Если username пустой или quantity <= 0
        Exception: При ошибках работы с базой данных

    Example:
         create_order("user123", 1, 2)
        {
            "order_id": 1,
            "username": "user123",
            "item_id": 1,
            "quantity": 2
        }
    """
    if not username or not username.strip():
        raise ValueError("Имя пользователя не может быть пустым")
    
    if quantity <= 0:
        raise ValueError("Количество товара должно быть положительным числом")

    # Проверка наличия товара и количества
    items = show_items()
    item = next((item for item in items if item["id"] == item_id), None)
    
    if not item:
        raise ValueError(f"Товар с ID {item_id} не найден")
        
    if quantity > item["quantity"]:
        raise ValueError(f"Недостаточно товара. Доступно: {item['quantity']}, запрошено: {quantity}")

    try:
        with session_scope() as session:
            # Создаем заказ
            order = Orders(username=username, item_id=item_id, quantity=quantity)
            session.add(order)
            
            # Обновляем количество доступного товара
            item_db = session.query(Items).filter_by(id=item_id).first()
            item_db.quantity -= quantity
            
            # Чтобы получить order_id, нужно сделать flush
            session.flush()
            
            return {
                "order_id": order.id,
                "username": order.username,
                "item_id": order.item_id,
                "quantity": order.quantity
            }
            
    except Exception as e:
        raise Exception(f"Ошибка при создании заказа: {str(e)}")

def find_order(username: str, item_id: int):
    """Поиск заказа по имени пользователя и идентификатору товара.

    Args:
        username (str): Имя пользователя, сделавшего заказ
        item_id (int): Идентификатор заказанного товара

    Returns:
        dict | None: Информация о заказе в виде словаря:
            {
                "order_id": int,  # Уникальный идентификатор заказа
                "username": str,  # Имя пользователя
                "item_id": int,   # Идентификатор товара
                "quantity": int   # Количество товара в заказе
            }
        None: если заказ не найден

    Raises:
        Exception: При ошибке подключения к базе данных

    Example:
         find_order("user123", 1)
        {
            "order_id": 1,
            "username": "user123",
            "item_id": 1,
            "quantity": 2
        }
    """
    try:
        with session_scope() as session:
            order = session.query(Orders).filter_by(username=username, item_id=item_id).first()
            if order:
                return {
                    "order_id": order.id,
                    "username": order.username,
                    "item_id": order.item_id,
                    "quantity": order.quantity
                }
        return None
    except Exception as e:
        raise Exception(f"Ошибка при поиске заказа: {str(e)}")


def cancel_order(order_id: int, quantity: int):
    """Отмена заказа полностью или частично.

    Args:
        order_id (int): Идентификатор заказа для отмены
        quantity (int): Количество товара для отмены

    Returns:
        int: 
            - число оставшихся товаров в заказе > 0: если заказ частично отменен
            - 0: если заказ полностью отменен и удален

    Raises:
        ValueError: 
            - Если заказ с указанным ID не найден
            - Если количество для отмены больше, чем в заказе
        Exception: При других ошибках работы с базой данных

    Example:
         cancel_order(1, 2)  # Отмена 2 единиц товара из заказа
        1  # Заказ остался, но количество уменьшилось до одного
         cancel_order(1, 5)  # Отмена всех оставшихся единиц
        0  # Заказ полностью удален - не осталось товаров в заказе
    """
    try:
        with session_scope() as session:
            # Находим заказ
            order = session.query(Orders).filter_by(id=order_id).first()
            if not order:
                raise ValueError(f"Заказ с ID {order_id} не найден")
            
            if quantity > order.quantity:
                raise ValueError(f"Нельзя отменить больше товаров, чем в заказе")
            
            # Находим товар для обновления количества
            item = session.query(Items).filter_by(id=order.item_id).first()
            if not item:
                raise ValueError(f"Товар с ID {order.item_id} не найден")
            
            # Возвращаем товары на склад
            item.quantity += quantity
            
            # Обновляем или удаляем заказ
            new_quantity = order.quantity - quantity
            if new_quantity > 0:
                order.quantity = new_quantity
                return new_quantity
            else:
                session.delete(order)
                return new_quantity
                
    except Exception as e:
        raise Exception(f"Ошибка при отмене заказа: {str(e)}")


tools = [show_items, create_order, find_order, cancel_order]

#выполняет функцию из списка функций, которые доступны боту. возвращает рез-т выполнения функции
def execute_tool_call(tool_call, tools_map, agent_name):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"{agent_name}: {name}({args})")

    # call corresponding function with provided arguments
    return tools_map[name](**args)