from C import C


class Parser:
    currentCommand = ""
    currentFunction = ""
    commandList = []
    commandType = C.Null
    

    # initialize object
    def __init__(self, inFileName):
        self.file = open(inFileName, "r")


    # gets next command line/parses, returns "~~~" as EOF flag if end of file is reached
    def getNext(self):

        line = "\n"
        while line == "\n" or line[0:2] == "//": # skip newlines and comments
            line = self.file.readline()

        if(line == ""): # EOF base case
            self.currentCommand = "~~~"
            self.file.close()
            return

        if line.find("//") == -1: # only command
            line = line.strip()
            
        else: # has comment
            split = line.split("//") # isolate command
            if(split[0].strip() != ""): # if there is a command
                line = split[0].strip() # strip line

        self.currentCommand = line
        self.commandList = line.split()
        self.getCommandType()


    def getCommandType(self):
        type = ""
        operation = self.commandList[0] # check type
        if operation in ["and", "or", "not", "neg", "add", "sub", "eq", "gt", "lt"]:
            type = C.Arithmetic
        elif operation == "push":
            type = C.Push
        elif operation == "pop":
            type = C.Pop
        elif operation == "label":
            type = C.Label
        elif operation == "goto":
            type = C.Goto
        elif operation == "if-goto":
            type = C.IfGoto
        elif operation == "function":
            type = C.Function
        elif operation == "return":
            type = C.Return
        elif operation == "call":
            type = C.Call
        else:
            print("error: command type unknown")
            exit()

        self.commandType = type
        return type


    # don't call if command type is Return
    def firstArgument(self):
        if self.commandType == C.Arithmetic:
            return self.commandList[0]
        elif self.commandType in [C.Pop, C.Push, C.Label, C.Goto, C.IfGoto, C.Function, C.Call]:
            return self.commandList[1]


    # only call if command type is Push, Pop, Function, or Call
    def secondArgument(self):
        if self.commandType in [C.Pop, C.Push, C.Function, C.Call]:
            return self.commandList[2]