import os
import datetime
import inspect
# import threading

# THROBBER = ["⠦", "⠇", "⠋", "⠙", "⠸", "⠴"]

class BojanConsole:
    def __init__(self, printing=True, cite_sources=True, log_time=True) -> None:
        self.log = ""
        # self.progress_bar = ProgressBar()
        self.printing = printing
        self.cite_sources = cite_sources
        self.log_time = log_time
        # self.throbber_index = 0
        # self.throbbing = True
        # self.log_throbber()
        # self.thread = threading.Timer(0.1, self.log_throbber)
        # if self.throbbing:
        #     self.thread.start()
        
    # def update_throbber(self):
    #     self.throbber_index += 1
    #     if self.throbber_index >= len(THROBBER):
    #         self.throbber_index = 0
    #     return THROBBER[self.throbber_index]

    # def log_throbber(self):
    #     print(self.update_throbber(), end="\r")
    #     # Call this function every 0.1 seconds
    #     if not self.throbbing:
    #         self.thread.cancel()
    #     print(" ", end="\r")

    def __log_plain(self, message):
        # check whether to print the message to console
        if self.printing:
            print(message)
        
        self.log += message

        # add time to the log
        if self.log_time:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log += f" [{date}]"

        # add caller information to the log
        if self.cite_sources:
            # Get caller information
            caller_frame = inspect.stack()[2]
            caller_file = caller_frame.filename
            caller_line = caller_frame.lineno
            caller_method = caller_frame.function
            caller_class = caller_frame.frame.f_locals.get('self', None).__class__.__name__ if 'self' in caller_frame.frame.f_locals else None
            
            caller_file = caller_file.split("/")[-1]
            caller_file = caller_file.split("\\")[-1]
            
            caller_tree = ""
            if caller_file:
                caller_tree += f"{caller_file}"
            if caller_line:
                caller_tree += f":{caller_line}"
            if caller_class:
                caller_tree += f" > {caller_class}"
            if caller_method:
                caller_tree += f" > {caller_method}"
        
            self.log += f" [{caller_tree}]"
            
        # add a newline to the log
        self.log += "\n"
        
    def print(self, message, identifier="🕸️", depth=0):
        '''
        Print a message to the console with a given identifier and depth of nesting
        '''
        padding = "\t" * depth
        message = padding + identifier + " " + message
        self.__log_plain(message)

    def debug(self, message, depth=0):
        if(type(message) != str):
            message = str(message)
        self.print(color_codes.GREY + message + color_codes.END, "💬", depth=depth)
    
    def error(self, message, depth=0):
        if(type(message) != str):
            message = str(message)
        self.print(color_codes.RED + message + color_codes.END, "❌", depth=depth)
        
    def success(self, message, depth=0):
        if(type(message) != str):
            message = str(message)
        self.print(color_codes.GREEN + message + color_codes.END, "✅", depth=depth)

    def warning(self, message, depth=0):
        if(type(message) != str):
            message = str(message)
        self.print(color_codes.YELLOW + message + color_codes.END, "⚠️", depth=depth)

    def dictionary(self, d, depth=0, depth_emoji=None, cycles=False):
        if depth_emoji is None:
            depth_emoji = ["🏰", "🛖", "🌲", "🐦", "🐛", "🧬"]

        if depth >= len(depth_emoji):
            if cycles: depth = 0
            else: depth = len(depth_emoji) - 1
        
        for key, value in d.items():
            if isinstance(value, dict):
                self.print(f"{color_codes.ITALIC}{color_codes.WHITE if depth == 0 else ''}{key}{color_codes.END}:", depth_emoji[depth], depth)
                self.dictionary(value, depth + 1)
            elif isinstance(value, list):
                self.print(f"{color_codes.ITALIC}{color_codes.WHITE if depth == 0 else ''}{key}{color_codes.END}:", depth_emoji[depth], depth)
                for i, item in enumerate(value):
                    self.dictionary({i: item}, depth + 1)
            else:
                self.print(f"{key}: {value}", depth_emoji[depth], depth)
    
    # def print_parameter(self, section, parameters, icon="🔧"):
    #     self.log_plain(f"{icon} {color_codes.BOLD}{color_codes.YELLOW}{section}{color_codes.END}:")
    #     for key, value in parameters.items():
    #         self.log_plain(f"\t{color_codes.BLUE}{key}{color_codes.END} : {color_codes.BLUE}{value}{color_codes.END}")

    # def print_parameters(self, mappings, settings):
    #     self.log_plain(f"STARTING 🌱 {color_codes.BOLD}{color_codes.GREEN}VELES{color_codes.END}🌱 WITH FOLLOWING PARAMETERS:")
    #     self.print_parameter("Settings", settings, "⚙️")
    #     self.print_parameter("Mappings", mappings, "🗺️")
    
    def strip_colors(self, string):
        return string.replace(color_codes.END, "").replace(color_codes.BOLD, "").replace(color_codes.ITALIC, "").replace(color_codes.URL, "").replace(color_codes.BLINK, "").replace(color_codes.BLINK2, "").replace(color_codes.SELECTED, "").replace(color_codes.BLACK, "").replace(color_codes.RED, "").replace(color_codes.GREEN, "").replace(color_codes.YELLOW, "").replace(color_codes.BLUE, "").replace(color_codes.VIOLET, "").replace(color_codes.BEIGE, "").replace(color_codes.WHITE, "").replace(color_codes.BLACKBG, "").replace(color_codes.REDBG, "").replace(color_codes.GREENBG, "").replace(color_codes.YELLOWBG, "").replace(color_codes.BLUEBG, "").replace(color_codes.VIOLETBG, "").replace(color_codes.BEIGEBG, "").replace(color_codes.WHITEBG, "").replace(color_codes.GREY, "").replace(color_codes.RED2, "").replace(color_codes.GREEN2, "").replace(color_codes.YELLOW2, "").replace(color_codes.BLUE2, "").replace(color_codes.VIOLET2, "").replace(color_codes.BEIGE2, "").replace(color_codes.WHITE2, "").replace(color_codes.GREYBG, "").replace(color_codes.REDBG2, "").replace(color_codes.GREENBG2, "").replace(color_codes.YELLOWBG2, "").replace(color_codes.BLUEBG2, "").replace(color_codes.VIOLETBG2, "").replace(color_codes.BEIGEBG2, "").replace(color_codes.WHITEBG2, "")
    
    def save(self, filename):
        if "/" in filename or "\\" in filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w+", encoding="utf-8") as file:
            file.write(self.strip_colors(self.log))

