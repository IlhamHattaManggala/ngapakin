# Base ORM Model for Larapak (Eloquent-like)
# Supports CRUD, Relationships, and Eager Loading (N+1 Elimination)

from .database import db_manager
from .query_builder import QueryBuilder
from ngapak.vm import NgapakClass, NgapakInstance

class RelationMetadata:
    """Descriptor storing metadata about a defined relationship."""
    def __init__(self, rel_type, related_class_name, foreign_key, owner_or_local_key):
        self.rel_type = rel_type  # 'hasOne', 'hasMany', 'belongsTo'
        self.related_class_name = related_class_name
        self.foreign_key = foreign_key
        self.owner_or_local_key = owner_or_local_key

    def __repr__(self):
        return f"<RelationMetadata {self.rel_type} -> {self.related_class_name} (fk={self.foreign_key}, key={self.owner_or_local_key})>"


class Model:
    active_vm = None
    tabel = None
    fillable = []

    @classmethod
    def get_table_name(cls, class_obj):
        if isinstance(class_obj, NgapakClass):
            return class_obj.attributes.get("tabel", f"{class_obj.name.lower()}s")
        return getattr(class_obj, "tabel", f"{class_obj.__name__.lower()}s")

    @classmethod
    def get_fillable(cls, class_obj):
        if isinstance(class_obj, NgapakClass):
            return class_obj.attributes.get("fillable", [])
        return getattr(class_obj, "fillable", [])

    @classmethod
    def kabeh(cls):
        table = Model.get_table_name(cls)
        qb = ModelQueryBuilder(cls, table)
        return qb.kabeh()

    @classmethod
    def all(cls):
        return cls.kabeh()

    @classmethod
    def golek(cls, record_id):
        table = Model.get_table_name(cls)
        row = QueryBuilder(table).nek("id", "=", record_id).golek()
        if not row:
            return None

        instance = cls() if isinstance(cls, NgapakClass) else cls.__new__(cls)
        if isinstance(instance, NgapakInstance):
            instance.fields.update(row)
        else:
            instance.__dict__.update(row)
        instance._relations = {}
        return instance

    @classmethod
    def find(cls, record_id):
        return cls.golek(record_id)

    @classmethod
    def gawe(cls, data):
        table = Model.get_table_name(cls)
        fillable = Model.get_fillable(cls)

        filtered_data = {}
        if fillable:
            for k, v in data.items():
                if k in fillable:
                    filtered_data[k] = v
        else:
            filtered_data = data

        record_id = QueryBuilder(table).tambah(filtered_data)
        return Model.golek.__func__(cls, record_id)

    @classmethod
    def create(cls, data):
        return cls.gawe(data)

    @classmethod
    def nek(cls, kolom, op, nilai=None):
        table = Model.get_table_name(cls)
        qb = ModelQueryBuilder(cls, table)
        return qb.nek(kolom, op, nilai)

    @classmethod
    def where(cls, kolom, op, nilai=None):
        return cls.nek(kolom, op, nilai)

    @classmethod
    def with_(cls, *relations):
        """Eager load relationships to eliminate N+1 queries."""
        table = Model.get_table_name(cls)
        qb = ModelQueryBuilder(cls, table)
        return qb.with_(*relations)

    @classmethod
    def with_related(cls, *relations):
        return cls.with_(*relations)

    @classmethod
    def kaca(cls, saben_kaca=15, kaca_saiki=1):
        table = Model.get_table_name(cls)
        qb = ModelQueryBuilder(cls, table)
        return qb.kaca(saben_kaca, kaca_saiki)

    @classmethod
    def paginate(cls, per_page=15, page=1):
        return cls.kaca(per_page, page)

    @classmethod
    def lewati(cls, jumlah):
        table = Model.get_table_name(cls)
        qb = ModelQueryBuilder(cls, table)
        return qb.lewati(jumlah)

    @classmethod
    def offset(cls, jumlah):
        return cls.lewati(jumlah)

    @classmethod
    def ambil(cls, jumlah):
        table = Model.get_table_name(cls)
        qb = ModelQueryBuilder(cls, table)
        return qb.ambil(jumlah)

    @classmethod
    def limit(cls, jumlah):
        return cls.ambil(jumlah)

    # Instance Methods
    def simpen(self):
        cls = self.ngapak_class if isinstance(self, NgapakInstance) else self.__class__
        table = Model.get_table_name(cls)
        fields = self.fields if isinstance(self, NgapakInstance) else self.__dict__

        # Filter out internal private attributes
        db_fields = {k: v for k, v in fields.items() if not k.startswith("_")}

        if "id" in db_fields and db_fields["id"] is not None:
            QueryBuilder(table).nek("id", "=", db_fields["id"]).anyari(db_fields)
        else:
            record_id = QueryBuilder(table).tambah(db_fields)
            fields["id"] = record_id
        return self

    def save(self):
        return self.simpen()

    def busak(self):
        cls = self.ngapak_class if isinstance(self, NgapakInstance) else self.__class__
        table = Model.get_table_name(cls)
        fields = self.fields if isinstance(self, NgapakInstance) else self.__dict__

        if "id" in fields and fields["id"] is not None:
            QueryBuilder(table).nek("id", "=", fields["id"]).busak()
            fields["id"] = None
        return self

    def delete(self):
        return self.busak()

    # Relationship Methods
    def hasOne(self, related_class_name, foreign_key=None, local_key="id"):
        cls = self.ngapak_class if isinstance(self, NgapakInstance) else self.__class__
        if foreign_key is None:
            foreign_key = f"{cls.name.lower() if hasattr(cls, 'name') else cls.__name__.lower()}_id"

        # If in eager inspection mode, return metadata without executing query
        if getattr(self, "_eager_inspect", False):
            return RelationMetadata("hasOne", related_class_name, foreign_key, local_key)

        # Return preloaded relation if already eager loaded
        relations = getattr(self, "_relations", {})
        if related_class_name in relations:
            return relations[related_class_name]

        if not Model.active_vm:
            return None

        related_class = Model.active_vm.globals.get(related_class_name)
        if not related_class:
            raise ValueError(f"Model '{related_class_name}' tidak ditemukan di VM globals.")

        related_table = Model.get_table_name(related_class)
        fields = self.fields if isinstance(self, NgapakInstance) else self.__dict__
        local_val = fields.get(local_key)

        row = QueryBuilder(related_table).nek(foreign_key, "=", local_val).golek()
        if not row:
            return None

        instance = related_class() if isinstance(related_class, NgapakClass) else related_class.__new__(related_class)
        if isinstance(instance, NgapakInstance):
            instance.fields.update(row)
        else:
            instance.__dict__.update(row)
        instance._relations = {}
        return instance

    def hasMany(self, related_class_name, foreign_key=None, local_key="id"):
        cls = self.ngapak_class if isinstance(self, NgapakInstance) else self.__class__
        if foreign_key is None:
            foreign_key = f"{cls.name.lower() if hasattr(cls, 'name') else cls.__name__.lower()}_id"

        # If in eager inspection mode, return metadata without executing query
        if getattr(self, "_eager_inspect", False):
            return RelationMetadata("hasMany", related_class_name, foreign_key, local_key)

        # Return preloaded relation if already eager loaded
        relations = getattr(self, "_relations", {})
        if related_class_name in relations:
            return relations[related_class_name]

        if not Model.active_vm:
            return []

        related_class = Model.active_vm.globals.get(related_class_name)
        if not related_class:
            raise ValueError(f"Model '{related_class_name}' tidak ditemukan di VM globals.")

        related_table = Model.get_table_name(related_class)
        fields = self.fields if isinstance(self, NgapakInstance) else self.__dict__
        local_val = fields.get(local_key)

        rows = QueryBuilder(related_table).nek(foreign_key, "=", local_val).kabeh()
        instances = []
        for row in rows:
            instance = related_class() if isinstance(related_class, NgapakClass) else related_class.__new__(related_class)
            if isinstance(instance, NgapakInstance):
                instance.fields.update(row)
            else:
                instance.__dict__.update(row)
            instance._relations = {}
            instances.append(instance)
        return instances

    def belongsTo(self, related_class_name, foreign_key=None, owner_key="id"):
        if foreign_key is None:
            foreign_key = f"{related_class_name.lower()}_id"

        # If in eager inspection mode, return metadata without executing query
        if getattr(self, "_eager_inspect", False):
            return RelationMetadata("belongsTo", related_class_name, foreign_key, owner_key)

        # Return preloaded relation if already eager loaded
        relations = getattr(self, "_relations", {})
        if related_class_name in relations:
            return relations[related_class_name]

        if not Model.active_vm:
            return None

        related_class = Model.active_vm.globals.get(related_class_name)
        if not related_class:
            raise ValueError(f"Model '{related_class_name}' tidak ditemukan di VM globals.")

        related_table = Model.get_table_name(related_class)
        fields = self.fields if isinstance(self, NgapakInstance) else self.__dict__
        foreign_val = fields.get(foreign_key)

        row = QueryBuilder(related_table).nek(owner_key, "=", foreign_val).golek()
        if not row:
            return None

        instance = related_class() if isinstance(related_class, NgapakClass) else related_class.__new__(related_class)
        if isinstance(instance, NgapakInstance):
            instance.fields.update(row)
        else:
            instance.__dict__.update(row)
        instance._relations = {}
        return instance


