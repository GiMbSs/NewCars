from django.db import models

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, blank=False, null=False, verbose_name='Nome da Marca')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

class Car(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100, blank=False, null=False, verbose_name='Modelo')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='brands', verbose_name='Marca')
    factory_year = models.PositiveIntegerField(blank=False, null=False, verbose_name='Ano de Fabricação')
    model_year = models.PositiveIntegerField(blank=False, null=False, verbose_name='Ano do Modelo')
    color = models.CharField(max_length=50, blank=False, null=False, verbose_name='Cor')
    transmission = models.CharField(max_length=50, default='Manual', blank=False, null=False, verbose_name='Transmissão')
    mileage = models.PositiveIntegerField(blank=True, null=False, verbose_name='Quilometragem')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, verbose_name='Preço')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    is_new = models.BooleanField(default=False, verbose_name='Zero KM')
    is_available = models.BooleanField(default=True, verbose_name='Disponível')
    highlighted = models.BooleanField(default=False, verbose_name='Destaque')
    image = models.ImageField(upload_to='car_images/', blank=True, null=True, verbose_name='Imagem')

    def __str__(self):
        return f'[{self.id}]{self.brand} {self.model} ({self.model_year})'
    
    class Meta:
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'