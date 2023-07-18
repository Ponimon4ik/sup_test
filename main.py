import json

import pandas as pd

PATH = 'task.json'

with open(PATH, 'r') as file:
    data = json.load(file)

df = pd.DataFrame(data)
df['total_items'] = df['products'].apply(
    lambda products: sum(product['quantity'] for product in products)
)
df['tariff'] = df['highway_cost'].abs() // df['total_items']


tariffs = df.groupby('warehouse_name')['tariff'].mean()
print(tariffs)

product_normalize = pd.json_normalize(data, 'products', ['warehouse_name', 'order_id'])

products = product_normalize.merge(tariffs, on='warehouse_name')


products['income'] = products['price'] * products['quantity']
products['expenses'] = products['tariff'] * products['quantity']
products['profit'] = products['income'] - products['expenses']


products_profit = products.groupby('product').agg({
    'quantity': 'sum',
    'income': 'sum',
    'expenses': 'sum',
    'profit': 'sum',

})
print(products_profit)

order_profit = products.groupby('order_id').agg(order_profit=('profit', 'sum')).reset_index()
print(order_profit)

avg_profit = order_profit['order_profit'].mean()

print('Cредняя прибыль заказов', avg_profit)

table_for_percent = products.groupby(['warehouse_name', 'product']).agg({
    'quantity': 'sum',
    'profit': 'sum',
}).reset_index()

table_for_percent['percent_profit_product_of_warehouse'] = (
    table_for_percent['profit'] /
    table_for_percent.groupby('warehouse_name')['profit'].transform('sum') * 100
)
print(table_for_percent)

table_for_accumulated = table_for_percent.sort_values(
    by=['warehouse_name', 'percent_profit_product_of_warehouse'], ascending=False
)
table_for_accumulated['accumulated_percent_profit_product_of_warehouse'] = table_for_accumulated.groupby(
    'warehouse_name')['percent_profit_product_of_warehouse'].transform('cumsum')

print(table_for_accumulated)


def get_category(accumulated_percent):
    if accumulated_percent <= 70:
        return 'A'
    elif accumulated_percent <= 90:
        return 'B'
    return 'C'


table_for_abc = table_for_accumulated
table_for_abc['category'] = table_for_abc[
    'accumulated_percent_profit_product_of_warehouse'].apply(get_category)

print(table_for_abc)