class ModelQueryBuilder(QueryBuilder):
    def __init__(self, cls, table):
        super().__init__(table)
        self.cls = cls
        self._eager_relations = []

    def with_(self, *relations):
        for r in relations:
            if isinstance(r, (list, tuple)):
                self._eager_relations.extend(r)
            else:
                self._eager_relations.append(r)
        return self

    def with_related(self, *relations):
        return self.with_(*relations)

    def siji(self):
        instances = self.kabeh()
        return instances[0] if instances else None

    def first(self):
        return self.siji()

    def kabeh(self):
        rows = super().kabeh()
        instances = []
        for row in rows:
            instance = self.cls() if isinstance(self.cls, NgapakClass) else self.cls.__new__(self.cls)
            if isinstance(instance, NgapakInstance):
                instance.fields.update(row)
            else:
                instance.__dict__.update(row)
            instance._relations = {}
            instances.append(instance)

        if instances and self._eager_relations:
            self._load_eager_relations(instances)

        return instances

    def all(self):
        return self.kabeh()

    def kaca(self, saben_kaca=15, kaca_saiki=1):
        saben_kaca = max(1, int(saben_kaca or 15))
        kaca_saiki = max(1, int(kaca_saiki or 1))

        total = self.count()
        kaca_pungkasan = max(1, (total + saben_kaca - 1) // saben_kaca)

        self.ambil(saben_kaca).lewati((kaca_saiki - 1) * saben_kaca)
        instances = self.kabeh()

        return {
            "data": instances,
            "total": total,
            "saben_kaca": saben_kaca,
            "kaca_saiki": kaca_saiki,
            "kaca_pungkasan": kaca_pungkasan,
            "ana_sadurunge": kaca_saiki > 1,
            "ana_sabanjure": kaca_saiki < kaca_pungkasan,
        }

    def paginate(self, per_page=15, page=1):
        return self.kaca(per_page, page)

    def _resolve_relation_metadata(self, relation_name: str) -> RelationMetadata:
        """Inspect the model to determine relationship type and keys."""
        dummy = self.cls() if isinstance(self.cls, NgapakClass) else self.cls.__new__(self.cls)
        dummy._eager_inspect = True

        # 1. Search for method on model
        method = None
        candidates = [relation_name, relation_name.lower(), relation_name.capitalize()]
        
        if isinstance(self.cls, NgapakClass):
            for cand in candidates:
                if cand in self.cls.methods:
                    method = self.cls.methods[cand]
                    break
                elif cand in self.cls.attributes:
                    method = self.cls.attributes[cand]
                    break
        else:
            for cand in candidates:
                if hasattr(self.cls, cand):
                    method = getattr(self.cls, cand)
                    break

        if method:
            try:
                if hasattr(method, "chunk") and Model.active_vm:
                    meta = Model.active_vm.execute_callable(method, [dummy])
                    if isinstance(meta, RelationMetadata):
                        return meta
                elif callable(method):
                    meta = method(dummy)
                    if isinstance(meta, RelationMetadata):
                        return meta
            except Exception:
                pass

        # 2. Fallback heuristic: relation_name is related model name
        if Model.active_vm:
            for cand in candidates:
                if cand in Model.active_vm.globals:
                    related_cls = Model.active_vm.globals[cand]
                    parent_name = self.cls.name.lower() if hasattr(self.cls, "name") else self.cls.__name__.lower()
                    related_name = cand.lower()
                    
                    # Assume hasMany if related table has parent_id
                    return RelationMetadata("hasMany", cand, f"{parent_name}_id", "id")

        return None

    def _load_eager_relations(self, instances):
        """Batch-load related models in 1 query per relation (N+1 elimination)."""
        if not Model.active_vm:
            return

        for relation_name in self._eager_relations:
            meta = self._resolve_relation_metadata(relation_name)
            if not meta:
                continue

            related_class = Model.active_vm.globals.get(meta.related_class_name)
            if not related_class:
                continue

            related_table = Model.get_table_name(related_class)

            if meta.rel_type == "hasMany":
                # Collect parent IDs
                parent_ids = []
                for inst in instances:
                    val = inst.fields.get(meta.owner_or_local_key) if isinstance(inst, NgapakInstance) else getattr(inst, meta.owner_or_local_key, None)
                    if val is not None:
                        parent_ids.append(val)

                grouped = {}
                if parent_ids:
                    # EXACTLY ONE BATCH QUERY FOR ALL CHILDREN
                    child_rows = QueryBuilder(related_table).where_in(meta.foreign_key, parent_ids).kabeh()
                    for row in child_rows:
                        fk_val = row.get(meta.foreign_key)
                        c_inst = related_class() if isinstance(related_class, NgapakClass) else related_class.__new__(related_class)
                        if isinstance(c_inst, NgapakInstance):
                            c_inst.fields.update(row)
                        else:
                            c_inst.__dict__.update(row)
                        c_inst._relations = {}
                        grouped.setdefault(fk_val, []).append(c_inst)

                for inst in instances:
                    pk_val = inst.fields.get(meta.owner_or_local_key) if isinstance(inst, NgapakInstance) else getattr(inst, meta.owner_or_local_key, None)
                    matched_list = grouped.get(pk_val, [])
                    inst._relations[relation_name] = matched_list
                    inst._relations[meta.related_class_name] = matched_list

            elif meta.rel_type == "hasOne":
                parent_ids = []
                for inst in instances:
                    val = inst.fields.get(meta.owner_or_local_key) if isinstance(inst, NgapakInstance) else getattr(inst, meta.owner_or_local_key, None)
                    if val is not None:
                        parent_ids.append(val)

                grouped = {}
                if parent_ids:
                    child_rows = QueryBuilder(related_table).where_in(meta.foreign_key, parent_ids).kabeh()
                    for row in child_rows:
                        fk_val = row.get(meta.foreign_key)
                        c_inst = related_class() if isinstance(related_class, NgapakClass) else related_class.__new__(related_class)
                        if isinstance(c_inst, NgapakInstance):
                            c_inst.fields.update(row)
                        else:
                            c_inst.__dict__.update(row)
                        c_inst._relations = {}
                        if fk_val not in grouped:
                            grouped[fk_val] = c_inst

                for inst in instances:
                    pk_val = inst.fields.get(meta.owner_or_local_key) if isinstance(inst, NgapakInstance) else getattr(inst, meta.owner_or_local_key, None)
                    matched_item = grouped.get(pk_val, None)
                    inst._relations[relation_name] = matched_item
                    inst._relations[meta.related_class_name] = matched_item

            elif meta.rel_type == "belongsTo":
                foreign_ids = []
                for inst in instances:
                    val = inst.fields.get(meta.foreign_key) if isinstance(inst, NgapakInstance) else getattr(inst, meta.foreign_key, None)
                    if val is not None:
                        foreign_ids.append(val)

                mapped = {}
                if foreign_ids:
                    parent_rows = QueryBuilder(related_table).where_in(meta.owner_or_local_key, foreign_ids).kabeh()
                    for row in parent_rows:
                        pk_val = row.get(meta.owner_or_local_key)
                        p_inst = related_class() if isinstance(related_class, NgapakClass) else related_class.__new__(related_class)
                        if isinstance(p_inst, NgapakInstance):
                            p_inst.fields.update(row)
                        else:
                            p_inst.__dict__.update(row)
                        p_inst._relations = {}
                        mapped[pk_val] = p_inst

                for inst in instances:
                    fk_val = inst.fields.get(meta.foreign_key) if isinstance(inst, NgapakInstance) else getattr(inst, meta.foreign_key, None)
                    matched_item = mapped.get(fk_val, None)
                    inst._relations[relation_name] = matched_item
                    inst._relations[meta.related_class_name] = matched_item
