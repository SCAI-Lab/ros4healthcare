from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import message_dialog, ProgressBar
from prompt_toolkit.completion import NestedCompleter, WordCompleter, DynamicCompleter, DummyCompleter
from collections import defaultdict, OrderedDict
from inspect import signature
from corsano import CorsanoInterface
from util import check_crc, FileNames
from commands import commands, FW_SET_WAKE_UP, CMD_UNKNOWN
from enum import Enum
import datetime

class BottomBar:
    data = defaultdict(lambda: "")
    invalidate = None
    def update(self, cmd, data):
        if isinstance(cmd, FW_SET_WAKE_UP):
            self.data = defaultdict(lambda: "", data)
        elif isinstance(cmd, CMD_UNKNOWN):
            pass
        if self.invalidate:
            self.invalidate()
    def bottom_toolbar(self):
        return HTML(
            f'Corsano iface - B:{self.data["battery"]}% PPG:{self.data["ppg_size"]} '
            f'Act:{self.data["act_size"]} HRV:{self.data["hrv_size"]} '
            f'Workout:{self.data["workout_size"]} Sleep:{self.data["sleep_size"]} '
            f'Log:{self.data["log_size"]} D:{str(self.data["debug"])}'
        )
    def set_invalidate(self, instance):
        self.invalidate = instance
    def print(self, data):
        self.data["debug"] = data
        if self.invalidate:
            self.invalidate()

class RightPrompt:
    text = ""
    def update(self, text):
        self.text = text
    def set_invalidate(self, instance):
        self.invalidate = instance
    def get(self):
        if len(self.text) > 0:
            return f'<{self.text}>'
        else:
            return ''
        if self.invalidate:
            self.invalidate()

class Autocompleter:
    def __init__(self, rprompt, cmd_dict):
        self.rprompt = rprompt
        self.cmd_dict = cmd_dict
        self.commands_completer = WordCompleter(list(self.cmd_dict.keys()))
        self.completer = NestedCompleter.from_nested_dict({
            'help': None,
            'exec': None,
            'text': None,
            'exit': None,
            'stack': None,
            'buffer': None,
            'set_localtime': None,
            'rm': None,
            'ls': None,
            'get': None,
        })
    def autocompleter(self, document, complete_event):
        #print(document, complete_event)
        if len(document.text) == 0:
            return self.completer
        l = ' '.join(document.text.split()).split() # remove extra spaces and split
        if len(l) == 0:
            self.rprompt.update("")
        elif l[0] == "exec":
            if len(l) <= 1:
                self.rprompt.update("command")
                return self.commands_completer
            elif l[1] in self.cmd_dict:
                if len(signature(self.cmd_dict[l[1]].execute).parameters) == 0:
                    self.rprompt.update("")
                else:
                    parameters = signature(self.cmd_dict[l[1]].execute).parameters
                    if len(parameters) > (len(l) - 2):
                        param = list(parameters.items())[len(l)-2]
                        name = param[0]
                        m_type = param[1].annotation
                        self.rprompt.update(name)
                        if type(m_type) == type(Enum):
                            return WordCompleter([el.name for el in m_type])
                    else:
                        self.rprompt.update("")
        elif l[0] == "rm":
            return WordCompleter([el.name for el in FileNames])
        elif l[0] == "get":
            if len(l) > 1:
                self.rprompt.update("output filename")
                return DummyCompleter()
            return WordCompleter([el.name for el in FileNames])
        elif l[0] == "help":
            if len(l) < 2:
                self.rprompt.update("command")
                return self.commands_completer
        return DummyCompleter()

def get_completions(self, document, complete_event):
    completer = self.get_completer(document, complete_event) or DummyCompleter()
    return completer.get_completions(document, complete_event)

async def get_completions_async(self, document, complete_event):
    completer = self.get_completer(document, complete_event) or DummyCompleter()

    async for completion in completer.get_completions_async(
            document, complete_event):
        yield completion

