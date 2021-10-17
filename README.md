# smhi-wrapper

# Installation
* sudo mkdir /opt/smhi-wrapper
* sudo python3 -m venv /opt/smhi-wrapper/venv
* sudo source /opt/smhi-wrapper/venv/bin/activate
* sudo -s
* pip install -r requirements.txt
* exit
* sudo cp smhi-wrapper.py /opt/smhi-wrapper/.
* sudo cp smhi-wrapper.service /etc/systemd/system/.
* sudo systemctl start smhi-wrapper
* sudo systemctl enable smhi-wrapper
