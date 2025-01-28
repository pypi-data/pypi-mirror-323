import json
from typing import Any, Callable, ClassVar, Dict, Generic, Mapping, Tuple, Type, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel

from vellum.utils.templating.constants import DEFAULT_JINJA_CUSTOM_FILTERS, DEFAULT_JINJA_GLOBALS
from vellum.utils.templating.exceptions import JinjaTemplateError
from vellum.utils.templating.render import render_sandboxed_jinja_template
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base import BaseNodeMeta
from vellum.workflows.types.core import EntityInputsInterface, Json
from vellum.workflows.types.generics import StateType
from vellum.workflows.types.utils import get_original_base

_OutputType = TypeVar("_OutputType")


# TODO: Consolidate all dynamic output metaclasses
# https://app.shortcut.com/vellum/story/5533
class _TemplatingNodeMeta(BaseNodeMeta):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        parent = super().__new__(mcs, name, bases, dct)

        if not isinstance(parent, _TemplatingNodeMeta):
            raise ValueError("TemplatingNode must be created with the TemplatingNodeMeta metaclass")

        annotations = parent.__dict__["Outputs"].__annotations__
        parent.__dict__["Outputs"].__annotations__ = {
            **annotations,
            "result": parent.get_output_type(),
        }
        return parent

    def get_output_type(cls) -> Type:
        original_base = get_original_base(cls)
        all_args = get_args(original_base)

        if len(all_args) < 2 or isinstance(all_args[1], TypeVar):
            return str
        else:
            return all_args[1]


class TemplatingNode(BaseNode[StateType], Generic[StateType, _OutputType], metaclass=_TemplatingNodeMeta):
    """Used to render a Jinja template.

    Useful for lightweight data transformations and complex string templating.
    """

    # The Jinja template to render.
    template: ClassVar[str]

    # The inputs to render the template with.
    inputs: ClassVar[EntityInputsInterface]

    jinja_globals: Dict[str, Any] = DEFAULT_JINJA_GLOBALS
    jinja_custom_filters: Mapping[str, Callable[[Union[str, bytes]], bool]] = DEFAULT_JINJA_CUSTOM_FILTERS

    class Outputs(BaseNode.Outputs):
        """
        The outputs of the TemplatingNode.

        result: _OutputType - The result of the template rendering
        """

        # We use our mypy plugin to override the _OutputType with the actual output type
        # for downstream references to this output.
        result: _OutputType  # type: ignore[valid-type]

    def _cast_rendered_template(self, rendered_template: str) -> Any:
        original_base = get_original_base(self.__class__)
        all_args = get_args(original_base)

        output_type: Any
        if len(all_args) < 2 or isinstance(all_args[1], TypeVar):
            output_type = str
        else:
            output_type = all_args[1]

        if output_type is str:
            return rendered_template

        if output_type is float:
            return float(rendered_template)

        if output_type is int:
            return int(rendered_template)

        if output_type is bool:
            return bool(rendered_template)

        if get_origin(output_type) is list:
            try:
                data = json.loads(rendered_template)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON Array format for rendered_template")

            if not isinstance(data, list):
                raise ValueError(f"Expected a list of items for rendered_template, received {data.__class__.__name__}")

            inner_type = get_args(output_type)[0]
            if issubclass(inner_type, BaseModel):
                return [inner_type.model_validate(item) for item in data]
            else:
                return data

        if output_type is Json:
            try:
                return json.loads(rendered_template)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for rendered_template")

        if issubclass(output_type, BaseModel):
            try:
                data = json.loads(rendered_template)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for rendered_template")

            return output_type.model_validate(data)

        raise ValueError(f"Unsupported output type: {output_type}")

    def run(self) -> Outputs:
        rendered_template = self._render_template()
        result = self._cast_rendered_template(rendered_template)

        return self.Outputs(result=result)

    def _render_template(self) -> str:
        try:
            return render_sandboxed_jinja_template(
                template=self.template,
                input_values=self.inputs,
                jinja_custom_filters={**self.jinja_custom_filters},
                jinja_globals=self.jinja_globals,
            )
        except JinjaTemplateError as e:
            raise NodeException(message=str(e), code=WorkflowErrorCode.INVALID_TEMPLATE)
