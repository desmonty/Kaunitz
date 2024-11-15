import pandas as pd

class Holdings:
    def __init__(self):
        self._holdings = pd.DataFrame(columns=['asset', 'quantity'])
        
    def add(self, asset: str, quantity: int):
        assert quantity > 0, f"Quantity must be a strictly positive number, not {quantity}"
        if asset in self._holdings['asset'].values:
            # Increase the quantity of the existing asset
            self._holdings.loc[self._holdings['asset'] == asset, 'quantity'] += quantity
        else:
            # Add a new asset with the given quantity
            new_row = pd.DataFrame({'asset': [asset], 'quantity': [quantity]})
            self._holdings = pd.concat([self._holdings, new_row], ignore_index=True)
        
    def remove(self, asset: str, quantity: int):
        assert quantity > 0, f"Quantity must be a strictly positive number, not {quantity}"
        if asset in self._holdings['asset'].values:
            current_quantity = self._holdings.loc[self._holdings['asset'] == asset, 'quantity'].iloc[0]
            if quantity <= current_quantity:
                new_quantity = current_quantity - quantity
                if new_quantity > 0:
                    # Update the quantity
                    self._holdings.loc[self._holdings['asset'] == asset, 'quantity'] = new_quantity
                else:
                    # Remove the asset from holdings if quantity is zero
                    self._holdings = self._holdings[self._holdings['asset'] != asset]
            else:
                raise ValueError(f"Cannot remove {quantity} of '{asset}', only {current_quantity} available.")
        else:
            raise KeyError(f"Asset '{asset}' not found in holdings.")
    
    def state(self):
        return self._holdings.copy()
