import ASCII
import itertools 
from io import StringIO  
import pandas as pd


# this code allows to process default and readable format where headers are treated as text only

# multiple files with filegroup header, file headers and group/table headers
# get all tables/groups in 2 dimensional dataframe list
# get all table/group headers in 2 dimensional dataframe list
# get all file headers in 1 dimensional list
# get filegroup header in a list with single element (because it can be df or just a string)

# list of Encodings: https://docs.python.org/3/library/codecs.html#standard-encodings
# In file open modes rt and wt: t refers to the text mode. There is no difference between r and rt or w and wt since text mode is the default.
# Refer: https://docs.python.org/3/library/functions.html#open
# Character   Meaning
# 'r'     open for reading (default)
# 'w'     open for writing, truncating the file first
# 'x'     open for exclusive creation, failing if the file already exists
# 'a'     open for writing, appending to the end of the file if it exists
# 'b'     binary mode
# 't'     text mode (default)
# '+'     open a disk file for updating (reading and writing)
# 'U'     universal newlines mode (deprecated)

def read_asd(path_Text, encoding=None, Textstream = False): # path is actual data string if Textstream == True
    dft_2d_list = [] # tables/groups
    dfth_2d_list = [] # table/group headers
    dffh_list = [] # file headers
    dffgh_list = [] # filegroup headers
    r = False # readable/viewable format flag

    mode = 'rt'
    fileinput = open(path_Text, mode=mode, encoding=encoding) if Textstream == False else StringIO(path_Text)
    
    f = fileinput.read();
    filegrouptext = ""
    
    filegroupheadertext = ""
    filegroupwheader =  f.split(ASCII._ETXFG)
    # print(filewheader)
    if(len(filegroupwheader) > 1): # if filegroup header exists
        filegrouptext = filegroupwheader[1] # remaining part if actual filegroup contents
        temp = filegroupwheader[0].split(ASCII._STXFG)
        filegroupwheader = temp[0]
        # print(filegroupwheader)
        filegroupheadertext = temp[1] # Text after STXFG is Filegroup header text
        # print(filegroupheadertext)
        # if the text between SOHFG and STXFG is "readable" then set readable flag as true
        r = True if (filegroupwheader.lower().find("readable")>=0) else False
    else:
        filegrouptext = filegroupwheader[0]
        filegroupheadertext = None
    filegroupwheader = None # free the variable
    dffgh_list.append(filegroupheadertext)
    # print(filewheader)  
    # print('fh' ,filewheader)
    # print('g', file)

    RS =ASCII.F_RS(r)
    US =ASCII.F_US(r)

    FS =ASCII.F_FS (r)
    GS =ASCII.F_GS (r)

    SOHG =ASCII.F_SOHG(r)
    STXG =ASCII.F_STXG(r)
    ETXG =ASCII.F_ETXG(r)

    SOHF =ASCII.F_SOHF(r)
    STXF =ASCII.F_STXF(r)
    ETXF =ASCII.F_ETXF(r)

    SOHFG =ASCII.F_SOHFG(r)
    STXFG =ASCII.F_STXFG(r)
    ETXFG =ASCII.F_ETXFG(r)

    # print(r, US)


    filecount = 0
    # dfgh_list = []
    
    for file in filegrouptext.split(FS):
        filewheader =  file.split(ETXF)
        # print(filewheader)
        if(len(filewheader) >1):
            filetext = filewheader[1]
            filewheader = filewheader[0].split(STXF)[1]
        else:
            filetext = filewheader[0]
            filewheader = None
        # print('fh' ,filewheader)

        # print('fh' ,("NO HEADER - Group" if (filewheader==None) else filewheader + " - File") + str(filecount))
        
        dffh_list.append(filewheader)
        filecount+=1

        # print('g', group)
        df_list = []
        dfth_list = []
        tablecount = 0
        for table in filetext.split(GS):
            tablewheader = table.split(ETXG)
            # print(len(tablewheader))
            # print(tablewheader)
            if(len(tablewheader) >1):
                table = tablewheader[1]
                tablewheader = tablewheader[0].split(STXG)[1]
            else:
                table = tablewheader[0]
                tablewheader = None
            
            # print('th' ,("NO HEADER - Table" if (tablewheader==None) else tablewheader + " - Table") + str(tablecount))
            dfth_list.append(tablewheader)
            tablecount+=1    

            # TODO: header=0 means first row is header, we can also send header=None so there are no headers but then optional names have to be passed
            # engine= "python" to use multiple characters as separator
            df = pd.read_csv(StringIO(table), sep=US, lineterminator=RS, encoding=encoding, header=0)
            # df = pd.read_csv(StringIO(table), sep=US, lineterminator=RS, encoding=encoding, header=0, engine= "python")
            # print(df.columns)
            df_list.append(df)

        dft_2d_list.append(df_list)
        dfth_2d_list.append(dfth_list)

    return [dft_2d_list, dfth_2d_list, dffh_list, dffgh_list, r]


