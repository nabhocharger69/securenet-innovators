@echo off

:: Define the output file
set output_file=output.txt

:: Run the application and redirect the output to the file
TLBS_Windows.exe > %output_file%

:: Optional: Display a message indicating the output has been saved
echo Benchmarking results has been saved to %output_file%

pause
