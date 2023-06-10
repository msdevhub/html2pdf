from datetime import datetime, timedelta
from decimal import Decimal
import random

def create_order_item(number, model, start_time, city, start_point, end_point, distance_km, amount_yuan, note=""):
    return {
        "number": number,
        "model": model,
        "start_time": start_time,
        "city": city,
        "start_point": start_point,
        "end_point": end_point,
        "distance_km": distance_km,
        "amount_yuan": amount_yuan,
        "note": note
    }

weekday_map = {
    0: "一",
    1: "二",
    2: "三",
    3: "四",
    4: "五"
}

def generate_daily_orders(start_date, address_info, city, model, daily_amount):
    orders = []
    weekday = weekday_map[start_date.weekday()]

    def generate_item(start_time, start_point, end_point):
        mileage = round(random.uniform(address_info["mileage"][0], address_info["mileage"][1]), 1)
        amount = daily_amount * mileage / sum(address_info["mileage"]) * 2
        order = create_order_item(len(orders) + 1, model, start_time, city, start_point, end_point, mileage, amount)
        orders.append(order)

    def create_start_time(start, random_minutes):
        return (datetime.strptime(start_date.strftime("%Y-%m-%d") + " " + start, "%Y-%m-%d %H:%M") + timedelta(minutes=random_minutes)).strftime("%H:%M")

    morning_start_time = create_start_time("08:30", random.randint(0, 60))
    generate_item(start_date.strftime("%m-%d") + " " + morning_start_time + " 周" + weekday, address_info["start"], address_info["end"])

    evening_start_time = create_start_time("18:00", random.randint(0, 120))
    generate_item(start_date.strftime("%m-%d") + " " + evening_start_time + " 周" + weekday, address_info["end"], address_info["start"])

    return orders


def generate_orders(holidays, start_date, end_date, total_amount, address_info, city, model):
    orders = []
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    total_days = (end_date - start_date).days + 1  # 计算总的天数
    total_workdays = sum(1 for _ in range(total_days) if (start_date + timedelta(days=_)).weekday() < 5)  # 计算工作日天数
    daily_amount = total_amount / (total_workdays * 2)  # 每天有两条记录

    while start_date <= end_date:
        # 如果不是周六周日，并且日期不在节假日列表中
        if start_date.weekday() < 5 and start_date.strftime("%Y.%m.%d") not in holidays:
            daily_orders = generate_daily_orders(start_date, address_info, city, model, daily_amount)
            orders.extend(daily_orders)

        start_date += timedelta(days=1)

    # 调整金额使得总金额等于预算金额
    current_total_amount = sum(order['amount_yuan'] for order in orders)
    adjustment_ratio = total_amount / current_total_amount

    for order in orders:
        order['amount_yuan'] = Decimal(order['amount_yuan'] * adjustment_ratio).quantize(Decimal("0.00")) #round(order['amount_yuan'] * adjustment_ratio, 2)

    current_total_amount = sum(order['amount_yuan'] for order in orders)
    return orders, current_total_amount, total_amount
