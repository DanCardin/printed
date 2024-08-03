from typing import Annotated

from fastapi import Depends, Form, Request
from fastapi.templating import Jinja2Templates

from printed import print as print_actions
from printed.cli.base import PrintAdd
from printed.schema import State
from printed.web.dependencies import get_template, redirect_to, state, templates


def render(template: str):
    def template_response(
        request: Request,
        state: Annotated[State, Depends(state)],
        templates: Annotated[Jinja2Templates, Depends(templates)],
    ):
        return templates.TemplateResponse(
            request=request,
            name=get_template(request, template),
            context={
                "state": state,
                "query": request.query_params,
                "path": request.path_params,
            },
        )

    template_response.__name__ = template

    return template_response


def delete_print(
    request: Request,
    state: Annotated[State, Depends(state)],
    templates: Annotated[Jinja2Templates, Depends(templates)],
    name: str,
):
    print = state.prints.get(name)
    if print:
        print.delete()

    return redirect_to(request, "print", name=name)


async def add_print(
    request: Request,
    state: Annotated[State, Depends(state)],
    title: Annotated[str, Form()],
):
    command = PrintAdd(title=title)
    print = print_actions.add_print(state, command)

    return redirect_to(request, "print", name=print.name)


async def update_print(
    request: Request,
    state: Annotated[State, Depends(state)],
    name: str,
    source_link_urls: Annotated[
        list[str], Form(alias="source_link_url[]", default_factory=list)
    ],
    source_link_titles: Annotated[
        list[str], Form(alias="source_link_title[]", default_factory=list)
    ],
    reference_cost: Annotated[float, Form()] = 0.0,
    duration: Annotated[str, Form()] = "",
):
    print = state.prints.get(name)
    if print:
        source_links = list(zip(source_link_urls, source_link_titles))
        print.update(
            reference_cost=reference_cost,
            duration=duration,
            source_links=source_links,
        )
        print.write()

    return redirect_to(request, "print", name=name)


def append_history(
    request: Request, state: Annotated[State, Depends(state)], name: str
):
    print = state.prints.get(name)
    if print:
        print.append_history()
        print.write()

    return redirect_to(request, "print", name=name)


def delete_history(
    request: Request, state: Annotated[State, Depends(state)], name: str, number: int
):
    print = state.prints.get(name)
    if print:
        print.delete_history(number)
        print.write()

    return redirect_to(request, "print", name=name)


def append_source_link(
    request: Request, state: Annotated[State, Depends(state)], name: str
):
    print = state.prints.get(name)
    if print:
        print.append_source_link()
        print.write()

    return redirect_to(request, "print", name=name)


def delete_source_link(
    request: Request, state: Annotated[State, Depends(state)], name: str, number: int
):
    print = state.prints.get(name)
    if print:
        print.delete_source_link(number)
        print.write()

    return redirect_to(request, "print", name=name)
