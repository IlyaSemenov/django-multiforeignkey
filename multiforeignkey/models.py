from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import DEFAULT_DB_ALIAS, models, router, transaction
from django.db.models import DO_NOTHING, signals
from django.db.models.base import ModelBase, make_foreign_order_accessors
from django.db.models.fields.related import (
	ForeignObject, ForeignObjectRel, ReverseManyToOneDescriptor,
	lazy_related_operation,
)
from django.db.models.query_utils import PathInfo
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.functional import cached_property


class MultiForeignKey(object):
	# Field flags
	auto_created = False
	concrete = False
	editable = False
	hidden = False

	is_relation = True
	many_to_many = False
	many_to_one = True
	one_to_many = False
	one_to_one = False
	related_model = None
	remote_field = None

	def __init__(self, *args):
		if not args:
			raise ValueError("Provide at least one model")
		self.subfields = {
			model._meta.model_name: models.ForeignKey(model, null=True)
			for model in args
		}
		self.editable = False
		self.rel = None
		self.column = None

	def contribute_to_class(self, cls, name, **kwargs):
		self.name = name
		self.model = cls
		cls._meta.add_field(self, virtual=True)
		for subname, subfield in self.subfields.items():
			subfield.contribute_to_class(cls, subname)

		# Only run pre-initialization field assignment on non-abstract models
		if not cls._meta.abstract:
			signals.pre_init.connect(self.instance_pre_init, sender=cls)

		setattr(cls, name, self)

	def __str__(self):
		model = self.model
		app = model._meta.app_label
		return '%s.%s.%s' % (app, model._meta.object_name, self.name)

	def check(self, **kwargs):
		errors = []
		errors.extend(self._check_field_name())
		return errors

	def _check_field_name(self):
		if self.name.endswith("_"):
			return [
				checks.Error(
					'Field names must not end with an underscore.',
					hint=None,
					obj=self,
					id='fields.E001',
				)
			]
		else:
			return []

	def instance_pre_init(self, signal, sender, args, kwargs, **_kwargs):
		"""
		Handle initializing an object with the multi-FK
		"""
		if self.name in kwargs:
			value = kwargs.pop(self.name)
			for subname, subfield in self.subfields.items():
				kwargs[subname] = value if isinstance(value, subfield.model) else None

	def __get__(self, instance, instance_type=None):
		if instance is None:
			return self

		for subname in self.subfields.keys():
			value = getattr(instance, subname)
			if value is not None:
				return value

		return None

	def __set__(self, instance, value):
		if value is None:
			for subname, subfield in self.subfields.keys():
				setattr(instance, subname, None)
		else:
			allowed_models = [subfield.model for subfield in self.subfields]
			if not isinstance(value, allowed_models):
				raise ValueError("{} must be one of: {}".format(self.name, ", ".join(model.__name__ for model in allowed_models)))
			for subname, subfield in self.subfields.items():
				setattr(instance, subname, value if isinstance(value, subfield.model) else None)
