"""Create Embeddings via OpenAI embeddings API endpoint"""

from collections.abc import Generator, Sequence
from typing import Any, ClassVar

from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
    PluginContext,
)
from cmem_plugin_base.dataintegration.description import Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import (
    FixedNumberOfInputs,
    FixedSchemaPort,
    FlexibleSchemaPort,
    UnknownSchemaPort,
)
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from langchain_core.utils.utils import convert_to_secret_str
from langchain_openai import OpenAIEmbeddings
from openai import AuthenticationError, OpenAI

DEFAULT_EMBEDDING_PATH = "_embedding"
DEFAULT_EMBEDDING_SOURCE_PATH = "_embedding_source"
MODEL_EXAMPLE = "text-embedding-3-small"


class SamePathError(ValueError):
    """Same Path Exception"""

    def __init__(self, path: str):
        super().__init__(f"Path '{path}' can not be input AND output path.")


class OpenAPIModel(StringParameterType):
    """OpenAPI Model Type"""

    autocompletion_depends_on_parameters: ClassVar[list[str]] = ["url", "api_key"]

    # auto complete for values
    allow_only_autocompleted_values: bool = True
    # auto complete for labels
    autocomplete_value_with_labels: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Return all results that match ALL provided query terms."""
        _ = context
        url = depend_on_parameter_values[0]
        api_key = depend_on_parameter_values[1]
        api_key = api_key if isinstance(api_key, str) else api_key.decrypt()
        result = []
        try:
            api = OpenAI(api_key=api_key, base_url=url)
            models = api.models.list()
            filtered_models = set()
            if query_terms:
                for term in query_terms:
                    for model in models:
                        if term in model.id:
                            filtered_models.add(model.id)
            else:
                filtered_models = {_.id for _ in models}
            result = [Autocompletion(value=f"{_}", label=f"{_}") for _ in filtered_models]
        except AuthenticationError as error:
            raise ValueError(
                "Failed to authenticate with OpenAI API, Please check URL and API key."
            ) from error

        result.sort(key=lambda x: x.label)
        return result


@Plugin(
    label="Create Embeddings",
    description="Fetch embeddings from OpenAI embeddings API endpoint.",
    parameters=[
        PluginParameter(
            name="url",
            label="URL",
            description="URL of the OpenAI API (without endpoint path and without trailing slash)",
            default_value="https://api.openai.com/v1",
        ),
        PluginParameter(
            name="api_key",
            label="The OpenAI API key",
            param_type=PasswordParameterType(),
            description="Fill the OpenAI API key if needed "
            "(or give a dummy value in case you access an unsecured endpoint).",
        ),
        PluginParameter(
            name="model",
            label=f"The embeddings model, e.g. {MODEL_EXAMPLE}",
            param_type=OpenAPIModel(),
        ),
        PluginParameter(
            name="timout_single_request",
            label="Timeout (Single Request, in Milliseconds)",
            advanced=True,
            default_value=10000,
        ),
        PluginParameter(
            name="entries_processing_buffer",
            label="Entries Processing Buffer",
            description="How many input values do you want to send per request?",
            advanced=True,
            default_value=100,
        ),
        PluginParameter(
            name="embedding_output_path",
            label="Entity Embedding path (output)",
            description=f"Changing this value will change the output schema accordingly. "
            f"Default: {DEFAULT_EMBEDDING_PATH}",
            advanced=True,
            default_value=DEFAULT_EMBEDDING_PATH,
        ),
        PluginParameter(
            name="embedding_output_text",
            label="Entity Embedding text (output)",
            description=f"Changing this value will change the output schema accordingly. "
            f"Default: {DEFAULT_EMBEDDING_SOURCE_PATH}",
            advanced=True,
            default_value=DEFAULT_EMBEDDING_SOURCE_PATH,
        ),
        PluginParameter(
            name="embedding_paths",
            label="Used entity paths (comma-separated list)",
            description="Changing this value will change, which input paths are used by the "
            "workflow task. A blank value means, all paths are used.",
            advanced=True,
            default_value="text",
        ),
    ],
)
class CreateEmbeddings(WorkflowPlugin):
    """Fetch embeddings from OpenAI embeddings API endpoint"""

    execution_context: ExecutionContext
    embeddings: OpenAIEmbeddings
    entries_processing_buffer: int
    embedding_output_text: str
    embedding_output_path: str
    embedding_paths: list[str]
    embedding_report: ExecutionReport

    def __init__(  # noqa: PLR0913
        self,
        url: str,
        api_key: Password | str = "",
        model: str = MODEL_EXAMPLE,
        timout_single_request: int = 10000,
        entries_processing_buffer: int = 100,
        embedding_paths: str = "",
        embedding_output_text: str = DEFAULT_EMBEDDING_SOURCE_PATH,
        embedding_output_path: str = DEFAULT_EMBEDDING_PATH,
    ) -> None:
        self.base_url = url
        self.timout_single_request = timout_single_request
        self.api_key = api_key if isinstance(api_key, str) else api_key.decrypt()
        if self.api_key == "":
            self.api_key = "dummy-key"
        self.embeddings = OpenAIEmbeddings(
            base_url=url,
            api_key=convert_to_secret_str(self.api_key),
            model=model,
            timeout=timout_single_request,
        )
        self.entries_processing_buffer = entries_processing_buffer
        self.embedding_output_text = embedding_output_text
        self.embedding_output_path = embedding_output_path
        self.embedding_paths = self.input_paths_to_list(embedding_paths)
        self.embedding_report = ExecutionReport()
        self.embedding_report.operation = "create"
        self.embedding_report.operation_desc = "embeddings created"
        self._setup_ports()
        if self.embedding_output_text in self.embedding_paths:
            raise SamePathError(self.embedding_output_text)
        if self.embedding_output_path in self.embedding_paths:
            raise SamePathError(self.embedding_output_path)

    @staticmethod
    def input_paths_to_list(paths: str) -> list[str]:
        """Convert a comma-separated list of strings to a python list of strings."""
        return [] if paths == "" else [_.strip() for _ in paths.split(",")]

    def _setup_ports(self) -> None:
        """Configure input and output ports depending on the configuration"""
        if len(self.embedding_paths) == 0:
            self.input_ports = FixedNumberOfInputs([FlexibleSchemaPort()])
            self.output_port = UnknownSchemaPort()
            return

        input_paths = [EntityPath(path=_) for _ in self.embedding_paths]
        input_schema = EntitySchema(type_uri="entity", paths=input_paths)
        self.input_ports = FixedNumberOfInputs(ports=[FixedSchemaPort(schema=input_schema)])

        output_paths = [
            EntityPath(path=_)
            for _ in [*self.embedding_paths, self.embedding_output_path, self.embedding_output_text]
        ]
        output_schema = EntitySchema(type_uri="entity", paths=output_paths)
        self.output_port = FixedSchemaPort(schema=output_schema)

    def _generate_output_schema(self, input_schema: EntitySchema) -> EntitySchema:
        """Get output schema"""
        paths = list(input_schema.paths).copy()
        paths.append(EntityPath(self.embedding_output_path))
        paths.append(EntityPath(self.embedding_output_text))
        return EntitySchema(type_uri=input_schema.type_uri, paths=paths)

    def workflow_canceling(self) -> bool:
        """Check if the workflow is canceling / cancelled"""
        try:
            if self.execution_context.workflow.status() == "Canceling":
                self.log.info("End task (Cancelled Workflow).")
                return True
        except AttributeError:
            pass
        return False

    def _embedding_report_update(self, n: int) -> None:
        if hasattr(self.execution_context, "report"):
            self.embedding_report.entity_count += n
            self.execution_context.report.update(self.embedding_report)

    @staticmethod
    def chunker(seq: Sequence, size: int) -> Generator[Sequence]:
        """Split a sequence into chunks"""
        chunk = []
        for entry in seq:
            chunk.append(entry)
            if len(chunk) == size:
                yield chunk.copy()
                chunk.clear()
        if len(chunk) > 0:
            yield chunk.copy()

    @staticmethod
    def _entity_to_dict(paths: Sequence[EntityPath], entity: Entity) -> dict[str, list[str]]:
        """Create a dict representation of an entity"""
        entity_dic = {}
        for key, value in zip(paths, entity.values, strict=False):
            entity_dic[key.path] = list(value)
        return entity_dic

    def _process_entities(self, entities: Entities) -> Generator[Entity]:
        """Process an entity list (chunked), yielding new entity objects"""
        self._embedding_report_update(0)
        for entity_chunk in self.chunker(entities.entities, self.entries_processing_buffer):
            embeddings_sources: list[str] = []  # a list of embedding source texts
            entity_dicts: list[dict[str, list[str]]] = []  # a list of entity dictionaries
            entity: Entity
            if self.workflow_canceling():
                break
            for entity in entity_chunk:
                entity_dic = self._entity_to_dict(entities.schema.paths, entity)
                entity_dicts.append(entity_dic)
                if len(entity.values) == 1 and len(entity.values[0]) == 1:
                    embedding_source = entity.values[0][0]
                else:
                    embedding_source = str(entity_dic)
                embeddings_sources.append(embedding_source)
            embeddings: list[list[float]] = self.embeddings.embed_documents(embeddings_sources)
            self._embedding_report_update(len(embeddings_sources))

            # looping over list of embeddings, entity dicts, sources and entities
            for (
                entity_embedding,
                entity_dict,
                embedding_source,
                original_entity,
            ) in zip(
                embeddings,
                entity_dicts,
                embeddings_sources,
                entity_chunk,
                strict=False,
            ):
                # add string repr of the embedding as a single value list
                entity_dict[self.embedding_output_path] = [str(entity_embedding)]
                # add string repr of the embedding source as a single value list
                entity_dict[self.embedding_output_text] = [embedding_source]
                values = list(entity_dict.values())
                yield Entity(uri=original_entity.uri, values=values)

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        self.log.info("Start")
        self.execution_context = context
        first_input: Entities = inputs[0]
        for input_path in [_.path for _ in first_input.schema.paths]:
            if input_path in [self.embedding_output_path, self.embedding_output_text]:
                raise SamePathError(input_path)
        entities = self._process_entities(first_input)
        schema = self._generate_output_schema(first_input.schema)
        self.log.info("End")
        return Entities(entities=entities, schema=schema)
