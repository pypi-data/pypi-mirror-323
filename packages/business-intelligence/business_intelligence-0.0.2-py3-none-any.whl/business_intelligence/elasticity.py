import pandas as pd

class Elasticity:
    def __init__(self, data,date_col,articule_cod_col, quantity_col, sales_col):
        self.data = data
        self.date = date_col
        self.articule = articule_cod_col
        self.price_col = sales_col
        self.quantity_col = quantity_col

    def calculate_elasticity(self, cod_art=None, q_range=5):
        """
        Calculate the price elasticity of demand.
        """
        # Select the columns of interest
        required_columns = [self.date,self.articule,self.price_col, self.quantity_col]
        for col in required_columns:
            if col not in self.data.columns: 
                raise ValueError(f'La columna {col} no se encuentra en el dataframe')
        self.data = self.data[required_columns]

        # Filter the data by the articule
        if cod_art is not None:
            self.data = self.data[self.data[self.articule] == cod_art]
            if self.data.empty:
                raise ValueError(f'No se encontro el articulo cod {cod_art}')

        # Convertir las columnas a tipo numerico 
        self.data[self.price_col] = pd.to_numeric(self.data[self.price_col], errors='coerce')
        self.data[self.quantity_col] = pd.to_numeric(self.data[self.quantity_col], errors='coerce')

        # Eliminar filas con nan en columnas clave
        self.data.dropna(subset=[self.price_col, self.quantity_col], inplace=True)

        # create a new column for the single price
        self.data['single_price'] = (self.data[self.price_col] / self.data[self.quantity_col]).round(0)

        # remove the rows with zero price or quantity
        self.data = self.data[(self.data['single_price'] > 0) & (self.data[self.quantity_col] > 0)]

        # Calculate the total 
        prices_unique = self.data['single_price'].sort_values(ascending=True).unique()
        demand = []
        for price in prices_unique:
            demand.append(self.data[self.data['single_price'] == price][self.quantity_col].sum())

        # Discritize the singel prices
        ranges = pd.DataFrame({'single_price':prices_unique})
        ranges = pd.qcut(ranges['single_price'], q=q_range).unique()
        
        # Create a table with the demand for each price range
        table = pd.DataFrame({'single_price':prices_unique, 'demand':demand})
        for range in ranges:
            for index, row in table.iterrows():
                if row['single_price'] in range:
                    table.loc[index, 'range_price'] = range
        table = table.groupby('range_price').agg({'demand':'sum'}).reset_index() 

        # Calculate the elasticity of demand for each price range
        table['single_price'] = table['range_price'].apply(lambda x: x.mid).round(0)
        table = table[['range_price','single_price','demand']]
        table['var_single_price'] = table['single_price'].pct_change()
        table['var_demand'] = table['demand'].pct_change()
        table['elasticity'] = (table['var_demand'] / table['var_single_price']).abs()

        table = pd.DataFrame(table)

        return table
