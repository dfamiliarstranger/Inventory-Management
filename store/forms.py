from django import forms
from .models import Cap, Customer, Supplier, StockItem, Production, Stock

class CapForm(forms.ModelForm):
    class Meta:
        model = Cap
        fields = ['size', 'quantity_per_bag']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


                    ########## Stock Item Forms ################
class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = '__all__'

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = '__all__'


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'cap_type': forms.Select(attrs={'class': 'form-control'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control'}),
            'bottle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'preform_type': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

