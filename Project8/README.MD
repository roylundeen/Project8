Author: Roy Lundeen

There are 4 .py files that all need to be in the same folder: C, Parser, Writer, and VMTranslator. To run this VM Translator, place the entire VMTranslator folder into the same directory as the .vm file to convert. From there, run the VMTranslator.py from inside the VMTranslator folder, as it checks the directory above for .vm files. The program uses the terminal in the same way as the Project 6 implementation, you do not need to add .vm when prompted for a file name but (I think) it will work if you do.

As an example: For the StaticsTest test, I placed the VMTranslator folder inside the StaticsTest folder next to the .vm files, then ran the VMTranslator.py inside it three times for Class1, Class2, and Sys.vm. The code converts the Sys.vm into StaticsTest.vm so that the test will run.

*Currently only passes 4/6 tests, failing FibonacciElement and StaticsTest
