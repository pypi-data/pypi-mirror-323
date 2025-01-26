import sys
import httpx
import typer
import IPython
import lxml.html
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from typing_extensions import Annotated
from importlib.metadata import version

cli = typer.Typer(help="whsk: web harvesting/scraping toolKit")

VERSION = version("whsk")
_user_agent = f"whsk/{VERSION}"

# Common Options
opt = {
    "user_agent": typer.Option("--ua", help="User agent to make requests with"),
    "postdata": typer.Option(
        "--postdata", "-p", help="POST data (will make a POST instead of GET)"
    ),
    "headers": typer.Option(
        "--header", "-h", help="Additional headers in format 'Name: Value'"
    ),
    "css": typer.Option("--css", "-c", help="css selector"),
    "xpath": typer.Option("--xpath", "-x", help="xpath selector"),
}


def parse_headers(headers: list[str]) -> dict:
    """Parse list of header strings into a dictionary"""
    header_dict = {}
    for header in headers:
        try:
            name, value = header.split(":", 1)
            header_dict[name.strip()] = value.strip()
        except ValueError:
            typer.echo(f"Invalid header format: {header}", fg="red")
            raise typer.Exit(1)
    return header_dict


def make_request(url, headers, postdata):
    header_dict = parse_headers(headers)
    resp = httpx.request("GET", url, headers=header_dict, data=postdata)
    # if resp.headers["content-type"] == "text/html":
    root = lxml.html.fromstring(resp.text)
    return resp, root


def parse_selectors(root, css, xpath):
    # check for a selector
    selected = selector = None
    if css and xpath:
        typer.secho("Cannot specify css and xpath", fg="red")
        raise typer.Exit(1)
    if css:
        selector = css
        selected = root.cssselect(css)
    if xpath:
        selector = xpath
        selected = root.xpath(xpath)
    return selector, selected


@cli.command()
def version():
    pyversion = sys.version.split(" ")[0]
    console = Console()
    console.print(
        Panel(
            f""" 
W   H H H  SS K K
W W W HHH  S  KK
WWWWW H H SS  K K       v{VERSION}
                """.lstrip()
            + f"\npython {pyversion:>23}"
            f"\nipython {IPython.__version__:>22}"
            f"\nlxml.html {lxml.__version__:>20}"
            f"\nhttpx {httpx.__version__:>24}",
            style="cyan",
            expand=False,
        )
    )


@cli.command()
def query(
    url: Annotated[str, typer.Argument(help="URL to scrape")],
    user_agent: Annotated[str, opt["user_agent"]] = _user_agent,
    postdata: Annotated[str, opt["postdata"]] = "",
    headers: Annotated[list[str], opt["headers"]] = [],
    css: Annotated[str, opt["css"]] = "",
    xpath: Annotated[str, opt["xpath"]] = "",
):
    """Run a one-off query against the URL"""
    resp, root = make_request(url, headers, postdata)
    selector, selected = parse_selectors(root, css, xpath)

    for s in selected:
        print(s)


@cli.command()
def shell(
    url: Annotated[str, typer.Argument(help="URL to scrape")],
    user_agent: Annotated[str, opt["user_agent"]] = _user_agent,
    postdata: Annotated[str, opt["postdata"]] = "",
    headers: Annotated[list[str], opt["headers"]] = [],
    css: Annotated[str, opt["css"]] = "",
    xpath: Annotated[str, opt["xpath"]] = "",
):
    """Launch an interactive Python shell for scraping"""

    resp, root = make_request(url, headers, postdata)
    selector, selected = parse_selectors(root, css, xpath)

    console = Console()
    table = Table(
        title="variables",
        show_header=False,
        title_style="bold green",
        border_style="green",
    )
    table.add_row("[green]url[/green]", url)
    table.add_row("[green]resp[/green]", str(resp))
    table.add_row("[green]root[/green]", "lxml.html.Element")
    if selector:
        table.add_row("[green]selector[/green]", selector)
        table.add_row("[green]selected[/green]", f"{len(selected)} elements")
    console.print(table)
    #    typer.secho(f"root: `lxml HTML element` <{root.tag}>", fg="green")
    IPython.embed(
        banner1="",
        banner2="",
        confirm_exit=False,
        colors="neutral",
    )


if __name__ == "__main__":
    cli()
