from django import forms

class UploadPlanilhaForm(forms.Form):
    arquivo = forms.FileField(label="Selecione a planilha diária (.xlsx ou .csv)")