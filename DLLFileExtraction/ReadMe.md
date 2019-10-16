0. start the target program
1. dump its memory via the task-manager
    (details -> right-click on the executable -> Create dump file)
3. open a command prompt
4. drop into the command prompt:
* DLLFileExtractor.exe
* the created dump (can be found in %userprofile%\AppData\Local\Temp)
* an empty folder (which will hold the extracted files)
5. then write the estimated maximal file size of the encrypted DLL in bytes
    (if you don't know that value, ~100000000 should work - that's ~100MB)
6. copy AutoName_n_CleanUp.py into the former empty folder and execute it there