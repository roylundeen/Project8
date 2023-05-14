from C import C

# stack/SP  0
# local/LCL 1
# argument/ARG 2
# this/THIS 3
# that/THAT 4

class Writer:


    def __init__(self, outFileName, parser):
        self.file = open(outFileName, "w")
        self.parser = parser
        self.counter = 0

        # isolate root
        self.root = outFileName.split(".", 1)[0] # split .asm
        self.root = self.root.rsplit('\\', 1)[1] # split relative path

        # initialization
        self.file.write("@256\n")
        self.file.write("D=A\n")
        self.file.write("@SP\n")
        self.file.write("M=D\n")
        self.parser.currentFunction = "Sys.init"
        self.writeCall("Sys.init", 0)
        # self.file.write("(INITIALIZE)\n")
        # self.file.write("@INITIALIZE\n")
        # self.file.write("0;JMP\n")
        

    def writeNext(self):
        self.file.write("//" + self.parser.currentCommand + "\n") # comment which command is being written
        if(self.parser.commandType == C.Arithmetic):
            self.writeArithmetic(self.parser.firstArgument())
        elif self.parser.commandType == C.Push:
            self.writePush()
        elif self.parser.commandType == C.Pop:
            self.writePop()
        elif self.parser.commandType == C.Label:
            self.writeLabel(self.parser.firstArgument())
        elif self.parser.commandType == C.Goto:
            self.writeGoto(self.parser.firstArgument())
        elif self.parser.commandType == C.IfGoto:
            self.writeIfGoto(self.parser.firstArgument())
        elif self.parser.commandType == C.Function:
            self.writeFunction(self.parser.firstArgument(), self.parser.secondArgument())
        elif self.parser.commandType == C.Return:
            self.writeReturn()
        elif self.parser.commandType == C.Call:
            self.writeCall(self.parser.firstArgument(), self.parser.secondArgument())


    def writeArithmetic(self, command):
        operation = ""
        if(command == "add"):
            operation = "+"
            self.writeTwoOperandArithmetic(operation)
        elif(command == "sub"):
            operation = "-"
            self.writeTwoOperandArithmetic(operation)
        elif(command == "and"):
            operation = "&"
            self.writeTwoOperandArithmetic(operation)
        elif(command == "or"):
            operation = "|"
            self.writeTwoOperandArithmetic(operation)
        elif(command == "neg"):
            operation = "-"
            self.writeOneOperandArithmetic(operation) # one
        elif(command == "not"):
            operation = "!"
            self.writeOneOperandArithmetic(operation) # one
        elif(command == "lt"):
            self.writeLT()
        elif(command == "gt"):
            self.writeGT()
        elif(command == "eq"):
            self.writeEQ()
        else:
            print("unknown command", command)
            exit()


    def writeOneOperandArithmetic(self, operation):
        self.popD()
        self.file.write("D=" + operation + "D\n")
        self.pushD()


    def writeTwoOperandArithmetic(self, operation):
        self.popD()
        
        # R13 = D
        self.file.write("@R13\n") 
        self.file.write("M=D\n")
        
        self.popD()

        # D = R13 + D
        self.file.write("@R13\n")
        self.file.write("D=D" + operation + "M\n")
        
        self.pushD()


    def writeEQ(self):
        self.popD()

        # copy D to y = R13
        self.file.write("@R13\n") 
        self.file.write("M=D\n")

        self.popD() # D = x

        self.file.write("@R13\n")
        self.file.write("D=D-M\n")
        self.file.write("@EQUAL" + str(self.counter) + "\n")
        self.file.write("D;JEQ\n")

        self.file.write("@SP\n") # runs if D != 0
        self.file.write("D=A\n")
        self.file.write("@END" + str(self.counter) + "\n") # load END
        self.file.write("D;JMP\n") # jump to END

        self.file.write("(EQUAL" + str(self.counter) + ")\n")
        self.file.write("@SP\n")
        self.file.write("D=A-1\n")

        self.file.write("(END" + str(self.counter) + ")\n")
        self.pushD()
        self.counter += 1


    def writeGT(self): # opposite of writeLT (y then x)
        self.popD()

        # copy D to y = R13
        self.file.write("@R13\n") 
        self.file.write("M=D\n")

        self.popD() # D = x

        self.file.write("@R13\n")
        self.file.write("D=M-D\n")
        self.file.write("@32767\n") 
        self.file.write("A=A+1\n") # A = 0x8000
        self.file.write("D=D&A\n")
        self.file.write("@GREATER" + str(self.counter) + "\n")
        self.file.write("D;JEQ\n")
        self.file.write("D=D-1\n")
        self.file.write("@32767\n") 
        self.file.write("A=A+1\n") # A = 0x8000
        self.file.write("D=D+A\n")
        self.file.write("(GREATER" + str(self.counter) + ")\n")
        self.pushD()
        self.counter += 1


    def writeLT(self):
        self.popD()

        # R13 = D
        self.file.write("@R13\n") 
        self.file.write("M=D\n")

        self.popD() # D = x

        self.file.write("@R13\n")
        self.file.write("D=D-M\n")
        self.file.write("@32767\n") 
        self.file.write("A=A+1\n") # A = 0x8000
        self.file.write("D=D&A\n")
        self.file.write("@LESS" + str(self.counter) + "\n")
        self.file.write("D;JEQ\n")
        self.file.write("D=D-1\n")
        self.file.write("@32767\n") 
        self.file.write("A=A+1\n") # A = 0x8000
        self.file.write("D=D+A\n")
        self.file.write("(LESS" + str(self.counter) + ")\n")
        self.pushD()
        self.counter += 1


    def writePush(self):
        if self.parser.firstArgument() == "constant":
            self.file.write("@" + str(self.parser.secondArgument()) + "\n")
            self.file.write("D=A\n")
        elif self.parser.firstArgument() in ["local", "this", "that", "argument"]:
            self.getAddress(self.parser.firstArgument(), self.parser.secondArgument())
            self.file.write("D=M\n")
        elif self.parser.firstArgument() == "static":
            self.file.write("@" + self.root + "." + self.parser.secondArgument() + "\n")
            self.file.write("D=M\n")
        else:
            if self.parser.firstArgument() == "temp":
                mem = str(5 + int(self.parser.secondArgument()))
            elif self.parser.firstArgument() == "pointer" :
                 mem = str(3 + int(self.parser.secondArgument()))
            else:
                mem = "SP"
            self.file.write("@" + mem + "\n")
            self.file.write("D=M\n")
        self.pushD()


    def writePop(self):
        where = self.parser.firstArgument()
        offset = self.parser.secondArgument()
        if where in ["local", "this", "that", "argument"]:
            self.getAddress(where, offset)

            # R13 = address of segment + offset
            self.file.write("D=A\n")
            self.file.write("@R13\n")
            self.file.write("M=D\n")

            self.popD()

            # address at R13 = D
            self.file.write("@R13\n")
            self.file.write("A=M\n")
            self.file.write("M=D\n")    
        elif where == "static":
             self.popD()
             self.file.write("@" + self.root + "." + offset + "\n")
             self.file.write("M=D\n")
        else:
            if where == "temp":
                mem = str(5 + int(offset))
            elif where == "pointer": 
                mem = str(3 + int(offset))
            self.popD()
            self.file.write("@" + mem + "\n")
            self.file.write("M=D\n")


    def writeLabel(self, label):
        self.file.write("(" + label + ")\n")

    
    def writeGoto(self, label):
        self.file.write("@" + label + "\n")
        self.file.write("0;JMP\n")


    def writeIfGoto(self, label):
        self.popD()
        self.file.write("@" + label + "\n")
        self.file.write("D;JNE\n")


    def writeFunction(self, function, num):
        self.parser.currentFunction = function
        self.file.write("(" + function + ")\n")
        self.file.write("@SP\n")
        self.file.write("D=A\n")
        for i in range(int(num)):
            self.pushD()

    
    def writeReturn(self):
        # stack/SP  0
        # local/LCL 1
        # argument/ARG 2
        # this/THIS 3
        # that/THAT 4

        # Store address in LCL to temp location (FRAME)
        self.file.write("@LCL\n")
        self.file.write("D=M\n")
        self.file.write("@R11\n")
        self.file.write("M=D\n")

        # Store ra (5) in different temp location (RET)
        self.file.write("@5\n")
        self.file.write("A=D-A\n")
        self.file.write("D=M\n")
        self.file.write("@R12\n")
        self.file.write("M=D\n")

        # Copy return value from stack to ARG address (2)
        self.popD()
        self.file.write("@ARG\n")
        self.file.write("A=M\n")   
        self.file.write("M=D\n")

        # SP = ARG + 1 to pop whole stack frame
        self.file.write("D=A+1\n")
        self.file.write("@SP\n")
        self.file.write("M=D\n")

        # Restore
        # THAT: address in FRAME - 1
        self.file.write("@R11\n")
        self.file.write("AM=M-1\n")
        self.file.write("D=M\n")
        self.file.write("@THAT\n")
        self.file.write("M=D\n")

        # THIS: address in FRAME – 2
        self.file.write("@R11\n")
        self.file.write("AM=M-1\n")
        self.file.write("D=M\n")
        self.file.write("@THIS\n")
        self.file.write("M=D\n")

        # ARG: address in FRAME – 3
        self.file.write("@R11\n")
        self.file.write("AM=M-1\n")
        self.file.write("D=M\n")
        self.file.write("@ARG\n")
        self.file.write("M=D\n")

        # LCL: address in FRAME – 4
        self.file.write("@R11\n")
        self.file.write("AM=M-1\n")
        self.file.write("D=M\n")
        self.file.write("@LCL\n")
        self.file.write("M=D\n")

        # RET
        self.file.write("@R12\n")
        self.file.write("A=M\n")
        self.file.write("0;JMP\n")


    def writeCall(self, name, arguments):
        # Push ra
        returnAddress = self.parser.currentFunction + str(self.counter)
        self.counter += 1

        self.file.write("@" + returnAddress + "\n")
        self.file.write("D=A\n")
        self.pushD()

        # 2. Push LCL
        self.file.write("@LCL\n")
        self.file.write("D=M\n")
        self.pushD()

        # 3. Push ARG
        self.file.write("@ARG\n")
        self.file.write("D=M\n")
        self.pushD()

        # 4. Push THIS
        self.file.write("@THIS\n")
        self.file.write("D=M\n")
        self.pushD()

        # 5. Push THAT
        self.file.write("@THAT\n")
        self.file.write("D=M\n")
        self.pushD()

        # 6. ARG = SP – #arguments – 5 
        self.getSP()
        self.file.write("D=A\n")
        self.file.write("@" + str(arguments) + "\n")
        self.file.write("D=D-A\n")
        self.file.write("@5\n")
        self.file.write("D=D-A\n")
        self.file.write("@ARG\n")
        self.file.write("M=D\n")

        # LCL = SP
        self.getSP()
        self.file.write("D=A\n")
        self.file.write("@LCL\n")
        self.file.write("M=D\n")

        # Goto
        self.file.write("@" + name + "\n")
        self.file.write("0;JMP\n")

        # Write return address label
        self.file.write("(" + returnAddress + ")\n")


    def getSP(self):
        self.file.write("@SP\n")
        self.file.write("A=M\n")
    

    def getAddress(self, where, offset = -1):
        # stack/SP  0
        # local/LCL 1
        # argument/ARG 2
        # this/THIS 3
        # that/THAT 4
        address = "SP"
        if where == "local":
            address = "LCL"
        elif where == "argument":
            address = "ARG"
        elif where == "this":
            address = "THIS"
        elif where == "that":
            address = "THAT"

        self.file.write("@" + address + "\n")
        if offset != -1:
            self.file.write("D=M\n")
            self.file.write("@" + str(offset) + "\n")
            self.file.write("A=D+A\n")
        else:
            self.file.write("A=M\n")


    def popD(self):
        self.file.write("@SP\n")
        self.file.write("M=M-1\n")
        self.file.write("A=M\n")
        self.file.write("D=M\n")


    def pushD(self):
        self.getSP()
        self.file.write("M=D\n")
        self.file.write("@SP\n")
        self.file.write("M=M+1\n")