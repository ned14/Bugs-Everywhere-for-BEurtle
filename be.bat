@echo off
python -c "import sys, libbe.ui.command_line; sys.exit(libbe.ui.command_line.main());" %*
set BE_TOOL_ERRORLEVEL=%ERRORLEVEL%
exit /B %BE_TOOL_ERRORLEVEL%
