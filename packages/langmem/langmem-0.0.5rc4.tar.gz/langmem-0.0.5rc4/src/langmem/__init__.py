import asyncio
import typing
import uuid

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage
from langgraph.utils.config import get_store
from pydantic import BaseModel, Field, model_validator
from trustcall import create_extractor
from langmem import utils
from langmem.prompts.looping import (
    create_prompt_optimizer,
    create_multi_prompt_optimizer,
    Prompt,
)
import langsmith as ls


## LangGraph Tools


def create_manage_memory_tool(
    instructions: str = """Proactively call this tool when you:
1. Identify a new USER preference.
2. Receive an explicit USER request to remember something or otherwise alter your behavior.
3. Are working and want to record important context.
4. Identify that an existing MEMORY is incorrect or outdated.""",
    namespace_prefix: tuple[str, ...] = ("memories", "{user_id}"),
):
    namespacer = utils.NamespaceTemplate(namespace_prefix)

    @tool
    async def manage_memory(
        action: typing.Literal["create", "update", "delete"],
        content: typing.Optional[str] = None,
        *,
        id: typing.Optional[uuid.UUID] = None,
    ):
        """Create, update, or delete persistent MEMORIES that will be carried over to future conversations.
        {instructions}"""
        store = get_store()

        if action == "create" and id is not None:
            raise ValueError(
                "You cannot provide a MEMORY ID when creating a MEMORY. Please try again, omitting the id argument."
            )

        if action in ("delete", "update") and not id:
            raise ValueError(
                "You must provide a MEMORY ID when deleting or updating a MEMORY."
            )
        if action == "delete":
            await store.adelete(namespace_prefix, key=str(id))
            return f"Deleted memory {id}"
        namespace = namespacer()
        id = id or uuid.uuid4()
        await store.aput(
            namespace,
            key=str(id),
            value={"content": content},
        )
        return f"{action}d memory {id}"

    manage_memory.__doc__.format(instructions=instructions)

    return manage_memory


_MEMORY_SEARCH_INSTRUCTIONS = (
    """Call this tool to search your long term memory for information."""
)


def create_search_memory_tool(
    instructions: str = _MEMORY_SEARCH_INSTRUCTIONS,
    namespace_prefix: tuple[str, ...] = ("memories", "{user_id}"),
):
    namespacer = utils.NamespaceTemplate(namespace_prefix)

    @tool
    async def search_memory(
        query: str,
        *,
        limit: int = 10,
        offset: int = 0,
        filter: typing.Optional[dict] = None,
    ):
        """Search for MEMORIES stored in the graph.
        {instructions}"""
        store = get_store()
        namespace = namespacer()
        memories = await store.asearch(
            namespace,
            query=query,
            filter=filter,
            limit=limit,
            offset=offset,
        )
        return [m.dict() for m in memories]

    search_memory.__doc__.format(instructions=instructions)  # type: ignore

    return search_memory


def create_thread_extractor(
    model: str,
    schema: typing.Union[None, BaseModel, type] = None,
    instructions: str = "You are tasked with summarizing the following conversation.",
):
    class SummarizeThread(BaseModel):
        """Summarize the thread."""

        title: str
        summary: str

    schema_ = schema or SummarizeThread
    extractor = create_extractor(model, tools=[schema_], tool_choice="any")

    async def summarize_conversation(messages: list[AnyMessage]):
        id_ = str(uuid.uuid4())
        messages = [
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": f"Summarize the conversation below:\n\n"
                f"<conversation_{id_}>\n{utils.get_conversation}\n</conversation_{id_}>",
            },
        ]
        response = await extractor.ainvoke(messages)
        result = response["responses"][0]
        if isinstance(result, schema_):
            return result
        return result.model_dump(mode="json")

    return summarize_conversation


_MEMORY_INSTRUCTIONS = """You are tasked with extracting or upserting memories for all entities, concepts, etc.

Extract all important facts or entities. If an existing MEMORY is incorrect or outdated, update it based on the new information.

"""


@typing.overload
def create_memory_enricher(
    model: str | BaseChatModel,
    /,
    instructions: str = _MEMORY_INSTRUCTIONS,
    enable_inserts: bool = True,
    enable_deletions: bool = False,
) -> typing.Callable[
    [list[AnyMessage], typing.Optional[list[str]]], typing.Awaitable[tuple[str, str]]
]: ...


@typing.overload
def create_memory_enricher(
    model: str | BaseChatModel,
    /,
    schemas: list,
    instructions: str = _MEMORY_INSTRUCTIONS,
    enable_inserts: bool = True,
    enable_deletions: bool = False,
) -> typing.Callable[
    [
        list[AnyMessage],
        typing.Optional[
            typing.Union[
                list[tuple[str, BaseModel]],
                list[tuple[str, str, dict]],
            ]
        ],
    ],
    typing.Awaitable[tuple[str, BaseModel]],
]: ...