# class ProgressBar:
#     def __init__(self, total, length=50) -> None:
#         self.total = total
#         self.length = length
#         self.progress = 0
#         self.update(0)
    
#     def update(self, progress):
#         self.progress = progress
    
#     def print(self):
#         progress = int(self.progress/self.total*self.length)
#         print(f"[{'#'*progress}{'-'*(self.length-progress)}] {progress/self.length*100:.2f}%", end="\r")

# thanks to @qubodup for creating the list!
# permalink: https://stackoverflow.com/a/39452138
class color_codes:
    END      = '\33[0m'
    BOLD     = '\33[1m'
    ITALIC   = '\33[3m'
    URL      = '\33[4m'
    BLINK    = '\33[5m'
    BLINK2   = '\33[6m'
    SELECTED = '\33[7m'

    BLACK  = '\33[30m'
    RED    = '\33[31m'
    GREEN  = '\33[32m'
    YELLOW = '\33[33m'
    BLUE   = '\33[34m'
    VIOLET = '\33[35m'
    BEIGE  = '\33[36m'
    WHITE  = '\33[37m'

    BLACKBG  = '\33[40m'
    REDBG    = '\33[41m'
    GREENBG  = '\33[42m'
    YELLOWBG = '\33[43m'
    BLUEBG   = '\33[44m'
    VIOLETBG = '\33[45m'
    BEIGEBG  = '\33[46m'
    WHITEBG  = '\33[47m'

    GREY    = '\33[90m'
    RED2    = '\33[91m'
    GREEN2  = '\33[92m'
    YELLOW2 = '\33[93m'
    BLUE2   = '\33[94m'
    VIOLET2 = '\33[95m'
    BEIGE2  = '\33[96m'
    WHITE2  = '\33[97m'

    GREYBG    = '\33[100m'
    REDBG2    = '\33[101m'
    GREENBG2  = '\33[102m'
    YELLOWBG2 = '\33[103m'
    BLUEBG2   = '\33[104m'
    VIOLETBG2 = '\33[105m'
    BEIGEBG2  = '\33[106m'
    WHITEBG2  = '\33[107m'