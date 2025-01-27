import re
import itertools
from dataclasses import dataclass, asdict, field, Field, make_dataclass, fields, MISSING
from typing import Optional, Any, Protocol, ClassVar, Union, get_origin, get_args, Concatenate
import json
from collections.abc import Mapping

from dataclasses_json import config, dataclass_json
import yaml

_VERSION = '3.1.1'

def _filter_none_from_dict(d: dict) -> dict:
  if isinstance(d, Mapping):
    return {k: _filter_none_from_dict(v) for k, v in d.items() if v is not None}
  else:
    return d

class _IsDataClass(Protocol):
  __dataclass_fields__: ClassVar[dict[str, Any]]

class __openapi_repr():
  def __to_dict(self):
    return _filter_none_from_dict(self.to_dict())

  def openapi_to_json(self) -> str:
    return json.dumps(self.__to_dict())

  def openapi_to_yaml(self) -> str:
    return yaml.dump(self.__to_dict())

  def __str__(self) -> str:
    return self.openapi_to_yaml()

# OpenAPI Dataclasses
@dataclass_json
@dataclass
class ServerVariable(__openapi_repr):
  default: str
  enum: Optional[list[str]] = None
  description: Optional[str] = None

@dataclass_json
@dataclass
class ExternalDocumentation(__openapi_repr):
  url: str
  name: Optional[str] = None

@dataclass_json
@dataclass
class Server(__openapi_repr):
  url: str
  description: Optional[str] = None
  variables: Optional[dict[str, ServerVariable]] = None

@dataclass_json
@dataclass
class Contact(__openapi_repr):
  name: Optional[str] = None
  url: Optional[str] = None
  email: Optional[str] = None

@dataclass_json
@dataclass
class License(__openapi_repr):
  name: str
  identifier: Optional[str] = None
  url: Optional[str] = None

@dataclass_json
@dataclass
class Info(__openapi_repr):
  title: str
  version: str
  summary: Optional[str] = None
  description: Optional[str] = None
  termsOfService: Optional[str] = None
  contact: Contact = None
  license: License = None

@dataclass_json
@dataclass
class Reference(__openapi_repr):
  ref: str = field(metadata=config(field_name="$ref"))
  summary: Optional[str] = None
  description: Optional[str] = None

@dataclass_json
@dataclass
class Discriminator(__openapi_repr):
  propertyName: str
  mapping: Optional[dict[str, str]] = None

@dataclass_json
@dataclass
class XML(__openapi_repr):
  name: Optional[str] = None
  namespace: Optional[str] = None
  prefix: Optional[str] = None
  attribute: Optional[bool] = None
  wrapped: Optional[bool] = None

@dataclass_json
@dataclass
class Schema(__openapi_repr):
  ref: Optional[str] = field(metadata=config(field_name="$ref"), default=None)
  discriminator: Optional[Discriminator] = None
  xml: Optional[XML] = None
  externalDocs: Optional[ExternalDocumentation] = None
  required: Optional[list[str]] = None
  properties: Optional[dict[str, dict[str, str]]] = None
  field_type: Optional[str] = field(metadata=config(field_name="type"), default=None)
  items: Optional[Reference] = None
  example: Optional[Any] = None # deprecated

@dataclass_json
@dataclass
class Example(__openapi_repr):
  summary: Optional[str] = None
  description: Optional[str] = None
  value: Optional[Any] = None
  externalValue: Optional[str] = None

@dataclass_json
@dataclass
class Header(__openapi_repr):
  description: Optional[str] = None
  required: Optional[bool] = None
  deprecated: Optional[bool] = None

@dataclass_json
@dataclass
class Encoding(__openapi_repr):
  contentType: Optional[str] = None
  headers: Optional[dict[str, Header | Reference]] = None

@dataclass_json
@dataclass
class Link(__openapi_repr):
  operationRef: Optional[str] = None
  operationId: Optional[str] = None
  parameters: Optional[dict[str, Any]] = None
  requestBody: Optional[dict[str, Any]] = None
  description: Optional[str] = None
  server: Optional[Server] = None

@dataclass_json
@dataclass
class MediaType(__openapi_repr):
  schema: Optional[Schema] = None
  example: Optional[Any] = None
  examples: Optional[dict[str, Example | Reference]] = None
  encoding: Optional[dict[str, Encoding]] = None

@dataclass_json
@dataclass
class OAuthFlow(__openapi_repr):
  authorizationUrl: str
  tokenUrl: str
  scopes: dict[str, str]
  refreshUrl: Optional[str] = None

@dataclass_json
@dataclass
class OAuthFlows(__openapi_repr):
  implicit: Optional[OAuthFlow] = None
  password: Optional[OAuthFlow] = None
  clientCredentials: Optional[OAuthFlow] = None
  authorizationCode: Optional[OAuthFlow] = None

