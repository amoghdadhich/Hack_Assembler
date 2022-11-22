# Assembler for the hack machine language

import sys
from typing import TextIO

translation_dict = {}
convert_dict = {}

class Parser():
    '''
    A parser object modifies a file object through three passes
    '''

    def __init__(self)-> None:
        return None

    def read_file(self, f_object: TextIO)-> list:
        '''input: file object
        output: a list with all comments and empty lines removed. 
        Also removes the white space before and after each line and 
        new line character at the end of each line'''

        f_list = f_object.readlines() # read the file to a list
        
        # remove the leading and trailing white space 
        # and the new line characters at the end of the lines
        f_list = list(map(str.strip, f_list)) 

        f_list_mod = []     # Holds the modified list of lines without comments and with empty lines removed

        for i,line in enumerate(f_list.copy()):

            indx = line.find('//')          # Find the index where the comment begins

            if indx != -1:                  # If the line has a comment in it remove all characters including and after //
                line = line[0:indx]         # Modify the line in the original list

            if line != '':                  # if the line is empty ignore it
                f_list_mod.append(str.strip(line))

        return f_list_mod

    def read_labels(self, f_list: list, trans_dict: dict):
        '''Reads the GOTO labels and maps them to the jump location.
        The key-value is added to the global translation dictionary.

        INPUT - takes in a list of strings where each line is a command.
        Assumes that comments and white spaces have been removed. This is important because the jump locations are decided based
        the assumption that the line numbers are correct.
        '''

        line_num = -1    # line number counter

        for line in f_list:
            
            # Check if the line is a GOTO label

            if line.find('(') != -1:
                key = line.strip('()')      # Key is the label name
                val = line_num + 1          # Value is NEXT line number

                trans_dict[key] = str(val)  # DONT increment line_num counter on the line with a label
            
            else:
                line_num += 1               # increment if not a label

    def read_vars(self, f_list: list, trans_dict: dict):
        '''Finds the variables mentioned in the file and adds the memory locations to translation table.
        Before adding, checks if the variable is already present (either added by read_vars or read_labels)
        '''

        mem_loc = 16

        for line in f_list:
            indx = line.find('@')

            if  indx != -1:             # Found a variable symbol
                key = line[indx + 1:]   # Variable name

                if key not in trans_dict and not key.isnumeric():   # If the key is not already present add it and NOT a number

                    trans_dict[key] = mem_loc   # Increment mem_loc after assigning
                    mem_loc += 1

class Converter():

    def __init__(self) -> None:
        return None
    
    def convert_cmd(self, line: str, conv_dict: dict)->str: 
        '''breaks a command into comp, dest and jmp and returns the mapping to binary'''

        dest_indx = line.find('=')  # Find the destination 

        if dest_indx == -1:         # If = not found set destination to None
            dest = None             
            
        else: 
            dest = line[0:dest_indx]    
            dest = str.strip(dest)      # Remove white spaces if found

        comp_indx = dest_indx + 1       # cmp starts from next character of '=',this works even when '=' is missing

    
        jmp_indx = line.find(';')       # Find the jmp characters

        if jmp_indx == -1:
            jmp = None
            comp = line[comp_indx:]             # If no semicolon then all remaining characters are in comp
            
        else:
            jmp = line[jmp_indx+1:]             # If found, jmp is from the next character of semi colon till then end
            jmp = str.strip(jmp)
            comp = line[comp_indx: jmp_indx]    # comp is till the semicolon

        comp = str.strip(comp)

        return '111' + conv_dict['comp'][comp] + conv_dict['dest'][dest] + conv_dict['jmp'][jmp]

    def translate_var(self, line: str, trans_dict: dict)->str:
        '''Translates a variable or a GOTO label to the correct location'''

        var_indx = line.find('@')

        var = line[var_indx + 1:]   # Variable name from the next character of '@'

        if var in trans_dict:
            loc = int(trans_dict[var])  # Find the location, convert to int
            
        else:
            loc = int(var)      # In case a location is directly mentioned
            
        loc_bin = bin(loc).replace("0b", "")    # Convert to binary

        return '0' + (15 - len(loc_bin)) * '0' + loc_bin    # return 0 + 15 digit binary number


def init_dict(trans_dict: dict):
    '''Initializes the translation dictionary global variable with the translations of the pre defined variables'''

    for i in range(16):
        trans_dict[f'R{i}'] = f'{i}'    # The locations of the RAM registers
    
    trans_dict['SCREEN'] = '16384'      # screen and keyboard IO register location
    trans_dict['KBD'] = '24576'

    trans_dict['SP'] ='0'
    trans_dict['LCL'] = '1'
    trans_dict['ARG'] = '2'
    trans_dict['THIS'] = '3'
    trans_dict['THAT'] = '4'

def init_conv_dict(conv_dict: dict):

    comp_dict = {'0': '0101010','1':'0111111','-1':'0111010',
                'D':'0001100','A':'0110000','!D':'0001101',
                '!A':'0110001','-D':'0001111','-A':'0110011',
                'D+1':'0011111','A+1':'0110111','D-1':'0001110',
                'A-1':'0110010','D+A':'0000010','D-A':'0010011',
                'A-D':'0000111','D&A':'0000000','D|A':'0010101',
                'M':'1110000','!M':'1110001','-M':'1110011',
                'M+1':'1110111','M-1':'1110010','D+M':'1000010',
                'D-M':'1010011','M-D':'1000111','D&M':'1000000',
                'D|M':'1010101'
                }
    
    
    dest_dict = {
                None:'000', 'M':'001', 'D':'010', 'MD':'011',
                'A':'100', 'AM':'101', 'AD':'110','AMD':'111'
                }

    jmp_dict = {
                None:'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011',
                'JLT':'100', 'JNE':'101', 'JLE':'110','JMP':'111'
                }

    conv_dict['comp'] = comp_dict
    conv_dict['dest'] = dest_dict
    conv_dict['jmp'] = jmp_dict

if __name__ == "__main__":
    fname = sys.argv[1]         # The program is called with python assembler.py <path-to-file>

    # Open the file for reading
    f_object = open(fname, 'r')
    
    # Parser runs a first pass through the file
    # Removes new lines and comments 

    parse = Parser()                                # create a parser object
    f_list = parse.read_file(f_object= f_object)    # Returned list has only commands with comments and blank lines removed

    init_dict(translation_dict)                     # Initialize the translation dictionary

    # Run a pass through the file list
    # Builds a table for the labels of the GOTO locations

    parse.read_labels(f_list= f_list, trans_dict= translation_dict)

    # Run another pass through the file list
    # Build a table for the memory location of the variables

    parse.read_vars(f_list= f_list, trans_dict= translation_dict)

    # Create converter object and initialize the converter dictionary
    convert = Converter()
    init_conv_dict(conv_dict= convert_dict)

    # Convert the lines

    converted_list = []     # Holds the binary output for each line
    

    for line in f_list:

        if line.find('(') == -1:    # Ignore GOTO labels

            if line.find('@') == -1:    # C-instruction
                conv_line = convert.convert_cmd(line= line, conv_dict= convert_dict)

            else:                       # A-instruction
                conv_line = convert.translate_var(line= line, trans_dict= translation_dict)

            converted_list.append(conv_line)

    
    # Write the converted list to a file
    f_write_name = f'{sys.argv[1][:-4]}.hack'

    with open(f_write_name, 'w') as f:
       
        for line in converted_list:
            f.write(f"{line}\n")
    
    f_object.close()
