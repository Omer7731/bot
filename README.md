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

mv /data/data/com.termux/files/home/gramaddict/distutils /data/data/com.termux/files/usr/lib/python3.12/

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
pkg upgrade -y
curl -LO https://its-pointless.github.io/setup-pointless-repo.sh
bash setup-pointless-repo.sh
pkg install android-tools python build-essential cmake libjpeg-turbo libpng libxml2 libxslt freetype git -y
pip install wheel
pip install psutil
git clone https://github.com/omer7731/bot.git gramaddict
cd gramaddict
pip install -r requirements.txt

```


```
git clone https://github.com/omer7731/bot.git gramaddict
cd gramaddict
pip install -r requirements.txt

```

```
termux-wake-lock
adb connect localhost:5555
python -m uiautomator2 init
python yomedia.py
```

```
python -m uiautomator2 init
python run.py
```
