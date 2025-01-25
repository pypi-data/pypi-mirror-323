# Blipper

<p align="center">
  <img src="icon.png" alt="Icon" width="100" height="100">
</p>

**Blipper** is an AI application that empowers you to access large language model capabilities through a high-level interface. Blipper provides a lot of functions each with a task of their own. We call them *Blips*.

Integrate Blips in your application and easily get access to the power of language models in today's era. Don't worry about managing files and directories, we took care of that for you.

Currently, Blipper supports python library. Soon, it will be available for other popular languages as well.


## Installing Blipper

### Ensure Python is Installed
Make sure Python (version 3.10 or newer) is installed on your system. To check:
```bash
python3 --version
```


### Create and activate a virtual environment (Optional)
We recommend insall the library in a virtual enviroment to avoid conflicts with other Python projects on your system.

```bash
# Create the virtual environment:
python3 -m venv .venv

# Activate for mac/linux:
source .venv/bin/activate

# Activate for windows:
.\venv\Scripts\activate
```

### Install blipper library
```bash
pip install blipper
```


### Check the installation
To verify the installation, run:
```bash
pip show blipper
```

## Blipper library usage
Create a Python script (e.g., app.py) and import blipper.

Below is a sample python code on how one can use blipper blipper python client.

```
from blipper import Blipper

blip = Blipper(api_key="Bliper API key goes here")

blip.translate(text="hola. como estas", target_lang="en")
```

### Run the script
```bash
python app.py
```

`translate` is just one example. Blipper offers multiple functions. The endpoint.py file contains all the functions. one can just call any of these functions and test them out. 

All the functions are described in blipper documentation and it is available at https://blipperdocs.epystemic.com Happy Blipping.
