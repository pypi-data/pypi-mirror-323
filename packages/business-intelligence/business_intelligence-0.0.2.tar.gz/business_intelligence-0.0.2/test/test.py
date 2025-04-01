import pandas as pd
import business_intelligence as bi


df = './dataset/dataset_food.csv'
df = pd.read_csv(df)

test1 = bi.elasticity.CalculateElasticity(
    data=df, 
    date_col= 'fecha',
    articule_col='cod_art',
    quantity_col= 'kilos',
    sales_col='_ventas')
