#!/bin/bash

mkdir -p test/
cp -a config.m4 php_scripts.c php_scripts.h test/
cd test/
phpize
./configure
make
exit

cd ../
echo '*****'
php -c php.ini test.php
echo '*****'
php-cgi test.php
echo '*****'
php-cgi -c php.ini test.php
echo '*****'