def write_asd(path, asd_data, encoding=None):
    dft_2d_list = asd_data[0] # tables/groups
    dfth_2d_list = asd_data[1] # table/group headers
    dffh_list = asd_data[2] # file headers
    dffgh_list = asd_data[3] # filegroup headers
    r = asd_data[4] # readable/viewable format flag

    # df_2d_list = asd_data[0]
    # dfth_2d_list = asd_data[1]
    # dfgh_list = asd_data[2]
    # dffh_list = asd_data[3]

    RS =ASCII.F_RS(r)
    US =ASCII.F_US(r)

    FS =ASCII.F_FS(r)
    GS =ASCII.F_GS(r)

    SOHG =ASCII.F_SOHG(r)
    STXG =ASCII.F_STXG(r)
    ETXG =ASCII.F_ETXG(r)

    SOHF =ASCII.F_SOHF(r)
    STXF =ASCII.F_STXF(r)
    ETXF =ASCII.F_ETXF(r)

    SOHFG =ASCII.F_SOHFG(r)
    STXFG =ASCII.F_STXFG(r)
    ETXFG =ASCII.F_ETXFG(r)


    firstFSflag = False
    firstGSflag = False
    tabletext = ""
    tableheadertext = ""
    groupheadertext = ""
    filegroupheadertext = ""
    
    mode = 'wt'
    with open(path, mode=mode, encoding=encoding) as fileoutput:
        # pd.DataFrame(dffh_list[0])
        if(len(dffgh_list) > 0):
            filegroupheadertext = '' if dffgh_list[0] is None else dffgh_list[0]
            if r == True:
                filegroupheadertext = SOHFG + "READABLE" + STXFG + filegroupheadertext + ETXFG
            # print(filegroupheadertext)
            fileoutput.write(filegroupheadertext)

        for (file, tableheaders, fileheaders) in itertools.zip_longest(dft_2d_list, dfth_2d_list, dffh_list):             
            fileheaders = '' if fileheaders is None else fileheaders
            if(len(fileheaders) > 0):
                fileheadertext = (FS if(firstFSflag == True) else '') + SOHF + STXF + fileheaders + ETXF
            else:
                fileheadertext = (FS if(firstFSflag == True) else '')
            # print(fileheadertext)
            fileoutput.write(fileheadertext)
            
            firstFSflag = True
            firstGSflag = False
            for (table, tableheader) in itertools.zip_longest(file, tableheaders):         
                tableheader = '' if tableheader is None else tableheader
                if(len(tableheader) > 0):
                    tableheadertext = (GS if(firstGSflag == True) else '') + SOHG + STXG + tableheader + ETXG
                else:
                    tableheadertext = (GS if(firstGSflag == True) else '')
                # print(tableheadertext)
                fileoutput.write(tableheadertext)

                firstGSflag = True
                
                df = table #pd.DataFrame(table)
                tabletext = df.to_csv(sep=ASCII._US, lineterminator=ASCII._RS, index=False, encoding=encoding)
                if r == True:
                    tabletext = tabletext.replace(ASCII._RS, RS).replace(ASCII._US, US)
                # print(tabletext)
                fileoutput.write(tabletext)
    fileoutput.close()



# # Chunk By Chunk
# https://stackoverflow.com/questions/47927039/reading-a-file-until-a-specific-character-in-python
# def each_chunk(stream, separator):
#   buffer = ''
#   while True:  # until EOF
#     chunk = stream.read(CHUNK_SIZE)  # I propose 4096 or so
#     if not chunk:  # EOF?
#       yield buffer
#       break
#     buffer += chunk
#     while True:  # until no separator is found
#       try:
#         part, buffer = buffer.split(separator, 1)
#       except ValueError:
#         break
#       else:
#         yield part

# with open('myFileName') as myFile:
#   for chunk in each_chunk(myFile, separator='\\-1\n'):
#     print(chunk)  # not holding in memory, but printing chunk by chunk