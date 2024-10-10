```
#!/bin/bash

# Update and upgrade all packages, bypassing the manual prompt
pkg upgrade -y -o Dpkg::Options::="--force-confnew"

# Download the setup script for the pointless repository
curl -LO https://its-pointless.github.io/setup-pointless-repo.sh

# Run the setup script
bash setup-pointless-repo.sh

# Install required packages
pkg install android-tools python build-essential cmake libjpeg-turbo libpng libxml2 libxslt freetype git -y

# Install the python pip
pkg install python-pip

# Install the wheel package via pip
pip install wheel

# Clone the bot repository
git clone https://github.com/omer7731/bot.git gramaddict

# Change to the bot directory
cd gramaddict

# Upgrade setuptools
pip install --upgrade setuptools

# Install lxml for Python
pkg install python-lxml

# Install psutil via pip
pip install psutil

# Install other required Python packages from the requirements file
pip install -r requirements.txt

# Notify user that the script has completed successfully
echo "Bot installation completed!"
```




```
termux-wake-lock
adb connect localhost:5555
python -m uiautomator2 init
python yomedia.py
```


```
#!/bin/bash

pkg uninstall -y python

pkg install -y wget clang make openssl libffi zlib libbz2 libsqlite readline

wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz

tar -xf Python-3.11.0.tgz

cd Python-3.11.0

./configure --prefix=$PREFIX --enable-shared --with-openssl=$PREFIX CFLAGS="-Wno-implicit-function-declaration"

make

make install

```



```
#!/bin/bash

pkg uninstall -y python

pkg install -y wget git make clang openssl libffi zlib libbz2 libsqlite readline

git clone https://github.com/pyenv/pyenv.git ~/.pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc

source ~/.bashrc

pyenv install 3.11.10

pyenv global 3.11.10


```
