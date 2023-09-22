REM Wait for 10 seconds
timeout /t 10 >nul

REM 激活虚拟环境
call venv\Scripts\activate

REM 运行 Python 脚本
python zendao_daily.py

REM 关闭虚拟环境
REM deactivate

pause >nul