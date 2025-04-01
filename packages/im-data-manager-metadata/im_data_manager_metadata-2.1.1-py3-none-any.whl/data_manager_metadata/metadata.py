"""Data Manager Metadata Class Definitions.

Note that the Metadata class is pickled when saved in the database so that
we can hold the annotations as an ordered list of objects.
The other classes should be searialisable without pickling hopefully:
Hints: https://pynative.com/make-python-class-json-serializable/
"""

import json
import datetime
import logging
import copy
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import re

from decoder import decoder
import yaml

from .exceptions import ANNOTATION_ERRORS, AnnotationValidationError

basic_logger: logging.Logger = logging.getLogger(__name__)

_METADATA_VERSION: str = '0.0.1'
_ANNOTATION_VERSION: str = '0.0.1'
_MASTER_VERSION: int = 0
_DEFAULT_SYNC_TIME: str = '2001-01-01T12:00:00.000001'

_SCHEMA: str = 'http://json-schema.org/draft/2019-09/schema#'
_SCHEMA_ID: str = 'https://example.com/product.schema.json'
_ANNOTATIONS_EXT = '.annotations'


# This is the basic structure of the rows FieldsDescriptorAnnotation fields
# list that is indexed by the field name.
FIELD_DICT = {'type': '', 'description': '', 'required': False, 'active': False}


def get_metadata_version() -> str:
    return _METADATA_VERSION


def get_annotation_version() -> str:
    return _ANNOTATION_VERSION


def get_annotation_filename(filename: str) -> str:
    """Return the associated annotations filename for a particular file
    This is very simple, but best done the same way everywhere!
    """
    assert filename
    return filename + _ANNOTATIONS_EXT


