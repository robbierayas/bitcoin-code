@echo off
echo Installing Bitcoin Code dependencies...
echo.

python -m pip install -U pip setuptools ecdsa pycryptodome

echo.
if %ERRORLEVEL% EQU 0 (
    echo Installation completed successfully!
    echo.
    echo Note: Using pycryptodome instead of pycrypto
    echo pycryptodome is the modern, maintained fork that works with Python 3.13
) else (
    echo Installation failed with error code %ERRORLEVEL%
    echo Please check the error messages above.
)

pause
