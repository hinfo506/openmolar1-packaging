:: calls pyinstaller to create openmolar.exe
:: FLAGS
:: -F one file
:: -w windowed (no console)
:: -n name of the executable and spec file.



pyinstaller -F -n openmolar ^
    -i "C:\Program Files\openmolar\resources\icons\openmolar.ico" ^
    C:\Python34\Scripts\win_openmolar.pyw
