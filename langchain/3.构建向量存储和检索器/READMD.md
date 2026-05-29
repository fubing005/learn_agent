# 安装sqlite3
```bash
sudo apt update
sudo apt upgrade
sudo apt remove sqlite3
sudo apt install wget build-essential
wget https://www.sqlite.org/2023/sqlite-autoconf-3430000.tar.gz
tar -xzvf sqlite-autoconf-3430000.tar.gz
cd sqlite-autoconf-3430000
./configure
make
sudo make install

vim ~/.bashrc
export PATH=/usr/local/bin:$PATH
source ~/.bashrc   # 如果是bash

# python 临时使用sqlite3 
pip install pysqlite3-binary

# index.py
# 🎯 必须放在代码的最顶部（第一行）
import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
```