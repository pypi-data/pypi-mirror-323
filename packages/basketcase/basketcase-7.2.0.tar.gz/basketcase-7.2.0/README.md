# BasketCase
Download images and videos from Instagram.

Notable features:
- Stories can be downloaded without triggering the "seen" flag.
- Downloads a high quality version of a profile picture.

["Green Day - Basket Case" on YouTube](https://www.youtube.com/watch?v=NUTGr5t3MoY) ;)

## Installation methods
### pipx
The author prefers [pipx](https://pipx.pypa.io/stable/), which greatly simplifies
user installations while avoiding conflicts with the system.
```sh
pipx install basketcase
```

### venv
Or you could simply install it in a virtual environment created with `venv`.
```sh
pip install basketcase
```

I would keep mine at `~/.venv`, then I'd use a shell alias to quickly activate it.

### zipapp
A pre-built executable for Linux is provided with the releases, and you can just put it in your `PATH`.

### User install
Finally, you can install it from [PyPI](https://pypi.org/project/basketcase/) as a [user install](https://pip.pypa.io/en/stable/user_guide/#user-installs).
But be aware that some operating systems forbid this practice.

```sh
pip install --user basketcase
```

## Command-line usage
```sh
basketcase -u "https://instagram.com/p/<post_id>"
```

> Downloaded resources will be stored in the current working directory by default. Override with the `--output` option.

To download from multiple URLs, create a text file (e.g. `urls.txt`)
and populate it with resource URLs:

```
https://instagram.com/p/<post_id>
https://instagram.com/reel/<reel_id>
https://instagram.com/<username>
```

```sh
basketcase -f ./urls.txt
```

See `--help` for more info.

### Supported URLs
| Supported URL                                              | Description                                                                      |
|------------------------------------------------------------|----------------------------------------------------------------------------------|
| `https://instagram.com/<username>`                         | User profile. Downloads stories from the past 24 hours, and the profile picture. |
| `https://instagram.com/p/<post_id>`                        | Standard feed post                                                               |
| `https://instagram.com/reel/<reel_id>`                     | Reels movie                                                                      |
| `https://instagram.com/stories/highlights/<highlight_id>/` | A collection of stories, or "highlights"                                         |
| `https://instagram.com/s/<code>`                           | An alternative URL commonly used for highlighted stories                         |
| `https://instagram.com/tv/<code>`                          | Similar to reels                                                                 |

### Authentication
Add a session cookie.
```sh
basketcase --cookie <session_cookie_id> --cookie-name "my session"
# Added session id: 1
```

Specify its identifier when downloading.
```sh
basketcase -s 1
```

> List all available sessions with `basketcase -l`.
> 
> To disable sessions, use `--no-session`.
> 
> If only one exists, it is treated as the default.

## User data
Cookies and other application data are kept in your home directory (i.e. `~/.basketcase`).

## Known limitations
This program relies on the APIs used by the web browser Instagram client, which can change without a notice.

To discover and run all tests in this project, activate the project _venv_, `cd` to the project root
and run `python -m unittest`. Test coverage is still low and needs some effort.

### Multiple authors, owner is private
Fails to locate a suitable extractor for a standard feed post with multiple authors, in which
the owner - or main author - has a private profile you cannot see.

## Development setup
This project uses [pipenv](https://pipenv.pypa.io/en/latest/index.html) for dependency and virtual environment
management, so make sure it's installed. [pipx](https://pipx.pypa.io/stable/) is a convenient tool to manage
your virtual-environment user installations, and it can be used to install pipenv.

`cd` to the project root, then run `pipenv install --dev`.

### Package build and upload
First, increment the version in `pyproject.toml`.

Then build the package.
```sh
python -m build
```

Commit and push the changes (and a new version tag) to the git repository.

Finally, publish it.
```sh
python -m twine upload dist/*
```

### Build an executable
With the [zipapp](https://docs.python.org/3/library/zipapp.html#creating-standalone-applications-with-zipapp) module
we can build the whole package as an executable file for Linux. The only
runtime requirement is Python 3.

1. `cd` to the project root.
2. Activate the virtual environment.
3. Run `sh zipapp.sh`.

The executable file `basketcase` is in the `dist` folder.