def create_memory_enricher(  # type: ignore
    model: str | BaseChatModel,
    /,
    schemas: list | None = None,
    instructions: str = _MEMORY_INSTRUCTIONS,
    enable_inserts: bool = True,
    enable_deletions: bool = False,
):
    model = model if isinstance(model, BaseChatModel) else init_chat_model(model)
    str_type = False
    if schemas is None:

        class Memory(BaseModel):
            """Call this tool to extract memories for things like preferences, instructions, important context, events, and anything else you want to remember about for future conversations."""

            content: str

        schemas = [Memory]
        str_type = True

    @ls.traceable
    async def enrich_memories(
        messages: list[AnyMessage],
        existing: typing.Optional[
            typing.Union[
                list[str],
                list[tuple[str, BaseModel]],
                list[tuple[str, str, dict]],
            ]
        ] = None,
    ):
        id_ = str(uuid.uuid4())
        coerced = [
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": f"Enrich, prune, and organize memories based on the following interaction. If an existing memory is incorrect or outdated, update it based on the new information. "
                f"<session_{id_}>\n{utils.get_conversation(messages)}\n</session_{id_}>",
            },
        ]
        if str_type and existing and all(isinstance(ex, str) for ex in existing):
            existing = [(str(uuid.uuid4()), Memory(content=ex)) for ex in existing]
        existing_keys = [str(ex[0]) for ex in existing] if existing else []

        class RemoveMemory:
            """Use this tool to remove an invalid or redundant memory. To consolidate two memories, Patch the one to retain and call this tool with the keys of the two memories as arguments."""

            json_doc_id: str = Field(
                description=f"The json_doc_id of the memory to remove. Must be one of: {existing_keys}."
            )

            @model_validator(mode="after")
            def validate_keys(cls, values: typing.Any) -> typing.Any:
                if str(values["json_doc_id"]) not in existing_keys:
                    raise ValueError(
                        f"json_doc_id key {values['json_doc_id']} not in existing keyss {existing_keys}"
                    )
                return values

        schemas_ = schemas + ([RemoveMemory] if (enable_deletions and existing) else [])
        extractor = create_extractor(
            model, tools=schemas_, tool_choice="any", enable_inserts=enable_inserts
        )

        response = await extractor.ainvoke({"messages": coerced, "existing": existing})
        result = [
            (rmeta.get("json_doc_id", str(uuid.uuid4())), r)
            for r, rmeta in zip(response["responses"], response["response_metadata"])
        ]
        return result

    return enrich_memories


def create_memory_store_enricher(
    model: str | BaseChatModel,
    *,
    schemas: list | None = None,
    instructions: str = _MEMORY_INSTRUCTIONS,
    enable_inserts: bool = True,
    enable_deletions: bool = True,
    namespace_prefix: tuple[str, ...] = ("memories", "{user_id}"),
):
    model = model if isinstance(model, BaseChatModel) else init_chat_model(model)
    if schemas:
        evolver = create_memory_enricher(
            model,
            schemas=schemas,
            instructions=instructions,
            enable_inserts=enable_inserts,
            enable_deletions=enable_deletions,
        )
    else:
        evolver = create_memory_enricher(
            model,
            instructions=instructions,
            enable_inserts=enable_inserts,
            enable_deletions=enable_deletions,
        )
    search_tool = create_search_memory_tool(namespace_prefix=namespace_prefix)
    query_gen = model.bind_tools(
        [search_tool],
        tool_choice="search_memory",
    )

    namespacer = utils.NamespaceTemplate(namespace_prefix)

    async def manage_memories(messages: list[AnyMessage]):
        store = get_store()
        namespace = namespacer()
        convo = utils.get_conversation(messages)
        msg = await query_gen.ainvoke(
            f"""Generate a search query to retrieve memories based on the conversation: \n\n<convo>\n{convo}\n</convo>."""
        )
        all_search_results = await asyncio.gather(
            *(store.asearch(namespace, **tc["args"]) for tc in msg.tool_calls)
        )
        memories = [
            (r.key, r.value["kind"], r.value["content"])
            for search_results in all_search_results
            for r in search_results
        ]
        new_memories = await evolver(messages, existing=memories)
        deletions, others = [], []
        for key, content in new_memories:
            if content.__repr_name__() == "RemoveMemory":
                deletions.append(key)
            else:
                others.append((key, content))

        put_kwargs = [
            {
                "namespace": namespace,
                "key": key,
                "value": {
                    "kind": content.__repr_name__(),
                    "content": content.model_dump(mode="json"),
                },
            }
            for key, content in others
        ]
        await asyncio.gather(
            *(
                *(
                    store.aput(
                        **kwargs,
                    )
                    for kwargs in put_kwargs
                ),
                *(store.adelete(namespace, key=str(key)) for key in deletions),
            )
        )

        return [kwargs for kwargs in put_kwargs]

    return manage_memories


__all__ = [
    "create_memory_enricher",
    "create_memory_store_enricher",
    "create_manage_memory_tool",
    "create_thread_extractor",
    "create_multi_prompt_optimizer",
    "create_prompt_optimizer",
    "Prompt",
]
