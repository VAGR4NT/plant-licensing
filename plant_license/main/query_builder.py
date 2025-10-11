from django.db.models import Q
from functools import reduce
import operator
from django.core.exceptions import FieldDoesNotExist

from .models import Businesses, Suppliers, Locations 

MODEL_MAP = {
    'business': Businesses,
    'supplier': Suppliers,
    'location': Locations,
}

BusinessesConnectionList = []
SuppliersConnectionList = []
LocationsConnectionList = []

def _validate_and_get_field(model, path):
    parts = path.split('__')
    current_model = model
    
    for i, part in enumerate(parts):
        try:
            field = current_model._meta.get_field(part)
            if field.related_model:
                current_model = field.related_model
            elif i == len(parts) - 1:
                return field
        except FieldDoesNotExist:
            raise ValueError(f"'{path}' is not a valid field path for the model {model.__name__}.")
    return field


def query_builder(model, filters, select_columns):
    ''' 
    model = Django Model class from models.py eg. Businesses, Suppliers, Locations
    filters = A list of dictionaries, where each dict is a filter, field operator and value
                    [{'field': 'locations__city', 'operator': 'iexact', 'value': 'Lexington'}]
    select_columns: A list of field names to select, have whole path
    '''
    
    allowed_operators = ['exact', 'iexact', 'icontains', 'gt', 'gte', 'lt', 'lte']

    for col in select_columns:
        _validate_and_get_field(model, col)

    for rule in filters:
        _validate_and_get_field(model, rule['field'])
        if rule['operator'] not in allowed_operators:
            raise ValueError(f"'{rule['operator']}' is not a valid operator.")

    q_objects = []
    if filters:
        for rule in filters:
            lookup = f"{rule['field']}__{rule['operator']}"
            q_objects.append(Q(**{lookup: rule['value']}))
        
        combined_filters = reduce(operator.and_, q_objects)
        queryset = model.objects.filter(combined_filters)
    else:
        queryset = model.objects.all()

    rows = list(queryset.values_list(*select_columns))

    headers = [_validate_and_get_field(model, name).verbose_name.title() for name in select_columns]

    return (headers, rows)
