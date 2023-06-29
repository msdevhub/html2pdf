from datetime import datetime, timedelta
from decimal import Decimal
import random

WEEKDAY_MAP = {
    0: "一",
    1: "二",
    2: "三",
    3: "四",
    4: "五"
}

def create_start_time(start_date, start, random_minutes):
    """
    创建随机的起始时间
    """
    return (datetime.strptime(start_date.strftime("%Y-%m-%d") + " " + start, "%Y-%m-%d %H:%M") + timedelta(minutes=random_minutes)).strftime("%H:%M")

def generate_order_item(number, model, start_time, city, start_point, end_point, mileage_range, daily_amount):
    """
    生成订单项
    """
    mileage = round(random.uniform(mileage_range[0], mileage_range[1]), 1)
    peak_charge = calculate_peak_charge(start_time.split(' ')[1])  # calculate peak charge based on start time
    amount = daily_amount * mileage / (sum(mileage_range) / 2) * peak_charge  # apply peak charge to amount
    order = {
        "number": number,
        "model": model,
        "start_time": start_time,
        "city": city,
        "start_point": start_point,
        "end_point": end_point,
        "distance_km": mileage,
        "amount_yuan": amount,
        "note": "",
    }
    print(order)
    return order


def calculate_peak_charge(start_time):
    hour = int(start_time.split(':')[0])
    if (hour >= 7 and hour <= 9) or (hour >= 17 and hour <= 19):
        print("Peak charge applied ", start_time)
        return 1.2
    else:
        return 1.0


def generate_daily_orders(start_date, address_info, city, model, daily_amount):
    """
    生成每天的上下班记录
    """
    orders = []
    weekday = WEEKDAY_MAP[start_date.weekday()]

    morning_start_time = create_start_time(start_date, "06:40", random.randint(0, 60))
    morning_order = generate_order_item(
        len(orders) + 1,
        model,
        start_date.strftime("%m-%d") + " " + morning_start_time + " 周" + weekday,
        city,
        address_info["start"],
        address_info["end"],
        address_info["mileage"],
        daily_amount
    )
    orders.append(morning_order)

    evening_start_time = create_start_time(start_date, "18:00", random.randint(0, 120))
    evening_order = generate_order_item(
        len(orders) + 1,
        model,
        start_date.strftime("%m-%d") + " " + evening_start_time + " 周" + weekday,
        city,
        address_info["end"],
        address_info["start"],
        address_info["mileage"],
        daily_amount
    )
    orders.append(evening_order)

    return orders

def calculate_adjusted_amounts(total_amount, amounts):
    """
    计算调整后的金额列表，使得总金额等于预算金额
    """
    total_amount_generated = sum(amounts)
    adjustment_ratio = total_amount / total_amount_generated
    adjusted_amounts = [Decimal(amount * adjustment_ratio).quantize(Decimal("0.00")) for amount in amounts]
    current_total_amount = round(sum(adjusted_amounts), 2)

    # Check if the sum of adjusted amounts equals to total_amount (round to 2 decimal places)
    if current_total_amount != round(total_amount, 2):
        # Find the difference
        diff = round(Decimal(total_amount), 2) - current_total_amount
        # Randomly select a record to adjust
        adjusted_amounts[random.randint(0, len(adjusted_amounts) - 1)] += diff

    return adjusted_amounts


def generate_orders(holidays, start_date, end_date, total_amount, address_info, city, model):
    """
    生成订单
    """
    orders = []
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    daily_amount = total_amount / ((end_date - start_date).days + 1) 

    while start_date <= end_date:
        if start_date.weekday() < 5 and start_date.strftime("%Y.%m.%d") not in holidays:
            daily_orders = generate_daily_orders(start_date, address_info, city, model, daily_amount)
            orders.extend(daily_orders)

        start_date += timedelta(days=1)

    # Adjust the amount to match the total amount
    amounts = [order['amount_yuan'] for order in orders]
    adjusted_amounts = calculate_adjusted_amounts(total_amount, amounts)

    for index, (order, amount) in enumerate(zip(orders, adjusted_amounts)):
        order['amount_yuan'] = amount
        # update number
        order['number'] = index+1

    current_total_amount = sum(order['amount_yuan'] for order in orders)

    return orders, current_total_amount, total_amount
