from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from .models import Car, Brand
from cars.forms import CarForm
import django_filters
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

FILTERS = (
    ("brand", lambda qs, v: qs.filter(brand_id=v)),
    ("year_min", lambda qs, v: qs.filter(model_year__gte=v)),
    ("year_max", lambda qs, v: qs.filter(model_year__lte=v)),
    ("price_min", lambda qs, v: qs.filter(price__gte=v)),
    ("price_max", lambda qs, v: qs.filter(price__lte=v)),
    ("color", lambda qs, v: qs.filter(color__icontains=v)),
    ("model", lambda qs, v: qs.filter(model__icontains=v)),
)

SORT_OPTIONS = {
    "newest": "-created_at",
    "price_asc": "price",
    "price_desc": "-price",
    "year_desc": "-model_year",
    "year_asc": "model_year",
    "mileage_asc": "mileage",
}

class CarFilter(django_filters.FilterSet):
    year_min = django_filters.NumberFilter(field_name="model_year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="model_year", lookup_expr="lte")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    color = django_filters.CharFilter(field_name="color", lookup_expr="icontains")
    model = django_filters.CharFilter(field_name="model", lookup_expr="icontains")

    class Meta:
        model = Car
        fields = ["brand"]


class CarListView(FilterView, ListView):
    model = Car
    template_name = "cars_list.html"
    context_object_name = "cars"
    paginate_by = 12
    filterset_class = CarFilter

    def get_queryset(self):
        qs = super().get_queryset().filter(is_available=True).select_related("brand")
        sort = self.request.GET.get("sort", "newest")
        if sort in SORT_OPTIONS:
            qs = qs.order_by(SORT_OPTIONS[sort])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["brands"] = Brand.objects.order_by("name")
        ctx["colors"] = (
            Car.objects.filter(is_available=True)
            .values_list("color", flat=True)
            .distinct()
            .order_by("color")
        )
        return ctx
    

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'
    pk_url_kwarg = 'car_id'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return render(request, "404.html", status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
@method_decorator(staff_member_required(login_url='/usuarios/login/'), name='dispatch')
class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'create_car.html'
    success_url = '/carros/'

    def form_valid(self, form):
        form.instance._log_user = self.request.user
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'create_car.html'
    pk_url_kwarg = 'car_id'

    def get_success_url(self):
        return f'/carros/{self.object.pk}/'

    def form_valid(self, form):
        form.instance._log_user = self.request.user
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return render(request, "404.html", status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    

@method_decorator(staff_member_required, name='dispatch')
class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_detail.html'
    pk_url_kwarg = 'car_id'
    success_url = '/carros/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object._log_user = request.user
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)