# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from lionagi.libs.schema.as_readable import as_readable
from lionagi.operatives.types import Instruct
from lionagi.service.imodel import iModel
from lionagi.utils import copy

from .utils import Analysis, ReActAnalysis

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def ReAct(
    branch: "Branch",
    instruct: Instruct | dict[str, Any],
    interpret: bool = False,
    interpret_domain: str | None = None,
    interpret_style: str | None = None,
    interpret_sample: str | None = None,
    interpret_model: str | None = None,
    interpret_kwargs: dict | None = None,
    tools: Any = None,
    tool_schemas: Any = None,
    response_format: type[BaseModel] | BaseModel = None,
    extension_allowed: bool = True,
    max_extensions: int | None = 3,
    response_kwargs: dict | None = None,
    return_analysis: bool = False,
    analysis_model: iModel | None = None,
    verbose_analysis: bool = False,
    verbose_length: int = None,
    **kwargs,
):

    # If no tools or tool schemas are provided, default to "all tools"
    if not tools and not tool_schemas:
        tools = True

    # Possibly interpret the instruction to refine it
    instruction_str = None
    if interpret:
        instruction_str = await branch.interpret(
            str(
                instruct.to_dict()
                if isinstance(instruct, Instruct)
                else instruct
            ),
            domain=interpret_domain,
            style=interpret_style,
            sample_writing=interpret_sample,
            interpret_model=interpret_model,
            **(interpret_kwargs or {}),
        )
        if verbose_analysis:
            print("\n### Interpreted instruction:\n")
            as_readable(
                instruction_str,
                md=True,
                format_curly=True,
                display_str=True,
                max_chars=verbose_length,
            )
            print("\n----------------------------\n")

    # Convert Instruct to dict if necessary
    instruct_dict = (
        instruct.to_dict()
        if isinstance(instruct, Instruct)
        else dict(instruct)
    )

    # Overwrite "instruction" with the interpreted prompt (if any) plus a note about expansions
    max_ext_info = f"\nIf needed, you can do up to {max_extensions or 0 if extension_allowed else 0} expansions."
    instruct_dict["instruction"] = (
        instruction_str
        or (instruct_dict.get("instruction") or "")  # in case it's missing
    ) + max_ext_info

    # Prepare a copy of user-provided kwargs for the first operate call
    kwargs_for_operate = copy(kwargs)
    kwargs_for_operate["actions"] = True
    kwargs_for_operate["reason"] = True

    # Step 1: Generate initial ReAct analysis
    analysis: ReActAnalysis = await branch.operate(
        instruct=instruct_dict,
        response_format=ReActAnalysis,
        tools=tools,
        tool_schemas=tool_schemas,
        chat_model=analysis_model or branch.chat_model,
        **kwargs_for_operate,
    )
    analyses = [analysis]

    # If verbose, show round #1 analysis
    if verbose_analysis:
        print("\n### ReAct Round No.1 Analysis:\n")
        as_readable(
            analysis,
            md=True,
            format_curly=True,
            display_str=True,
            max_chars=verbose_length,
        )
        print("\n----------------------------\n")

    # Validate and clamp max_extensions if needed
    if max_extensions and max_extensions > 100:
        logging.warning(
            "max_extensions should not exceed 100; defaulting to 100."
        )
        max_extensions = 100

    # Step 2: Possibly loop through expansions if extension_needed
    extensions = max_extensions
    round_count = 1

    while (
        extension_allowed
        and analysis.extension_needed
        and (extensions if max_extensions else 0) > 0
    ):
        new_instruction = None
        if extensions == max_extensions:
            new_instruction = ReActAnalysis.FIRST_EXT_PROMPT.format(
                extensions=extensions
            )
        else:
            new_instruction = ReActAnalysis.CONTINUE_EXT_PROMPT.format(
                extensions=extensions
            )

        operate_kwargs = copy(kwargs)
        operate_kwargs["actions"] = True
        operate_kwargs["reason"] = True
        operate_kwargs["response_format"] = ReActAnalysis
        operate_kwargs["action_strategy"] = analysis.action_strategy
        if analysis.action_batch_size:
            operate_kwargs["action_batch_size"] = analysis.action_batch_size

        analysis = await branch.operate(
            instruction=new_instruction,
            tools=tools,
            tool_schemas=tool_schemas,
            **operate_kwargs,
        )
        analyses.append(analysis)
        round_count += 1

        # If verbose, show round analysis
        if verbose_analysis:
            print(f"\n### ReAct Round No.{round_count} Analysis:\n")
            as_readable(
                analysis,
                md=True,
                format_curly=True,
                display_str=True,
                max_chars=verbose_length,
            )
            print("\n----------------------------\n")

        if extensions:
            extensions -= 1

    # Step 3: Produce final answer by calling branch.instruct with an answer prompt
    answer_prompt = ReActAnalysis.ANSWER_PROMPT.format(
        instruction=instruct_dict["instruction"]
    )
    if not response_format:
        response_format = Analysis

    out = await branch.operate(
        instruction=answer_prompt,
        response_format=response_format,
        **(response_kwargs or {}),
    )
    if isinstance(out, Analysis):
        out = out.analysis

    if verbose_analysis:
        print("\n### ReAct Response:\n")
        as_readable(
            analysis,
            md=True,
            format_curly=True,
            display_str=True,
            max_chars=verbose_length,
        )
        print("\n----------------------------\n")

    if return_analysis:
        return out, analyses
    return out


# TODO: Do partial intermeditate output for longer analysis with form and report
