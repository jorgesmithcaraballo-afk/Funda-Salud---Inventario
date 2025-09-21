@echo off
REM Instala MySQL como servicio
cd C:\MySQL\mysql-9.4.0-winx64\bin
mysqld --install MySQL

REM Inicia el servicio
net start MySQL
