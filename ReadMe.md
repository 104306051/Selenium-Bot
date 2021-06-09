
# Environment

Python `3.7.3`


Following environment variable is needed for the script to work properly.

| Variable Name | Value |
| --- | --- | 
| SIBOT_USERNAME | i.e. `username`@hp.com
| SIBOT_PWD | `password-of-the-user`  | 
| SIBOT_SQS_REGION_NAME | AWS SQS region name | 
| SIBOT_SQS_ACCESS_KEY_ID | AWS SQS access key |
| SIBOT_SQS_SECRECT_ACCESS_KEY| AWS SQS service secret key |


# Execution

Create virtual environment for the bot

```
python -m venv .\venv
```

Activate with either powershell or cmd
```powershell
.\venv\Scripts\Activate.ps1

.\venv\Scripts\Activate.bat
```

Restore library needed for sibot, from sibot directory

```
pip install -r requirements.txt
```


## SI Bot
SI Bot is for OBS creation page on Sherlock, it will create OBS on Sudden Impact automatically.

| Deployed on...  | Instance         | 
| --------------- | ---------------- |
|``tdcnebulaw01.tpc.rd.hpicorp.net``| 3 for ``prod``, 1 for``staging``, 1 for``testing`` |
|``tdcnebulas01.tpc.rd.hpicorp.net``| 3 for ``prod``, 1 for``staging``, 1 for``testing`` |


