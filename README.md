# LiDAR Visualization Tool

## Getting Started
### Prerequistes
LiDAR Visualization Tool runs on a Linux system, so you'll need to set up a system if you have a different operating system.
We have 3 ways for you to set up a system.
1. **Dual-boot your system for better processing power.**
2. **Set-up a GUI-based virtual machine.**

    We used [VMware](https://www.vmware.com/) to set-up our virtual machine. 
    Check out this [tutorial](https://unixcop.com/how-to-install-ubuntu-21-04-on-vmware-workstation-pro/) that can help with installation. However, here are some notes:
    * UMD students have access to VMWare through TerpWare for free
    * We used Ubuntu 20.04 since it includes the correct verion of Python (3.8)
    * We recommend allocating at least 30 GB of disk space

3. **SSH into a virtual machine**
    
    Download [RealVNC](https://www.realvnc.com/en/connect/download/viewer/) for your specific operating system and follow the instructions in the setup wizard.

    SSH into the virtual machine in a terminal (password: check SVN)
    ```sh
    ssh cmsc435@vodaphone.cs.umd.edu
    ```
    Run the script `./vc` to create a console handler on the host

    Add a connection in VNC Viewer to `vodaphone.cs.umd.edu:6` (password: check SVN)

    Now you have a running virtual machine. After closing the machine, use `./vk` to kill the console handler.


### Cloning the Repository
**Note**: if any command doesn't exist, run `sudo apt-get install` for that command

Execute these commands on your Linux system.
```sh
git clone https://para.cs.umd.edu/neehar/lidar.git
git checkout Development
```

### Installing Dependencies
**Note**: if any command doesn't exist, run `sudo apt-get install` for that command

As a good practice and to make sure you have the necessary dependencies, update your Linux system.
```sh
sudo apt update && sudo apt upgrade
```

Check which version of Python you have. Due to constraints by Open3D, you must have Python 3.8. 

```sh
python3 --version
```

If you have a different version, you'll have to change to the correct version. We've included a tutorial for a Debian-based system.

---
Run these commands to get the necessary dependencies to install Python (run in your root directory).
```sh
# Install dependencies
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
# download a Python 3.8 tarball
wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
# unzip the tarball
tar xzf Python-3.8.12.tgz
# make sure your system has the right configurations
cd Python-3.8.12
./configure --enable-optimizations
# make and install the Python binaries
make -j 2
sudo make altinstall
```
**Note**: you'll use `python3.8` instead of `python3` from now on

---

Move into the `src` folder
```sh
pip install pipenv
pipenv install
```
Add the following lines to the `~/.bashrc` file
```sh
export PATH=$PATH:/home/[your_username]/.local/bin/
```
Run this to update the shell
```sh
. ~/.bashrc
```

## Usage
### Converting a nuScenes Dataset
`input_path` : a path to a nuScenes data file

`output_path` : the directory to output the LVT directory to

`scene_name` : a scene from the dataset to convert

`prediction_path` : a path to a JSON file with the predicted bounding boxes
```sh
python3 nuscenes-ct.py -f [input_path] -o [output_path] -s [scene_name] -p [prediction_path]
```
### Converting a Waymo Dataset
`input_path` : a path to a Waymo TFRecord file

`output_path` : the the directory to output the LVT directory to

```sh
python3 waymo-ct.py -f [input_path] -o [output_path]
```

### Visualizing Data
`input_path` : a path to a converted dataset in the LVT format
```sh
pipenv run python3 lct.py -f [input_path]
```

## Folder Structure
**cameras** : contains the RGB images from different cameras
* CAM_FRONT
  * 1.jpg
  * 2.jpg
  * ...
* CAM_BACK
  * 1.jpg
  * 2.jpg
  * ...
...

**pointcloud** : contains PCD files with LiDAR pointclouds for each sensor
* LIDAR_TOP
  * 1.pcd
  * 2.pcd
  * ...
* LIDAR_FRONT
  * 1.pcd
  * 2.pcd
  * ...
* ...

**bounding** : contains the ground truth bounding boxes as JSON files
* 1
  * description.json
  * boxes.json
* 2
  * ...
* ...

**pred_bounding** : contains a model's predicted bounding boxes as JSON files
* 1
  * description.json
  * boxes.json
* 2
  * ...
* ...

**ego** : contains the translation and rotation for each frame as JSON files
* 1.json
* 2.json
* ...


