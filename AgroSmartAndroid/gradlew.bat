@echo off
setlocal
set DIR=%~dp0
if not defined JAVA_HOME goto findJavaHome
set JAVA_EXE=%JAVA_HOME%\bin\java.exe
goto execute
:findJavaHome
where java >nul 2>nul
if %ERRORLEVEL%==0 (
    for /f "usebackq tokens=*" %%i in (`where java`) do set JAVA_EXE=%%i
) else (
    echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
    exit /b 1
)
:execute
"%JAVA_EXE%" -classpath "%DIR%gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
