import calendar
from datetime import datetime, timedelta
import os
import jinja2
import streamlit as st
import base64
from generate import generate_orders
from holiday import get_holidays
from utils import generate_pdf, split_orders
from logger import log_to_database



def main():
    # 假设你的 HTML 文件的名字是 'template.html'
    html_file_name = "template.html"

    # 获取 HTML 文件的绝对路径
    html_file_path = os.path.realpath(html_file_name)

    # 获取 HTML 文件所在的目录
    html_dir = os.path.dirname(html_file_path)

    # 打开 HTML 文件并读取内容
    with open(html_file_name, "r") as f:
        html = f.read()

    # 将 HTML 中的相对路径更改为绝对路径
    html = html.replace("./images/", "file://" + html_dir + "/images/")

    # 添加用户界面元素到左侧侧边栏
    st.set_page_config(layout="wide")
    sidebar = st.sidebar
    sidebar.title("参数配置")

    start_date, end_date = sidebar.date_input(
        "日期范围",
        help="选择开始和结束日期",
        value=(datetime.today(), datetime.today() + timedelta(days=30)),
    )

    total_amount = sidebar.number_input("总金额", value=1889, min_value=0, step=100)

    start_address = sidebar.text_input("起点地址", value="北京", key="start_address")

    end_address = sidebar.text_input("终点地址", value="上海", key="end_address")

    mileage_range = sidebar.text_input(
        "里程范围（例如：23-25）",
        value="23-25",
        key="mileage_range",
    )

    amount_range = sidebar.text_input(
        "金额范围（例如：60-90）",
        value="60-90",
        key="amount_range",
    )

    city = sidebar.text_input("城市", value="北京市", key="city")

    model = sidebar.text_input("车型", value="车", key="model")

    phone_number = sidebar.text_input("电话号码", value="18088889999", key="phone_number")

    pdf_file_name = sidebar.text_input("文件名", value="行程单", key="pdf_file_name")

    if "instructions_hidden" not in st.session_state:
        st.info("请先在左侧侧边栏设置参数，然后点击“生成订单”按钮。")

    # 处理用户输入
    if sidebar.button("生成订单", key="generate"):
        with st.spinner("正在生成订单，请稍候..."):
            start_time = datetime.now()
            address_info = {
                "start": start_address,
                "end": end_address,
                "mileage": list(map(float, mileage_range.split("-"))),
                "amount": list(map(float, amount_range.split("-"))),
            }

            holidays = [holiday["key"] for holiday in get_holidays(start_date)]

            orders, pre_total_amount, post_total_amount = generate_orders(
                holidays,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                total_amount,
                address_info,
                city,
                model,
            )

            trip_count = len(orders)

            # Split orders into multiple parts
            splitted_orders = split_orders(orders)

            st.header("生成结果")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"申请日期：{datetime.now().strftime('%Y-%m-%d')}")
                st.write(f"开始日期：{start_date.strftime('%Y-%m-%d')}")
                st.write(f"结束日期：{end_date.strftime('%Y-%m-%d')}")

            with col2:
                st.write(f"总记录：{trip_count}")
                st.write(f"调整前的总金额：{pre_total_amount}")
                st.write(f"调整后的总金额：{post_total_amount}")

            # Generate HTML content
            generate_vars = {
                "apply_date": datetime.now().strftime("%Y-%m-%d"),
                "trip_start_date": start_date.strftime("%Y-%m-%d"),
                "trip_end_date": end_date.strftime("%Y-%m-%d"),
                "phone_number": phone_number,
                "trip_count": trip_count,
                "total_amount": total_amount,
            }

            html_content = jinja2.Template(html).render(
                orders=splitted_orders, **generate_vars
            )

            print(html_content)

            # Generate PDF and log to database
            pdf_data = generate_pdf(html_content)

            log_to_database(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_amount": total_amount,
                    "start_address": start_address,
                    "end_address": end_address,
                    "mileage_range": mileage_range,
                    "amount_range": amount_range,
                    "city": city,
                    "model": model,
                    "phone_number": phone_number,
                    "pdf_file_name": pdf_file_name,
                    "generation_time": (datetime.now() - start_time).total_seconds(),
                }
            )

            # Display PDF preview and download link
            st.write(f"### PDF预览")
            b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            st.write(
                f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_file_name}.pdf">点击此处下载PDF文件</a> <iframe src="data:application/pdf;base64,{base64.b64encode(pdf_data).decode("utf-8")}" width="100%" height="600px" style="border: none;"></iframe>',
                unsafe_allow_html=True,
            )

            # Display orders in a table
            for i, order_group in enumerate(splitted_orders):
                st.subheader(f"订单 - 第 {i + 1} 页")
                order_table = []
                order_table.append(
                    ["序号", "车型", "上车时间", "城市", "起点", "终点", "里程[公里]", "金额[元]", "备注"]
                )
                for order in order_group:
                    order_table.append(
                        [
                            order["number"],
                            order["model"],
                            order["start_time"],
                            order["city"],
                            order["start_point"],
                            order["end_point"],
                            order["distance_km"],
                            order["amount_yuan"],
                            order["note"],
                        ]
                    )
                st.table(order_table)


if __name__ == "__main__":
    main()
