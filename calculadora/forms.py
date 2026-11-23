from django import forms


UNIDADES = [
    ("h", "por hora"),
    ("min", "por minuto"),
    ("d", "por día"),
]

BASE_COSTO = [
    ("L", "sobre L (tiempo en el sistema)"),
    ("Lq", "sobre Lq (solo tiempo en cola)"),
]


class FormMM1(forms.Form):
    lam = forms.FloatField(
        label="Tasa de llegada (λ)", min_value=0.0001,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    mu = forms.FloatField(
        label="Tasa de servicio (μ)", min_value=0.0001,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    unidad = forms.ChoiceField(label="Unidad de tiempo", choices=UNIDADES, initial="h")
    n_max = forms.IntegerField(
        label="N máximo para distribución", min_value=1, max_value=50, initial=10,
    )

    def clean(self):
        datos = super().clean()
        lam, mu = datos.get("lam"), datos.get("mu")
        if lam is not None and mu is not None and lam >= mu:
            raise forms.ValidationError(
                f"El sistema no es estable: λ ({lam:g}) es mayor o igual que μ ({mu:g}). "
                "La cola crecería indefinidamente. Aumente μ o reduzca λ."
            )
        return datos


class FormMMs(forms.Form):
    lam = forms.FloatField(
        label="Tasa de llegada (λ)", min_value=0.0001,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    mu = forms.FloatField(
        label="Tasa de servicio por servidor (μ)", min_value=0.0001,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    s = forms.IntegerField(label="Número de servidores (s)", min_value=1)
    unidad = forms.ChoiceField(label="Unidad de tiempo", choices=UNIDADES, initial="h")
    n_max = forms.IntegerField(
        label="N máximo para distribución", min_value=1, max_value=50, initial=10,
    )

    def clean(self):
        datos = super().clean()
        lam, mu, s = datos.get("lam"), datos.get("mu"), datos.get("s")
        if lam is not None and mu is not None and s is not None and lam >= s * mu:
            raise forms.ValidationError(
                f"El sistema no es estable: λ ({lam:g}) es mayor o igual que s·μ ({s * mu:g}). "
                "La cola crecería indefinidamente. Aumente s o μ."
            )
        return datos


class FormCostos(forms.Form):
    lam = forms.FloatField(
        label="Tasa de llegada (λ)", min_value=0.0001,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    mu = forms.FloatField(
        label="Tasa de servicio por servidor (μ)", min_value=0.0001,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    cs = forms.FloatField(
        label="Costo por servidor por unidad de tiempo (Cs)", min_value=0,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    cw = forms.FloatField(
        label="Costo de espera por cliente por unidad de tiempo (Cw)", min_value=0,
        widget=forms.NumberInput(attrs={"step": "any"}),
    )
    s_max = forms.IntegerField(label="Número máximo de servidores a evaluar", min_value=1)
    unidad = forms.ChoiceField(label="Unidad de tiempo", choices=UNIDADES, initial="h")
    base = forms.ChoiceField(label="Base del costo de espera", choices=BASE_COSTO, initial="L")
    moneda = forms.CharField(label="Moneda", max_length=6, initial="COP")
