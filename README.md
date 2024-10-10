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
pip install --upgrade uiautomator2
pip install --upgrade pip setuptools wheel
termux-wake-lock
adb connect localhost:5555
python -m uiautomator2 init
python yomedia.py
```


```
#!/bin/bash

# Step 1: Uninstall the current Python version (if installed)
pkg uninstall -y python

# Step 2: Install dependencies required for building Python
pkg install -y wget clang make openssl libffi zlib libbz2 libsqlite readline

# Step 3: Download Python 3.11.0 source code
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz

# Step 4: Extract the tar file
tar -xf Python-3.11.0.tgz

# Step 5: Change directory to Python-3.11.0
cd Python-3.11.0

# Step 6: Configure the build
./configure --prefix=$PREFIX --enable-shared --with-openssl=$PREFIX

# Step 7: Compile Python (this may take some time)
make

# Step 8: Install Python
make install



```
