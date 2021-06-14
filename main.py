from typing import List
import black
import pathlib
import argparse


# WARNING: this assumes your syntax is correct, if not you'll just have to deal with it


class Lines:
    def __init__(self, lines: List[str]) -> None:
        self.lines = lines
        self.max_i = len(self.lines) - 1
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i > self.max_i:
            raise StopIteration
        self.i += 1
        return self.lines[self.i - 1].rstrip()

    def add(self, lines: List[str], pos: int = None):
        if pos is None:
            self.lines[self.i : self.i] = lines
        else:
            self.lines[pos] = lines
        self.max_i = len(self.lines) - 1


TO_REPLACE = {
    "=": "==",
    "!=": "!=",
    "<": "<",
    "<=": "<=",
    ">": ">",
    ">=": ">=",
    "TRUE": "True",
    "FALSE": "False",
    "AND": "and",
    "OR": "or",
}


def parseLines(lines: Lines):
    for line in lines:

        def parseLine(line: str, *, oneLine=False, indent: int = 0) -> str:
            final = None  # TODO: remove when not important
            if line.strip() == "":
                return "\n"
            elif line.lstrip().startswith("#"):
                final = line.lstrip()
            else:
                command, rest = line[indent:].split(" ", 1)
                for old, new in TO_REPLACE.items():
                    rest = rest.replace(old, new)
                new_rest = ""
                in_brackets = []
                bracket_started = False
                for char in rest:
                    if char == "(" and not bracket_started:
                        in_brackets.append("")
                        new_rest += "%" + str(len(in_brackets) - 1)
                        bracket_started = True
                    elif char == ")" and bracket_started:
                        bracket_started = False
                    elif bracket_started:
                        in_brackets[-1] += char
                    else:
                        new_rest += char
                rest = new_rest.strip()

                if command == "INPUT":
                    final = f"{rest} = input()"
                elif command == "OUTPUT":
                    final = f"print({rest})"
                elif command == "IF" and not oneLine:

                    def parseIf(if_line: str):
                        out = (
                            "if "
                            + if_line[: if_line.find("THEN")].strip()
                            + ":\n"
                        )

                        def findEnd(out: str):
                            next_line = next(lines)
                            while next_line[indent : indent + 2] in ["  ", ""]:
                                out += parseLine(next_line, indent=(indent + 2))
                                next_line = next(lines)
                            last_line = next_line[indent:]
                            if last_line.startswith("ELSE IF"):
                                return out + "el" + parseIf(last_line[8:])
                            elif last_line.startswith("ELSE"):
                                out += "else:\n"
                                return findEnd(out)
                            elif last_line == "END IF":
                                return out

                        return findEnd(out)

                    final = parseIf(rest)
                elif command == "CASE" and not oneLine:
                    toCompare = rest[: rest.find("OF") - 1].strip()
                    print(toCompare)
                    final = ""
                    firstIf = True
                    next_line = next(lines)
                    while True:
                        colon_index = next_line.find(":")
                        if next_line[indent : indent + 4] == "  = ":
                            final += f"{'' if firstIf else 'el'}if {toCompare} == {next_line[indent+4:colon_index].strip()}: {parseLine(next_line[colon_index+1:].strip(), oneLine=True)}"
                            firstIf = False
                        elif next_line[indent : indent + 9] == "  DEFAULT":
                            final += f"else: {parseLine(next_line[colon_index+1:].strip(), oneLine=True)}\n"
                        elif next_line.strip().startswith("#"):
                            final += f"{(indent+2)*' '}{next_line.strip()}\n"
                        elif next_line.strip() == "":
                            final += "\n"
                        else:
                            break
                        next_line = next(lines)
                # elif
                elif rest.startswith("<-"):
                    final = f"{command} = {rest[3:]}"

                for i, in_bracket in enumerate(in_brackets):
                    final = final.replace("%" + str(i), in_bracket)

            # print("-----\n" + line[indent:] + "\n------")
            # print("command: " + command)
            # print("rest: " + rest)

            return (indent * " ") + final + "\n"

        yield parseLine(line)


parser = argparse.ArgumentParser(
    description="Compile SCSA pseudocode to python code."
)
parser.add_argument("inputFile", type=str, help="input file")
parser.add_argument(
    "--run",
    dest="run",
    action="store_const",
    const=True,
    default=False,
    help="use this if you want to immediately run the python program",
)
args = parser.parse_args()

inputPath = pathlib.Path(args.inputFile)
outputPath = inputPath.with_suffix(".out.py")

with open(inputPath, "rt") as fileIn:
    with open(outputPath, "w") as fileOut:
        fileOut.writelines(parseLines(Lines(fileIn.read().split("\n"))))

black.format_file_in_place(outputPath, True, black.Mode(), black.WriteBack.YES)

if args.run:
    from subprocess import call
    from sys import executable

    call([executable, outputPath])
