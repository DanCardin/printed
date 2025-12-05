from typing import Annotated

from fastapi import Depends, Form, Request, UploadFile
from fastapi.responses import FileResponse
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
        list[str], Form(alias="source_link_urls[]", default_factory=list)
    ],
    source_link_titles: Annotated[
        list[str], Form(alias="source_link_titles[]", default_factory=list)
    ],
    reference_link_urls: Annotated[
        list[str], Form(alias="reference_link_urls[]", default_factory=list)
    ],
    reference_link_titles: Annotated[
        list[str], Form(alias="reference_link_titles[]", default_factory=list)
    ],
    material_names: Annotated[
        list[str], Form(alias="material_names[]", default_factory=list)
    ],
    material_amounts: Annotated[
        list[float], Form(alias="material_amounts[]", default_factory=list)
    ],
    files: list[UploadFile] | None = None,
    reference_cost: Annotated[float, Form()] = 0.0,
    duration: Annotated[str, Form()] = "",
):
    print = state.prints.get(name)
    if print:
        source_links = list(zip(source_link_urls, source_link_titles))
        reference_links = list(zip(reference_link_urls, reference_link_titles))
        materials = dict(zip(material_names, material_amounts))
        print.update(
            reference_cost=reference_cost,
            duration=duration,
            source_links=source_links,
            reference_links=reference_links,
            materials=materials,
        )
        print.write()

        for file in files or []:
            assert file.filename
            print.add_file(file.filename, file.file)

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


def append_reference_link(
    request: Request, state: Annotated[State, Depends(state)], name: str
):
    print = state.prints.get(name)
    if print:
        print.append_reference_link()
        print.write()

    return redirect_to(request, "print", name=name)


def delete_reference_link(
    request: Request, state: Annotated[State, Depends(state)], name: str, number: int
):
    print = state.prints.get(name)
    if print:
        print.delete_reference_link(number)
        print.write()

    return redirect_to(request, "print", name=name)


def append_print_material(
    request: Request,
    state: Annotated[State, Depends(state)],
    name: str,
    material_name: Annotated[str, Form()],
):
    print = state.prints.get(name)
    if print:
        material = state.materials[material_name]
        print.append_material(material)
        print.write()

    return redirect_to(request, "print", name=name)


def delete_print_material(
    request: Request,
    state: Annotated[State, Depends(state)],
    name: str,
    material_name: str,
):
    print = state.prints.get(name)
    if print:
        print.delete_material(material_name)
        print.write()

    return redirect_to(request, "print", name=name)


def download_print_file(
    request: Request, state: Annotated[State, Depends(state)], name: str, file: str
):
    print = state.prints.get(name)
    if print:
        print_file = print.files[file]
        return FileResponse(print_file.path)

    return redirect_to(request, "print", name=name)
