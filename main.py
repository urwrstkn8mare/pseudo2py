from typing import List
import black
import pathlib


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


def parseValue(val: str):
    for old, new in TO_REPLACE.items():
        val = val.replace(old, new)
    return val.strip()


def parseLines(lines: Lines):
    for line in lines:

        def parseLine(line: str, indent: int = 0) -> str:
            if line.strip() == "":
                return "\n"
            elif line.lstrip().startswith("#"):
                final = line.lstrip()
            else:
                command, rest = line[indent:].split(" ", 1)
                if command == "INPUT":
                    final = f"{rest} = input()"
                elif command == "OUTPUT":
                    final = f"print({rest})"
                elif command == "IF":

                    def parseIf(if_line: str):
                        out = "if " + parseValue(if_line.split("THEN")[0]) + ":\n"

                        def findEnd(out: str):
                            next_line = next(lines)
                            while next_line[indent : indent + 2] in ["  ", ""]:
                                out += parseLine(next_line, indent + 2)
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

                elif rest.startswith("<-"):
                    final = f"{command} = {rest[3:]}"

            return (indent * " ") + final + "\n"

        yield parseLine(line)


with open("in.txt", "rt") as fileIn:
    with open("out.py", "w") as fileOut:
        fileOut.writelines(parseLines(Lines(fileIn.read().split("\n"))))

black.format_file_in_place(
    pathlib.Path("out.py"), True, black.Mode(), black.WriteBack.YES
)

# def parseLine(line: str, lines: str):
#     line = line.rstrip()

#     indented = False
#     converted = None

#     if " " in line:
#         command, params = line.split(" ", 1)
#         if command == "INPUT":
#             pass

#     return {indented, converted}


# def parseLines(lines: List[str]):
#     for i, line in enumerate(lines):
#         print(line)
#         parseLine(line)
#         break


# def main():
#     with open("test.txt", "rt") as f:
#         inFile = Lines(f.read().split("\n"))


# # main()


# lines = Lines([str(i) for i in range(20)])
# for line in lines:
#     if line == "9":
#         print("s", line)
#         for line2 in lines:
#             print("n", line2)
#             if line2 == "15":
#                 break
#     else:
#         print(line)
