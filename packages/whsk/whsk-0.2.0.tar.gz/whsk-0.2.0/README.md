# whsk

**whsk** (pronounced "whisk") is a command line utility for web scraper authors.

It provides a set of utilities for inspecting HTML responses, and applying selectors against them.

## Installation

It is recommended you install whsk with `uvx` or `pipx`:

`uvx whsk` is the fastest way to get running with `whsk`

It currently consists of two utilities:

## whsk shell

`whsk shell` fetches a page, automatically parsing HTML, XML, or JSON responses.
It then opens an `ipython` shell allowing you to interact with the raw and parsed response.

When the command runs it will print a table of the variables it has loaded (which will depend on the type of page and particular flags passed):

```
$ uvx whsk shell https://example.com 
            variables
┌──────────┬───────────────────────┐
│ url      │ https://example.com   │
│ resp     │ <Response [200 OK]>   │
│ root     │ lxml.html.HtmlElement │
└──────────┴───────────────────────┘

In [1]:
```

The `In[1]`: is an `ipython` prompt, the variables in the table area available for inspection & usage.

If you pass a selector from the command line, that first query will be made for you:

```
$ uvx whsk shell https://example.com --xpath //p
            variables
┌──────────┬───────────────────────┐
│ url      │ https://example.com   │
│ resp     │ <Response [200 OK]>   │
│ root     │ lxml.html.HtmlElement │
│ selector │ //p                   │
│ selected │ 2 elements            │
└──────────┴───────────────────────┘

In [1]:
```

### Options

```
 Usage: whsk shell [OPTIONS] URL                                                        
                                                                                        
 Launch an interactive Python shell for scraping                                        
                                                                                        
╭─ Arguments ──────────────────────────────────────────────────────────────────────────╮
│ *    url      TEXT  URL to scrape [default: None] [required]                         │
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --ua                TEXT  User agent to make requests with                           │
│ --postdata  -p      TEXT  POST data (will make a POST instead of GET)                │
│ --header    -h      TEXT  Additional headers in format 'Name: Value'                 │
│ --css       -c      TEXT  css selector                                               │
│ --xpath     -x      TEXT  xpath selector                                             │
│ --help                    Show this message and exit.                                │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

## whsk query

`whsk query` takes the same command line options as `whsk shell` but instead of opening a shell
will output the results of the `--css` or `--xpath` selection, and then exit immediately.

As such, you must provide *one* of the two selector parameters.

This can be used for rapid testing of queries without opening the shell each time.

### Options

```
Usage: whsk query [OPTIONS] URL                                                                       
                                                                                                       
 Run a one-off query against the URL                                                                   
                                                                                                       
╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────╮
│ *    url      TEXT  URL to scrape [default: None] [required]                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --ua                TEXT  User agent to make requests with                                          │
│ --postdata  -p      TEXT  POST data (will make a POST instead of GET)                               │
│ --header    -h      TEXT  Additional headers in format 'Name: Value'                                │
│ --css       -c      TEXT  css selector                                                              │
│ --xpath     -x      TEXT  xpath selector                                                            │
│ --help                    Show this message and exit.                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Common Parameters

### --ua

This parameter is provided as a shortcut to set common browser "User-Agent" headers.

It must be one of:

- linux.chrome
- linux.firefox
- mac.chrome
- mac.firefox
- mac.safari
- win.chrome
- win.edge
- win.firefox

These will use the values in `user_agents.py`, a relatively recent snapshot of a real user agent for the browser in question.

If you need to set a custom user agent, use `--header 'user-agent: whatever you need'`
