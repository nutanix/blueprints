-----------
Description
-----------

The blueprint will create 2 playbooks in Prism Central: 

* One is for send notification to communication platform, such as Slack or Microsoft Teams
* Another one is accept the feedback from communication platform to decide to launch app or clean the environment.


-------------
How to use it
-------------

1. Prepare Microsoft Teams
++++++++++++++++++++++++++

* Create a public team from scratch, and skip add members.
* Add a connector to `General` channel (or create a dedicated channel first)
* Choose `incoming webhook` connector, click `Add`
* Input the connector name, then click `Create`
* Copy the url like following, then click `Done` 

  * `https://outlook.office.com/webhook/80b91334-601a-4d2e-aa59-36fbc15bc09e@bb047546-786f-4de1-bd75-24e5b6f79043/IncomingWebhook/18ac0e3f1df2475da0ef744cf3e5204b/2591ac3b-a500-441b-b9c8-079006eb9020` 

* (option) you could create playbook with this url and `MS Teams` action in xplay. 

2. Prepare ticket system 
++++++++++++++++++++++++

git clone and go into this folder and execute following commands

- Change variable: PC_IP to your prism central IP address
- Remeber to change `admin:password` to your really username and password to connect prism central
- ensure your vpn connection established and you could access prism central form localhost

.. code-block::

  virtualenv -p python3 venv
  source venv/bin/activate
  pip install -r requirements.txt
  PC_IP=<x.x.x.x> PC_PORT=9440 PC_TOKEN=$(echo -e 'admin:<password>\c' |base64) python single-page.py

3. Import blueprint and launch it
+++++++++++++++++++++++++++++++++

* Upload the `pre_approve_flow` blueprint to you project.

  * put the URL (mentioned in step 1) in variable: `msteams_url`
  * change the variable: `pc_ip` to your prism central IP address
  * change the **password** in variable: `blueprint_name`
  * In Credentials, set the password for `null` user

* prepare another blueprint, it should be the really blueprint you want to launch. For example the LAMP blueprint, and ensure it is launchable.

* Launch `pre_approve_flow` blueprint and select really blueprint you want to launch.

* Enjoy it

---------
Changelog
---------

- 2020.12 - 1st release
- 2021.01 - add README.rst


