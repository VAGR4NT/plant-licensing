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


def query_builder(model, filters):
    ''' 
    model = Django Model class from models.py eg. Businesses, Suppliers, Locations
    filters = A list of dictionaries, where each dict is a filter, field operator and value
                    [{'field': 'locations__city', 'operator': 'iexact', 'value': 'Lexington'}]
    select_columns: A list of field names to select, have whole path
    returns tuple of headers and rows
    '''
    
    allowed_operators = ['exact', 'iexact', 'icontains', 'gt', 'gte', 'lt', 'lte']

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
        return model.objects.filter(combined_filters)
    else:
        return model.objects.all()

def format_table(queryset, select_columns, include_meta=True):
    if not select_columns:
        return {'headers': [], 'rows': []}

    model = queryset.model
    headers = [_validate_and_get_field(model, name).verbose_name.title() for name in select_columns]
    
    pks_and_values = queryset.values_list('pk', *select_columns)

    rows = []
    for item in pks_and_values:
        pk = item[0]
        data = item[1:]
        if include_meta:
            model_name_str = model._meta.model_name
            
            rows.append({
                'id': pk,
                'model_name': model_name_str, # Use the corrected variable
                'data': data
            })
        else:
            rows.append({'data': data})

    return {'headers': headers, 'rows': rows}
