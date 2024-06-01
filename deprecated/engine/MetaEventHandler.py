class MetaEventHandler(type):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class.to_register = []

        for _, attr_value in attrs.items():
            if callable(attr_value) and hasattr(attr_value, "to_register"):
                key = attr_value.to_register
                new_class.to_register.append((key, attr_value))

        return new_class
