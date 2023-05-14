import sys
import os
from Parser import Parser
from Writer import Writer


def translate():

    # get file name, split into input/output files
    root = input("Enter the name of the .vm file to convert to asm: ")
    root = root.split(".", 1)[0] # isolate root name
    absolute = sys.path[0].rsplit('\\', 1)[0] # directory above translator folder (.../target-directory)
    name = absolute.rsplit('\\', 1)[1] # directory/test name to replace sys.vm ("target-directory")
    
    absoluteIn = os.path.join(absolute, root)
    if root == "Sys": # if Sys.vm, change to test name 
        absoluteOut = os.path.join(absolute, name) # (.../target-directory/directory_name.vm)

    else: # otherwise use root name
        absoluteOut = absoluteIn
  
    outFileName = absoluteOut + ".asm"
    inFileName = absoluteIn + ".vm"

    # create parser and writer, feed appropriate files
    parser = Parser(inFileName)
    writer = Writer(outFileName, parser)

    parser.getNext() # get next first
    while parser.currentCommand != "~~~": # then loop until EOF flag
        print(parser.currentCommand)
        writer.writeNext()
        parser.getNext()
    writer.file.close()

    # ask user to loop again
    print("Finished!")
    while(1):
        ask = input("Run again? (y/n): ")
        if ask == "y":
            print()
            translate()
            break
        elif ask == "n":
            exit()


if __name__ == '__main__':
    translate() # runs entire program