class Metadata:
    """Class Metadata

    Purpose: Defines a list of metadata dnd annotations that can be serialized
    and saved in a dataset.

    """

    def __init__(
        self,
        dataset_name: str,
        dataset_id: str,
        description: str,
        created_by: str,
        created: str = None,
        last_updated: str = None,
        metadata_version: str = None,
        annotations: List = None,
        labels: List = None,
        dataset_version: int = None,
        synchronised_datetime: str = None,
    ):
        assert dataset_name
        assert dataset_id
        assert created_by

        self.dataset_name = dataset_name
        self.dataset_uuid = dataset_id
        self.description = description
        self.created_by = created_by

        if created:
            self.created = datetime.datetime.strptime(created, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self.created = datetime.datetime.utcnow()

        if last_updated:
            self.last_updated = datetime.datetime.strptime(
                last_updated, '%Y-%m-%dT%H:%M:%S.%f'
            )
        else:
            self.last_updated = self.created

        if metadata_version:
            self.metadata_version = metadata_version
        else:
            self.metadata_version = get_metadata_version()

        self.annotations = []
        if annotations:
            annos_copy = copy.deepcopy(annotations)
            self.add_annotations(annos_copy, init=True)

        self.labels = []
        if labels:
            labels_copy = copy.deepcopy(labels)
            for label_row in labels_copy:
                self._create_label(label_row)

        if dataset_version:
            self.dataset_version = dataset_version
        else:
            self.dataset_version = _MASTER_VERSION

        if synchronised_datetime:
            self.synchronised_datetime = datetime.datetime.strptime(
                synchronised_datetime, '%Y-%m-%dT%H:%M:%S.%f'
            )
        else:
            self.synchronised_datetime = datetime.datetime.strptime(
                _DEFAULT_SYNC_TIME, '%Y-%m-%dT%H:%M:%S.%f'
            )

    def get_dataset_name(self):
        return self.dataset_name

    def set_dataset_name(self, dataset_name: str):
        assert dataset_name
        annotation = PropertyChangeAnnotation('dataset_name', self.dataset_name)
        self.add_annotation(annotation)
        self.dataset_name = dataset_name

    def get_dataset_uuid(self):
        return self.dataset_uuid

    def set_dataset_uuid(self, dataset_uuid: str):
        assert dataset_uuid
        annotation = PropertyChangeAnnotation('dataset_uuid', self.dataset_uuid)
        self.add_annotation(annotation)
        self.dataset_uuid = dataset_uuid

    def get_description(self):
        return self.description

    def set_description(self, description: str):
        annotation = PropertyChangeAnnotation('description', self.description)
        self.add_annotation(annotation)
        self.description = description

    def get_created_by(self):
        return self.created_by

    def set_created_by(self, created_by: str):
        assert created_by
        annotation = PropertyChangeAnnotation('created_by', self.created_by)
        self.add_annotation(annotation)
        self.created_by = created_by

    def get_metadata_version(self):
        return self.metadata_version

    def get_dataset_version(self):
        return self.dataset_version

    def set_dataset_version(self, dataset_version: int):
        # Note that no property change annotation is set here as this is
        # a technical field.
        assert dataset_version
        self.dataset_version = dataset_version

    def get_synchronised_datetime(self):
        return self.synchronised_datetime.isoformat()

    def set_synchronised_datetime(self):
        # Note that no property change annotation is set here as this is
        # a technical field.
        self.synchronised_datetime = datetime.datetime.utcnow()

    def get_annotation(self, pos: int):
        """Get an annotation from the annotation list identified by the
        position.
        """
        return self.annotations[pos]

    def add_annotation(self, annotation: object):
        """Add a serialized annotation to the annotation list"""
        self.annotations.append(annotation)
        self.last_updated = datetime.datetime.utcnow()

    def get_annotations_dict(self, annotation_type=all):
        """Get a list of all annotations from the annotation list in dict
        format.

            The list can be filtered by annotation class.
            Within an annotation class, the keyword arguments can be used to
            filter within a particular class.
        """
        anno_list = []
        for anno in self.annotations:
            if annotation_type is all:
                anno_list.append(anno.to_dict())
            elif anno.get_type() is annotation_type:
                anno_list.append(anno.to_dict())
        return anno_list

    def get_annotations_json(self, annotation_type=all):
        """Get a list of all annotations from the annotation list in json
        format.
        """
        return json.dumps(self.get_annotations_dict(annotation_type))

    def _create_annotation(self, annotation_row: dict):
        """Creates an annotation object based on the dictionary and add to the
        annotations list.
        """
        class_lookup = {
            'PropertyChangeAnnotation': PropertyChangeAnnotation,
            'FieldsDescriptorAnnotation': FieldsDescriptorAnnotation,
            'ServiceExecutionAnnotation': ServiceExecutionAnnotation,
        }

        # Get class and original create data
        annotation_class = annotation_row['type']
        annotation_created = None
        # Remove from parameter list
        del annotation_row['type']

        # Remove unused elements if they exist
        if 'created' in annotation_row:
            annotation_created = annotation_row['created']
            del annotation_row['created']
        if 'annotation_version' in annotation_row:
            del annotation_row['annotation_version']

        # Create new annotation for metadata using rest of original parameters
        # and reset created datetime. This also effectively validates the
        # content.
        annotation = class_lookup[annotation_class](**annotation_row)
        if annotation_created:
            annotation.set_created(annotation_created)
        self.annotations.append(annotation)

    def add_annotations(self, annotations_list: dict, init=False):
        """Add a list of annotations in json format to the annotation list"""
        # Note that this also validates the Json and returns a ValueError if
        # not valid
        # annotations_list = json.loads(annotations)

        # If a single annotation is provided but it's simply not in a list then
        # add it
        # if annotations.lstrip()[0] != '[':
        #    annotations_list = []
        #    annotations_list.append(json.loads(annotations))

        if 'type' in annotations_list:
            # Only one annotation in the dict.
            self._create_annotation(annotations_list)
        else:
            # Murltiple annotations in the dict
            for annotation_row in annotations_list:
                self._create_annotation(annotation_row)

        if not init:
            self.last_updated = datetime.datetime.utcnow()

    def _create_label(self, label_row: dict):
        """Creates an annotation object based on the dictionary and add to the
        labels list.
        """
        class_lookup = {'LabelAnnotation': LabelAnnotation}

        # Get class and original create data
        label_class = label_row['type']
        label_created = None
        # Remove from parameter list
        del label_row['type']

        # Remove unused elements if they exist
        if 'created' in label_row:
            label_created = label_row['created']
            del label_row['created']
        if 'annotation_version' in label_row:
            del label_row['annotation_version']

        # Create new label for metadata using rest of original parameters
        # and reset created datetime. This also effectively validates the
        # content.
        label = class_lookup[label_class](**label_row)
        if label_created:
            label.set_created(label_created)
        self.labels.append(label)

    def add_label(self, label: object):
        """Add a serialized annotation to the annotation list"""
        self.labels.append(label)
        self.last_updated = datetime.datetime.utcnow()

    def add_labels(self, labels_list: dict):
        """Add a list of labels in dict format to the labels list"""
        for label_row in labels_list:
            self._create_label(label_row)
        self.last_updated = datetime.datetime.utcnow()

    def get_labels_existing_dataset(self, synchronised_datetime: str):
        """Get a list of the labels from the labels list that were applied
        after a given datetime (used for synchronising travelling metadata with
        an existing dataset when adding labels
        """
        compare_datetime = datetime.datetime.strptime(
            synchronised_datetime, '%Y-%m-%dT%H:%M:%S.%f'
        )

        return [
            label.to_dict() for label in self.labels if label.created > compare_datetime
        ]

    def get_labels_new_dataset(self, synchronised_datetime: str):
        """Get the subset of the labels from the from travelling metadat that with
        be applied when creating a new dataset. These are:
        1. plane labels after the synchronised-datetime (i.e. created by the job)
        2. any hash or address labels.
        """

        active_labels = self.get_labels(active=True)
        for label in active_labels:
            if (
                label['label'][0] not in ['#', '@']
                and label['created'] < synchronised_datetime
            ):
                active_labels.remove(label)

        return active_labels

    def get_labels(self, active=None, labels_only=False, label_type='all'):
        """Returns a list of the active/inactive Label Annotations.
        The last version of each label is returned.
        active not set, return complete set
        active = true - filter for active
        If label_type is set, then filter for plain, hash(#) or address(@) labels
        """
        label_list = []
        label_set = set()
        # Read through labels in reverse order and take the latest one for
        # each label.
        for anno in reversed(self.labels):
            if anno.get_label(label_types=[label_type]) not in label_set:
                label_list.append(anno)
                label_set.add(anno.get_label())

        # If not active then filter any inactive labels
        if active is True:
            for label in reversed(label_list):
                if label.get_active() is False:
                    label_list.remove(label)

        if labels_only:
            return_dict = {}
            for label in label_list:
                return_dict.update({label.get_label(): label.get_value()})
        else:
            return_dict = [label.to_dict() for label in label_list]

        return return_dict

    def get_json_schema(self):
        """Returns the latest complete FieldsDescriptor and labels as a dict
        of the json schema as defined in https://json-schema.org/.
        """

        # Process all FieldDescriptor Annotations in the Annotations list in
        # order to retrieve all of the fields in the dataset. Add these to a
        # single new FieldDescriptor that will have compilation of all fields.
        # We can then extract the active fields from the final compiled
        # FieldDescriptor to use in the json schema output.
        comp_descriptor = FieldsDescriptorAnnotation()
        for annotation in self.annotations:
            if annotation.get_type() in [
                'FieldsDescriptorAnnotation',
                'ServiceExecutionAnnotation',
            ]:
                # Allow for validation errors in old field descriptors.
                try:
                    comp_descriptor.add_fields(annotation.get_fields())
                except AnnotationValidationError:
                    pass
        fields = {}
        required = []

        for prop, value in comp_descriptor.get_fields(False).items():
            fields[prop] = {'type': value['type'], 'description': value['description']}
            if value['required']:
                required.append(prop)

        schema = {
            '$schema': _SCHEMA,
            '$id': _SCHEMA_ID,
            'title': self.dataset_name,
            'description': self.description,
            'version': self.dataset_version,
            'type': 'object',
            'fields': fields,
            'required': required,
            'labels': self.get_labels(active=True, labels_only=True),
        }

        return schema

    def get_compiled_fields(self):
        """Returns the latest complete FieldsDescriptor as a dict of the json
        schema as defined in https://json-schema.org/.
        """

        # Process all FieldDescriptor Annotations in the Annotations list in
        # order to retrieve all of the fields in the dataset. Add these to a
        # single new FieldDescriptor that will have compilation of all fields.

        comp_descriptor = FieldsDescriptorAnnotation()
        for annotation in self.annotations:
            if annotation.get_type() in [
                'FieldsDescriptorAnnotation',
                'ServiceExecutionAnnotation',
            ]:
                # Allow for validation errors in old field descriptors.
                try:
                    comp_descriptor.add_fields(annotation.get_fields())
                except AnnotationValidationError:
                    pass

        return comp_descriptor.to_dict()

    def to_dict(self):
        """Return principle data items in the form of a dictionary"""
        return {
            "dataset_name": self.dataset_name,
            "dataset_id": self.dataset_uuid,
            "description": self.description,
            "created": self.created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "created_by": self.created_by,
            "metadata_version": self.metadata_version,
            "dataset_version": self.dataset_version,
            "annotations": [anno.to_dict() for anno in self.annotations],
            "labels": [anno.to_dict() for anno in self.labels],
            "synchronised_datetime": self.synchronised_datetime.isoformat(),
        }

    def to_json(self):
        """Serialize class to JSON"""
        output_dict = self.to_dict()
        return json.dumps(output_dict)


class Annotation(ABC):
    """Class Annotation - Abstract Base Class to enable annotation
    functionality

    Purpose: Annotations can be added to Metadata. They are defined as classes
    so that they can have both fixed data and methods that work with the data.

    """

    @abstractmethod
    def __init__(self):
        self.created = datetime.datetime.utcnow()
        self.annotation_version = get_annotation_version()

    def get_type(self):
        return self.__class__.__name__

    def set_created(self, created):
        """This used only when transferring existing annotations to a new
        metadata instance.
        """
        self.created = datetime.datetime.fromisoformat(created)

    def to_dict(self):
        """Return principle data items in the form of a dictionary"""
        return {
            "type": self.__class__.__name__,
            "created": self.created.isoformat(),
            "annotation_version": self.annotation_version,
        }

    def to_json(self):
        """Serialize class to JSON"""
        return json.dumps(self.to_dict())


class PropertyChangeAnnotation(Annotation):
    """Class PropertyChangeAnnotation

    Purpose: A simple annotation used when a property changes in the metadata.

    """

    # meta_property: str = ''
    # previous_value: str = ''

    def __init__(self, meta_property: str, previous_value: str):
        assert property
        self.meta_property = meta_property
        self.previous_value = previous_value
        super().__init__()

    def to_dict(self):
        """Return principle data items in the form of a dictionary"""
        output_dict = {
            "meta_property": self.meta_property,
            "previous_value": self.previous_value,
        }
        return {**super().to_dict(), **output_dict}


class LabelAnnotation(Annotation):
    """Class LabelAnnotation

    Purpose: Object to create a simple label type of annotation to add to the
    metadata.

    Note that the label is associated with an implicit type:
    hash labels (start with #) - can be pulled from multiple files when creating job annotations
    address labels (start with @)  - can be pulled from only the 'derived-from' file when creating
     job annotations.
    plain labels - are only transferred to a new dataset if they are created as a job annotation or
      uploaded as a new version of an existing dataset.

    The optional 'reference' field is intended to be used to be used to communicate to a
    future process such as the pose viewer

    """

    def __init__(
        self, label: str, value: str = None, active: bool = True, reference: str = None
    ):
        self.validate(label, value)
        self.label = label.lower()
        self.value = value
        self.active = active
        self.reference = reference
        super().__init__()

    def validate(self, label: str, value: str = None):
        """Validate main data items"""

        if not re.match(ANNOTATION_ERRORS['LabelAnnotation']['1']['regex'], label):
            raise AnnotationValidationError('LabelAnnotation', '1', 'label')

        if value and not re.match(
            ANNOTATION_ERRORS['LabelAnnotation']['2']['regex'], value
        ):
            raise AnnotationValidationError('LabelAnnotation', '2', 'value')

    def get_label(self, label_types=None):

        if label_types is None:
            label_types = ['all']

        if 'all' in label_types:
            return self.label
        elif 'hash' in label_types and self.label[0] == '#':
            return self.label
        elif 'address' in label_types and self.label[0] == '@':
            return self.label
        elif 'plain' in label_types and self.label[0] not in ['#', '@']:
            return self.label

    def get_value(self):
        return self.value

    def get_active(self):
        return self.active

    def get_reference(self):
        return self.reference

    def to_dict(self):
        """Return principle data items in the form of a dictionary"""
        return {
            **super().to_dict(),
            "label": self.label,
            "value": self.value,
            "active": self.active,
            "reference": self.reference,
        }


class FieldsDescriptorAnnotation(Annotation):
    """Class FieldsDescriptorAnnotation

    Purpose: Object to add a Fields Descriptor annotation to the metadata.
    The class contains a list of fields that a dataset will contain.
    This is expected to be of the format:
    { "name": string, "type": string, "description": string, "active": boolean}

    """

    def __init__(
        self,
        origin: str = '',
        description: str = '',
        fields: dict = None,
        job_spec: dict = None,
    ):

        self.validate_origin(origin)
        self.origin = origin
        self.validate_description(description)
        self.description = description
        self.spec = job_spec
        if fields:
            self.fields = {}
            self.add_fields(fields, job_spec)
        else:
            self.fields = {}
        super().__init__()

    def get_origin(self):
        return self.origin

    def validate_origin(self, origin: str):
        if not re.match(
            ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['1']['regex'], origin
        ):
            raise AnnotationValidationError('FieldsDescriptorAnnotation', '1', 'origin')

    def set_origin(self, origin):
        self.validate_origin(origin)
        self.origin = origin

    def get_description(self):
        return self.description

    def validate_description(self, description: str):
        if not re.match(
            ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['2']['regex'], description
        ):
            raise AnnotationValidationError(
                'FieldsDescriptorAnnotation', '2', 'description'
            )

    def set_description(self, description):
        self.description = description

    def validate_field(
        self, field_name: str, prop_type: str = None, description: str = None
    ):
        """Validate an additions/updates to a field"""

        # field_name
        if not re.match(
            ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['3']['regex'], field_name
        ):
            raise AnnotationValidationError(
                'FieldsDescriptorAnnotation', '3', 'field_name', field_name
            )

        # type is enumerated. This can be omitted if updating an existing field
        if prop_type:
            if (
                prop_type.lower()
                not in ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['4']['enum']
            ):
                raise AnnotationValidationError(
                    'FieldsDescriptorAnnotation', '4', 'type', field_name
                )

        # description can be omitted but if it's there it must be < 255
        if description:
            if not re.match(
                ANNOTATION_ERRORS['FieldsDescriptorAnnotation']['5']['regex'],
                description,
            ):
                raise AnnotationValidationError(
                    'FieldsDescriptorAnnotation', '5', 'description', field_name
                )

    def add_field(
        self,
        *,
        field_name: str,
        active: bool = True,
        prop_type: str = None,
        description: str = None,
        expression: str = None,
        required: bool = None,
        job_spec: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an individual property to the fields list"""

        # If an expression is provided it is assumed to be a jinja2 expression
        # that's expanded using the Job's original variables (in the specification).
        # The field name is then replaced using the result of the expression.
        rendered_field_name: str = field_name
        if expression:
            basic_logger.info(
                'Handling expression for "%s" (%s)', field_name, expression
            )
            # A Job spec must be provided
            if not job_spec:
                raise RuntimeError(
                    f'Field "{field_name}" with expression but no job_spec'
                )
            # Extract variables from the Job spec using our decoder
            # and the "jinja2_3_0" templating engine (that's all that's available atm).
            variables: Dict[str, str] = job_spec.get('variables', {})
            rendered_field_name, success = decoder.decode(
                expression,
                variables,
                'field-expression',
                decoder.TextEncoding.JINJA2_3_0,
            )
            if not success:
                # Failed to render the expression.
                # Do not add this field.
                basic_logger.warning(
                    'Expression failure for "%s" (%s)', field_name, rendered_field_name
                )
                return

        # validate the field data
        self.validate_field(rendered_field_name, prop_type, description)

        # Add to list
        if rendered_field_name not in self.fields:
            # Note that this has to be copied in,
            # or it will reference the same dictionary.
            self.fields[rendered_field_name] = copy.deepcopy(FIELD_DICT)

        self.fields[rendered_field_name]['active'] = active

        if prop_type:
            self.fields[rendered_field_name]['type'] = prop_type.lower()
        if description:
            self.fields[rendered_field_name]['description'] = description
        if required:
            self.fields[rendered_field_name]['required'] = required

    def get_property(self, field_name: str):
        """Get a property from the fields list identified by the name."""
        return self.fields[field_name]

    def add_fields(self, new_fields: dict, job_spec: Optional[dict] = None):
        """Add a dictionary of additions/updates to the fields list
        fields. Each field must have a 'type'.
        """

        for prop, values in new_fields.items():
            # unpack the individual lines for processing, adding optional fields.
            if 'type' not in values:
                raise RuntimeError(f'Property "{prop}" has no "type"')
            self.add_field(
                field_name=prop,
                active=values.get('active', True),
                prop_type=values['type'],
                description=values.get('description'),
                expression=values.get('expression'),
                required=values.get('required', False),
                job_spec=job_spec,
            )

    def get_fields(self, get_all: bool = False):
        """Get (all/only active) fields from the property list in dict format."""
        if get_all:
            return self.fields
        else:
            # Return active fields only
            active_fields = {}
            for prop, value in self.fields.items():
                if value['active']:
                    active_fields[prop] = value
            return active_fields

    def to_dict(self):
        """Return principle data items in the form of a dictionary"""
        return {
            **super().to_dict(),
            "origin": self.origin,
            "description": self.description,
            "fields": self.fields,
        }


class ServiceExecutionAnnotation(FieldsDescriptorAnnotation):
    """Class FieldAnnotation

    Purpose: Object to add a Field Descriptor annotation to the metadata.

    """

    def __init__(
        self,
        service: str,
        service_version: str,
        service_user: str,
        service_name: str,
        service_ref: str,
        service_parameters: dict = None,
        origin: str = '',
        description: str = '',
        fields: list = None,
    ):

        self.validate_service(service)
        self.service = service
        self.validate_service_version(service_version)
        self.service_version = service_version
        self.validate_service_user(service_user)
        self.service_user = service_user
        self.validate_service_name(service_name)
        self.service_name = service_name
        self.validate_service_ref(service_ref)
        self.service_ref = service_ref
        if service_parameters:
            self.service_parameters = copy.deepcopy(service_parameters)
        else:
            self.service_parameters = {}
        super().__init__(origin, description, fields, service_parameters)

    def get_service(self):
        return self.service

    def validate_service(self, service: str):
        if not re.match(
            ANNOTATION_ERRORS['ServiceExecutionAnnotation']['1']['regex'], service
        ):
            raise AnnotationValidationError(
                'ServiceExecutionAnnotation', '1', 'service'
            )

    def get_service_version(self):
        return self.service_version

    def validate_service_version(self, service_version: str):
        if not re.match(
            ANNOTATION_ERRORS['ServiceExecutionAnnotation']['2']['regex'],
            service_version,
        ):
            raise AnnotationValidationError(
                'ServiceExecutionAnnotation', '2', 'service_version'
            )

    def get_service_user(self):
        return self.service_user

    def validate_service_user(self, service_user: str):
        if not re.match(
            ANNOTATION_ERRORS['ServiceExecutionAnnotation']['3']['regex'], service_user
        ):
            raise AnnotationValidationError(
                'ServiceExecutionAnnotation', '3', 'service_user'
            )

    def get_service_name(self):
        return self.service_name

    def validate_service_name(self, service_name: str):
        if not re.match(
            ANNOTATION_ERRORS['ServiceExecutionAnnotation']['4']['regex'], service_name
        ):
            raise AnnotationValidationError(
                'ServiceExecutionAnnotation', '4', 'service_name'
            )

    def get_service_ref(self):
        return self.service_ref

    def validate_service_ref(self, service_ref: str):
        if not re.match(
            ANNOTATION_ERRORS['ServiceExecutionAnnotation']['5']['regex'], service_ref
        ):
            raise AnnotationValidationError(
                'ServiceExecutionAnnotation', '5', 'service_ref'
            )

    def get_service_parameters(self):
        return self.service_parameters

    def set_service_parameters(self, service_parameters: dict):
        self.service_parameters = copy.deepcopy(service_parameters)

    def parameters_to_yaml(self):
        return yaml.dump(self.service_parameters)

    def to_dict(self):
        """Return principle data items in the form of a dictionary"""
        return {
            **super().to_dict(),
            "service": self.service,
            "service_version": self.service_version,
            "service_user": self.service_user,
            "service_name": self.service_name,
            "service_ref": self.service_ref,
            "service_parameters": self.service_parameters,
        }


if __name__ == "__main__":
    print('Data Manager Metadata (v%s)', _METADATA_VERSION)
    print('Data Manager Annotation (v%s)', _ANNOTATION_VERSION)
