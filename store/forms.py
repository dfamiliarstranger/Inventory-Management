from django import forms
from .models import Cap, Customer, Supplier, StockItem, Production

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
    # preform_type = forms.ModelChoiceField(queryset=Preform.objects.all(), required=True, empty_label="Select")
    class Meta:
        model = StockItem
        fields = '__all__'

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = '__all__'

