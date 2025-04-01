from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    PARENT_FIELD_KEY = 'parent_field'

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        request = context.get('request', None)
        fields = []
        relations = []

        if request:
            fields = request.query_params.get('fields', '').split(',')
            relations = request.query_params.get('relations', '').split(',')

            kwargs.pop('expand', None)
            kwargs.pop('fields', None)
            kwargs.pop('relations', None)
            kwargs.pop('params', None)

        super().__init__(*args, **kwargs)

        fields_requested = set(fields) if fields else set()
        relations_requested = set(relations) if relations else set()

        allowed_fields = set(self.get_allowed_fields())
        allowed_relations = set(self.get_allowed_relations())
        fields_requested &= allowed_fields
        relations_requested &= allowed_relations

        if fields_requested or relations_requested:
            # due to how the DRF serialization mechanism works, both fields and relations are treated the same
            allowed = fields_requested.union(relations_requested)

            # gets the last key of each requested field (dot notation) to search in the list of fields in the current serializer
            allowed = {item.split('.')[-1] for item in allowed}

            for field_name in list(self.fields):
                if field_name not in allowed:
                    # if the field wasn't specified in request it is removed from the list of fields to serialize
                    self.fields.pop(field_name)

    def get_allowed_fields(self):
        # required to know if the serializer was called explicitly from the view or
        # if it is a delegation from a parent serializer (parent collection field)
        # - view explicit call -> field_name
        # - parent serializer delegation -> parent_field_name.field_name
        parent_field = self.context.get(self.PARENT_FIELD_KEY, None)

        if parent_field:
            return [f"{parent_field}.{field}" for field in self.fields.keys()]

        return self.fields.keys()

    def get_delegated_allowed_relations(self, allowed_relations):
        # required to know if the serializer was called explicitly from the view or
        # if it is a delegation from a parent serializer (parent collection field)
        # - view explicit call -> field_name
        # - parent serializer delegation -> parent_field_name.field_name
        parent_field = self.context.get(self.PARENT_FIELD_KEY, None)

        if parent_field:
            return [f"{parent_field}.{allowed_relation}" for allowed_relation in allowed_relations]

        return allowed_relations

    def get_allowed_relations(self):
        return []

    def get_expand(self):
        request = self.context.get('request', None)
        str_expand = request.query_params.get('expand', '') if request else None
        if not str_expand:
            return []

        expand = str_expand.split(',')
        parent_field = self.context.get(self.PARENT_FIELD_KEY, None)

        if parent_field:
            # current serializer related expand
            pattern = f'{parent_field}.'
            return [
                field.split(pattern)[1]
                for field in expand
                if pattern in field
            ]

        return expand

    def get_validation_detail(self, code = 0):
        errors = [f'{field}: {str(detail)}'
            for field, details in self.errors.items()
            for detail in details
        ]
        return {'message': 'Validation Failed', 'errors': errors, 'code': code}
