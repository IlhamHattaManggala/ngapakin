# Error system definitions for NgapakIn

class NgapakError(Exception):
    def __init__(self, message, line=None, column=None, filename=None):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename

    def __str__(self):
        parts = []
        if self.filename:
            parts.append(f"Berkas '{self.filename}'")
        if self.line is not None:
            parts.append(f"baris {self.line}")
        if self.column is not None:
            parts.append(f"kolom {self.column}")
        
        prefix = f"Error pada {', '.join(parts)}" if parts else "Error"
        return f"{prefix}: {self.message}"

class NgapakSyntaxError(NgapakError):
    """Errors encountered during lexing or parsing."""
    pass

class NgapakRuntimeError(NgapakError):
    """Errors encountered during AST evaluation/interpretation."""
    pass
