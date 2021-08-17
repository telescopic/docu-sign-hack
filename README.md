# Docu-Sign-hack
This repository contains code for our project chimPrint submitted as part of the DocuSign Good code hackathon : https://docusign2021.devpost.com/

![Screenshot from 2021-08-13 21-10-08](https://user-images.githubusercontent.com/45061877/129696120-290575b1-2aa6-437b-af45-30ee37ff8aa4.png)



# What we do
The website helps Participatory Mapping for Collaborative Conservation Planning with Decision-Makers Sign-off in accordance with the Jane Goodall institute challenge track of the DocuSign Good code hackathon

# How we do it
The well known cycle of clone-modify-review-merge is prevalent in any code version control system(such as Github) and we drew inspiration from this to apply it for the specific case of Maps as was required for the challenge. Here are the key features of this webapp:
- Allow users to clone existing maps and add/update features on them
- Merge changes on one map onto the other so all changes can be consolidated
- Track history of changes on any map so each change is well documented
- Approve a map for ready for distribution and decision makers provide their sign through the DocuSign Interface

# Why we did it this way
We have the following problems and their corresponding solutions

### #1 How do we allow any stakeholder to propose a change/add a feature to a map while keeping the original map intact?
For this, cloning a map is the best solution so any changes being proposed can be added to the new map that was cloned

### #2 How do we accept proposed changes in an atomic fashion ?
We grant edit/merge permissions to certain users and only those users can merge the changes on one map to the map that it was originally cloned from

### #3 How can we document any changes made?
We do something similar to documenting the commit history of code as is used in vcs by storing all history of changes

The above problem/solution pairs clearly lead to the need of a map version contol system that incorporates the clone-modify-review-merge cycle

# Tech Stack
<img src="https://img.shields.io/badge/html5%20-%23E34F26.svg?&style=for-the-badge&logo=html5&logoColor=white"/> <img src="https://img.shields.io/badge/css3%20-%231572B6.svg?&style=for-the-badge&logo=css3&logoColor=white"/> <img src="https://img.shields.io/badge/javascript%20-%23323330.svg?&style=for-the-badge&logo=javascript&logoColor=%23F7DF1E"/> <img src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/flask%20-%23000.svg?&style=for-the-badge&logo=flask&logoColor=white"/> <img src="https://img.shields.io/badge/bootstrap%20-%23563D7C.svg?&style=for-the-badge&logo=bootstrap&logoColor=white"/> <img src="https://img.shields.io/badge/github%20-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white"/> <img src ="https://img.shields.io/badge/sqlite-%2307405e.svg?&style=for-the-badge&logo=sqlite&logoColor=white"/>

- **Frontend**: HTML, CSS, Vanilla JS
- **Backend**: Flask
- **IDE**: VS Code
- **Version Control**: Git and GitHub
- **Database**: FlaskSQLAlchemy
- **API**: DocuSign eSignature API, ARCgis js 3.37 API
# Project Demo
A Working demo detailing the features of our webapp

[![Working Demo](https://img.youtube.com/vi/PiUikQyJ-hI/0.jpg)](https://www.youtube.com/watch?v=PiUikQyJ-hI)

# Working Screenshots

### The Map Editor along with note adding capabilities
![Screenshot from 2021-08-13 21-10-45](https://user-images.githubusercontent.com/45061877/129696386-74b89b29-d0be-421e-b099-5433f045b41d.png)

### History of changes documented for the map
![Screenshot from 2021-08-13 21-11-18](https://user-images.githubusercontent.com/45061877/129696426-20331505-4b44-41e1-a2dc-9524648f6f5f.png)

### Final Map Approved with decision makers sign
![Screenshot from 2021-08-13 21-12-38](https://user-images.githubusercontent.com/45061877/129696475-b09bed5f-4b4f-44e4-a434-5f02551d3cc3.png)

### Projects tab showing list of active projects, their status and signing status/availability
![Screenshot from 2021-08-13 21-13-26](https://user-images.githubusercontent.com/45061877/129696871-7b81cd77-0beb-4750-aee5-4926a7d66d43.png)