@dataclass_json
@dataclass
class SecurityScheme(__openapi_repr):
  field_type: str
  name: str
  field_in: str # can be query, header, or cookie
  scheme: str
  flows: OAuthFlows
  openIdConnectUrl: str
  description: Optional[str] = None
  bearerFormat: Optional[str] = None



@dataclass_json
@dataclass
class Response(__openapi_repr):
  description: str
  headers: Optional[dict[str, Header | Reference]] = None
  content: Optional[dict[str, MediaType]] = None
  links: Optional[dict[str, Link | Reference]] = None

## Define Responses
def __status_code_to_field(statusCode: int):
  name = 'sc{}'.format(statusCode)
  typehint = Optional[Response | Reference]
  dataclassField = field(metadata=config(field_name='{}'.format(statusCode)), default=None)
  return (name, typehint, dataclassField)

__default_fields = [('default', Optional[Response | Reference], field(default=None))]
__status_code_fields = [__status_code_to_field(statusCode) for statusCode in range(100, 600)]
Responses = make_dataclass('Responses', __default_fields + __status_code_fields)


@dataclass_json
@dataclass
class RequestBody(__openapi_repr):
  content: dict[str, MediaType]
  description: Optional[str] = None
  required: Optional[bool] = None

@dataclass_json
@dataclass
class Parameter(__openapi_repr):
  name: str
  field_in: str = field(metadata=config(field_name="in"))# can be query, header, path, cookie
  description: Optional[str] = None
  required: bool = False
  deprecated: Optional[bool] = None
  allowEmptyValue: Optional[bool] = None

@dataclass_json
@dataclass
class Operation(__openapi_repr):
  tags: Optional[list[str]] = None
  summary: Optional[str] = None
  description: Optional[str] = None
  externalDocs: Optional[ExternalDocumentation] = None
  operationId: Optional[str] = None
  parameters: Optional[list[Parameter | Reference]] = None
  requestBody: Optional[RequestBody | Reference] = None
  responses: Optional[Responses] = None
  callbacks: Optional[dict[str, dict[str, 'PathItem'] | Reference]] = None
  deprecated: Optional[bool] = None
  security: Optional[list[ dict[str, list[str]] ]] = None
  servers: Optional[list[Server]] = None

@dataclass_json
@dataclass
class PathItem(__openapi_repr):
  ref: Optional[str] = field(metadata=config(field_name="$ref"), default=None)
  summary: Optional[str] = None
  description: Optional[str] = None
  servers: Optional[list[Server]] = None
  parameters: Optional[list[Parameter | Reference]] = None
  get: Optional[Operation] = None
  put: Optional[Operation] = None
  post: Optional[Operation] = None
  delete: Optional[Operation] = None
  options: Optional[Operation] = None
  head: Optional[Operation] = None
  patch: Optional[Operation] = None
  trace: Optional[Operation] = None

@dataclass_json
@dataclass
class Tag():
  name: str
  description: Optional[str] = None
  externalDocs: Optional[ExternalDocumentation] = None

@dataclass_json
@dataclass
class Components():
  schemas: Optional[dict[str, Schema]] = None
  responses: Optional[dict[str, Response | Reference]] = None
  parameters: Optional[dict[str, Parameter | Reference]] = None
  examples: Optional[dict[str, Example | Reference]] = None
  requestBodies: Optional[dict[str, RequestBody | Reference]] = None
  headers: Optional[dict[str, Header | Reference]] = None
  securitySchemes: Optional[dict[str, SecurityScheme | Reference]] = None
  links: Optional[dict[str, Link | Reference]] = None
  callbacks: Optional[dict[str, dict[str, PathItem] | Reference]] = None
  pathItems: Optional[dict[str, PathItem]] = None

