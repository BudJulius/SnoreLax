# SnoreLax

SnoreLax - a sleep monitoring system, developed as a school project for the course ACIT4015 - Internet of Things.

This repository contains the trained model, application code and web application code.

The SnoreLax_WebApp folder contains the Blazor web application files that ember a Looker studio report, as well as displays recordings.

The SnoreLax_System folder contains all the python files and classification model required to run the whole system. 

Credentials, passwords and connection strings have been removed for security reasons.

Microsoft Azure resources have been used - SQL database, Storage Account and Web Apps.


IMPORTANT NOTE:
The SnoreLax_System folder contains files that are working on a Raspberry Pi 4B device and uses AlsaAudio and subprocess for recording audio. To do it on a Windows device, PyAudio should be used instead.