def main(args = None):
    dev = "c4:8d:e7:96:bd:ad" # Heba
    #dev = "d2:10:73:90:52:6c" # Ricardo
    b_bar = BottomBar()
    cors = CorsanoInterface(dev)
    while cors.connect() is False:
        print("Connection failed. Trying again")
    
    rprompt = RightPrompt()

    file_completer = WordCompleter([x.name for x in FileNames])
    type_to_command = {type(v).__name__:v for v in cors.commands.values()}
    commands_completer = WordCompleter(list(type_to_command.keys()))
    
    main_completer = Autocompleter(rprompt, type_to_command)
    
    m_completer = DynamicCompleter(main_completer.autocompleter)
    
    m_completer.get_completions = get_completions.__get__(m_completer, DynamicCompleter)
    m_completer.get_completions_async = get_completions_async.__get__(m_completer, DynamicCompleter)

    cors.register_ping(b_bar)
    if cors:
        session = PromptSession()
        b_bar.set_invalidate(session.app.invalidate)
        rprompt.set_invalidate(session.app.invalidate)
        while True:
            try:
                text = session.prompt("corsano> ", completer=m_completer, bottom_toolbar=b_bar.bottom_toolbar, rprompt=rprompt.get)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            else:
                rprompt.update("")
                l = ' '.join(text.split()).split() # remove extra spaces and split
                if text == "dialog":
                    message_dialog(title="Hola", text="Esta es una prueba\n con dos lineas!").run()
                elif text == "text":
                    if buff := cors.get_buffer():
                        try:
                            message_dialog(title="Text Buffer", text=buff.read().decode("UTF-8")).run()
                        except UnicodeDecodeError:
                            print("Buffer is not text, try buffer command")
                if len(l) == 0:
                    pass
                elif l[0] == "help":
                    if len(l) == 1:
                        print("this is the main help")
                    else:
                        try:
                            print(type_to_command[l[1]].__doc__)
                        except KeyError:
                            print("Command not found!")
                elif l[0] == "exec":
                    try:
                        cmd = type_to_command[l[1]]
                        if len(signature(cmd.execute).parameters) > 0:
                            arguments = OrderedDict()
                            try:
                                for i, (name, _class) in enumerate(signature(cmd.execute).parameters.items()):
                                    if type(_class.annotation) == type(Enum):
                                        arguments[name] = _class.annotation[l[i+2]]
                                    else:
                                        arguments[name] = _class.annotation(l[i+2])
                            except ValueError as e:
                                print("Syntax Error:", e)
                            except KeyError as e:
                                print(f"Invalid value {e} for enumeration: {_class.annotation.__name__}")
                            except IndexError as e:
                                print("Not enough parameters\nsee: help " + type(cmd).__name__)
                            except Exception as e:
                                print("Unkown exception:", e)
                                import traceback; print(traceback.format_exc())
                            else:
                                if hasattr(cmd, "str"):
                                    print(cmd.str(cors.execute(cmd.cmd, **arguments)))
                                else:
                                    print(cors.execute(cmd.cmd, **arguments))
                        else:
                            if hasattr(cmd, "str"):
                                print(cmd.str(cors.execute(cmd.cmd)))
                            else:
                                print(cors.execute(cmd.cmd))
                    except (KeyError, IndexError):
                        print("Command not found!")
                elif l[0] == "set_localtime":
                    utctime = datetime.datetime.utcnow()
                    timezone = datetime.datetime.now().astimezone().tzinfo
                    utcoffset = int(timezone.utcoffset(utctime).total_seconds() / 60)
                    cmd = type_to_command["APP_CMD_UPDATE_TIME"]
                    cors.execute(
                        cmd.cmd,
                        year=utctime.year,
                        month=utctime.month,
                        day=utctime.day,
                        hour=utctime.hour,
                        minute=utctime.minute,
                        seconds=utctime.second,
                        utc_offset=utcoffset,
                    )
                elif l[0] == "ls":
                    cmd = type_to_command["CMD_GET_FILE_SIZE"]
                    for f in FileNames:
                        f_data = cors.execute(cmd.cmd, file=f)
                        print(f"{f_data['file'].name:30} {f_data['size']}")
                elif l[0] == "rm":
                    cmd = type_to_command["CMD_GET_FILE_SIZE"]
                    try:
                        data = cors.execute(cmd.cmd, file=FileNames[l[1]])
                        cmd = type_to_command["CMD_ERASE_FROM_FILE"]
                        cors.execute(cmd.cmd, file=FileNames[l[1]], size=data["size"])
                    except KeyError as e:
                        print("File type not found")
                elif l[0] == "get":
                    cmd = type_to_command["CMD_GET_FILE_SIZE"]
                    try:
                        size = cors.execute(cmd.cmd, file=FileNames[l[1]])["size"]
                        if size <= 0:
                            print("File has no data")
                            continue
                        if type(l[2]) is not str:
                            print("Output filename not provided")
                            continue
                    except KeyError:
                        print("File type not found")
                    except IndexError:
                        print("Incorrect number of parameters")
                    else:
                        cmd = type_to_command["CMD_START_STREAMING_FILE"]
                        cors.execute(cmd.cmd, file=FileNames[l[1]])
                        with ProgressBar() as pb:
                            counter = pb(total=size)
                            for i in cors.block():
                                counter.items_completed = i
                        with open(l[2], "wb") as f:
                            f.write(cors.get_buffer().read())
                elif l[0] == "buffer":
                    print(cors.get_buffer().read())
                elif l[0] == "stack":
                    print(cors.stack)
                elif l[0] == "exit":
                    break
                else:
                    print("You entered:", text)


if __name__ == "__main__":
    main()