# Validation Engine for Larapak

class Validator:
    def __init__(self, data=None, rules=None):
        self.data = data or {}
        self.rules = rules or {}
        self._errors = {}
        self._validated = {}
        self._has_run = False

    def validate(self):
        if self._has_run:
            return len(self._errors) == 0
        
        self._has_run = True
        for field, rules_str in self.rules.items():
            value = self.data.get(field)
            field_rules = rules_str.split('|')
            
            # Check for required first
            is_required = "required" in field_rules
            if is_required and (value is None or str(value).strip() == ""):
                self._errors[field] = f"Kolom {field} kudu diisi."
                continue
                
            if value is None or str(value).strip() == "":
                # If not required and empty, skip other checks
                continue

            for rule in field_rules:
                if rule == "required":
                    continue
                elif rule == "email":
                    if "@" not in str(value) or "." not in str(value).split("@")[-1]:
                        self._errors[field] = f"Format {field} kudu alamat email sing bener."
                elif rule == "numeric":
                    try:
                        float(value)
                    except ValueError:
                        self._errors[field] = f"Kolom {field} kudu berupa angka."
                elif rule.startswith("min:"):
                    try:
                        min_val = float(rule.split(":")[1])
                        # If numeric, compare values
                        try:
                            num_val = float(value)
                            if num_val < min_val:
                                self._errors[field] = f"Kolom {field} minimal kudu {min_val}."
                        except ValueError:
                            # string length comparison
                            if len(str(value)) < min_val:
                                self._errors[field] = f"Kolom {field} minimal kudu {int(min_val)} karakter."
                    except ValueError:
                        pass
                elif rule.startswith("max:"):
                    try:
                        max_val = float(rule.split(":")[1])
                        try:
                            num_val = float(value)
                            if num_val > max_val:
                                self._errors[field] = f"Kolom {field} maksimal kudu {max_val}."
                        except ValueError:
                            if len(str(value)) > max_val:
                                self._errors[field] = f"Kolom {field} maksimal kudu {int(max_val)} karakter."
                    except ValueError:
                        pass

            if field not in self._errors:
                self._validated[field] = value

        return len(self._errors) == 0

    def gagal(self):
        self.validate()
        return len(self._errors) > 0

    def fails(self):
        return self.gagal()

    def luput(self):
        self.validate()
        return self._errors

    def errors(self):
        return self.luput()

    def valid(self):
        self.validate()
        return self._validated

    def validated(self):
        return self.valid()

    @staticmethod
    def gawe(data, rules):
        return Validator(data, rules)

    @staticmethod
    def make(data, rules):
        return Validator(data, rules)
