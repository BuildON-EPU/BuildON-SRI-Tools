from django import forms

class SriForm(forms.Form):
    sri_goal = forms.IntegerField()


class HandleUploadFile(forms.Form):
    csvFile = forms.FileField()