@dataclass_json
@dataclass
class Description(__openapi_repr):
  info: Info
  openapi: str = _VERSION
  security: Optional[list[ dict[str, list[str]] ]] = None
  jsonSchemaDialect: Optional[str] = None
  servers: Optional[list[Server]] = None
  paths: Optional[dict[str, PathItem]] = field(default_factory=lambda: {})
  webhooks: Optional[dict[str, PathItem]] = None
  tags: Optional[list[Tag]] = None
  externalDocs: Optional[ExternalDocumentation] = None
  components: Optional[Components] = None

  def path(
    self: 'Description',
    path: str,
    summary: Optional[str] = None,
    path_parameter_descriptions: Optional[list[str]] = None
  ) -> PathItem:
    if path not in self.paths:
      # Extract parameters from path and match with descriptions
      parameters = None
      path_parameter_names = re.findall(r"\{([^}]*)\}", path)
      if len(path_parameter_names) > 0:
        parameters = []
        path_names_and_descriptions = itertools.zip_longest(path_parameter_names, path_parameter_descriptions)
        for match in path_names_and_descriptions:
          parameters.append(
            Parameter(
              name=match[0],
              field_in='path',
              description=match[1],
              required=True
            )
          )
      self.paths[path] = PathItem(summary=summary, parameters=parameters)
    return self.paths[path]

  def __deconstruct_generic_types(self, fieldType) -> object:
    origin = get_origin(fieldType)
    if origin is None:
      return (fieldType,)
    origin_origin = get_origin(origin)
    if origin_origin is None and origin is not Union and origin is not Concatenate:
      return (origin, get_args(fieldType))
    for arg in get_args(fieldType):
      dFieldType = self.__deconstruct_generic_types(arg)
      if dFieldType[0] is not None:
        return dFieldType
    return self.__deconstruct_generic_types(origin)

  def __get_property(self, _fieldType: Any) -> str:
    deconstructedType = self.__deconstruct_generic_types(_fieldType)
    fieldType = deconstructedType[0]
    if hasattr(fieldType, '__dataclass_fields__'):
      return Reference(self.__addSchemaComponent(fieldType))
    if fieldType is float or fieldType is int or fieldType is complex:
      return {
        'type': 'number',
      }
    if fieldType is bool:
      return {
        'type': 'boolean',
      }
    if fieldType is str:
      return {
        'type': 'string',
      }
    if fieldType is list:
      return {
        'type': 'array',
        'items': self.__get_property(deconstructedType[1][0]),
      }
    if fieldType is type(None):
      return {
        'type': 'null',
      }
    return {
      'type': 'object',
    }

  def __field_is_required(self, field: Field):
    is_optional_typing = get_origin(field.type) is Union and type(None) in get_args(field.type)
    is_default_is_not_none = field.default is not None and field.default is not MISSING and field.default_factory is not None and field.default_factory is not MISSING and field.default_factory() is not None
    return is_default_is_not_none or not is_optional_typing

  def __addSchemaComponent(self: 'Description', objClass: _IsDataClass) -> str:
    object_name = objClass.__name__
    object_reference = "#/components/schemas/{}".format(object_name)
    if self.components is None:
      self.components = Components(schemas={})
    if self.components.schemas is None:
      self.components.schemas = {}
    if object_name not in self.components.schemas:
      schema = Schema()
      self.components.schemas[object_name] = schema
      required = []
      properties = {}
      for field in fields(objClass):
        if self.__field_is_required(field):
          required.append(field.name)
        properties[field.name] = self.__get_property(field.type)
      schema.required = required
      schema.properties = properties
      schema.field_type = 'object'
    return object_reference

  def _mediatype(self: 'Description', objClass: _IsDataClass) -> MediaType:
    object_reference = self.__addSchemaComponent(objClass)
    return MediaType(schema=Schema(ref=object_reference))

  def operation(
    self: 'Description',
    summary: Optional[str] = None,
    tags: Optional[list[str]] = None,
    cookieParameters: Optional[list[tuple[str, str, Optional[bool]]]] = None,
    headerParameters: Optional[list[tuple[str, str, Optional[bool]]]] = None,
    queryParameters: Optional[list[tuple[str, str, Optional[bool]]]] = None,
    requestBody: Optional[_IsDataClass | str] = None,
    responses: Optional[dict[str, Response]] = None,
  ) -> Operation:
    getParameters = lambda field_in, params: [] if params is None else [Parameter(field_in=field_in, name=param[0], description=param[1], required=(None if len(param) < 3 else param[2])) for param in params]
    parameters = getParameters('cookie', cookieParameters) + getParameters('header', headerParameters) + getParameters('query', queryParameters)
    operationRequestBody = None
    if requestBody is not None:
      if type(requestBody) is str:
        operationRequestBody = RequestBody(content={requestBody: {}}) # File upload
      else:
        operationRequestBody = RequestBody(
          description=requestBody.__name__,
          content={
            'application/json': self._mediatype(requestBody),
          }
        )
    operationResponses = None
    if responses is not None:
      operationResponses = Responses()
      for code, response in responses.items():
        operationResponses.__dict__["sc{}".format(code)] = response
    return Operation(
      summary=summary,
      tags=tags,
      parameters=parameters if len(parameters) > 0 else None,
      requestBody=operationRequestBody,
      responses=operationResponses,
    )

  def response(
    self: 'Description',
    description: str,
    headerParameters: Optional[list[tuple[str, str, Optional[bool]]]] = None,
    responseBody: Optional[_IsDataClass | str] = None,
  ) -> Response:
    headers = None
    if headerParameters is not None:
      headers = {}
      for header in headerParameters:
        headers[header[0]] = Header(description=header[1], required=(None if len(header) < 3 else header[2]))
    content = None
    if responseBody is not None:
      if type(responseBody) is str:
        content = {
          responseBody: {},  # File download
        }
      else:
        content = {
          'application/json': self._mediatype(responseBody),
        }
    return Response(
      description=description,
      headers=headers,
      content=content,
    )

singleton = Description(Info(title="API Title", version="0.1.0"), security=[{},], components=Components(schemas={}))
