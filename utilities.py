import os  # Clear screen
import difflib
import subprocess


def printable_paragraph(string, width):
    if len(string) > width:
        out = ""
        line = ""
        word = ""
        for c in string:
            if len(line) + len(word) > width:
                out += "\n" + line.strip()
                line = ""

            if c == " ":
                line += f" {word}"
                word = ""
            elif c == "\n":
                line += f" {word}"
                word = ""
                out += "\n" + line.strip()
                line = ""
            else:
                word += c

        out += "\n" + (line + " " + word).strip()

        return out
    else:
        return string


def level_prefix(level):
    if level == 0:
        return "Cantrip"
    elif level == 1:
        return "1st Level"
    elif level == 2:
        return "2nd Level"
    elif level == 3:
        return "3rd Level"
    else:
        return f"{level}th Level"


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# Parse a string like "school:evocation time:action"
def parse_spell_query(string):
    string += " "

    queries = {}

    query_shortenings = {
        "n": "name",
        "s": "school",
        "l": "level",
        "c": "cast",
        "r": "range",
        "co": "components",
        "d": "duration",
        "t": "desc",
        "rit": "ritual",
        "range": "range",
        "class": "classes",
        "cls": "classes",
        "cl": "classes",
        "subclass": "subclasses",
        "scls": "subclasses",
        "sc": "subclasses",
    }

    quote = False
    colon = False
    query = ""
    criteria = ""
    for c in string:
        if c == " ":
            if not quote and criteria:
                colon = False

                if query and criteria:
                    if query in query_shortenings:
                        query = query_shortenings[query]
                    queries[query.lower()] = criteria.lower()
                query = ""
                criteria = ""
            elif query in ["rit", "ritual"]:
                queries["ritual"] = "true"
            elif colon and quote:
                criteria += c
        elif c == '"':
            if colon:
                quote = not quote
            else:
                raise ValueError('Format: "search <attribute>:<criteria>".')
        elif c == ":" and not quote:
            colon = True
        else:
            if colon:
                criteria += c
            else:
                query += c

    return queries


def suggest_command(command, commands):
    suggestion = difflib.get_close_matches(command, commands, 1)
    if suggestion:
        suggestion = suggestion[0]
    return suggestion


def capitalise(string):
    words = string.split(" ")
    return " ".join([w.capitalize() for w in words])


def replace_unicode(string):
    return (
        string.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u2013", "-")
    )


def punctuate_list(l):
    if len(l) > 1:
        return f"{', '.join(l[:-1])} and {l[-1]}"
    elif len(l):
        return l[0]
    return ""


def exec_shell_stdout(command, check=True):
    return subprocess.run(
        command, capture_output=True, check=check, shell=True
    ).stdout.decode()


def exec_shell_returncode(command):
    return subprocess.call(command, shell=True, stdout=subprocess.DEVNULL)


def program_available(program):
    # Source: https://stackoverflow.com/a/27394096
    NT_CHECK_COMMAND = (
        'cmd /c "(help {0} > nul || exit 0) && where {0} > nul 2> nul'
    )

    POSIX_CHECK_COMMAND = "command -v {}"

    if os.name == "nt":
        command = NT_CHECK_COMMAND
    elif os.name == "posix":
        command = POSIX_CHECK_COMMAND
    else:
        print("Unsupported operating system.")
        return False

    try:
        return not exec_shell_returncode(command.format(program))
    except:
        return False


def mod_str(mod):
    if mod > 0:
        return f"(+{mod})"
    else:
        return f"({mod})"


def func_options(options):
    """
    Given a list [(title, func)], print out the numbered titles and return the
    context options update.
    """
    titles = []
    funcs = []
    for title, func in options:
        titles.append(title)
        funcs.append(func)

    print("\n" + " ".join(f"[{i + 1}] {t}" for i, t in enumerate(titles)))
    return ("func", funcs)
