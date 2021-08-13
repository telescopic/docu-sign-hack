from flask_app_basic import db, login_manager
from flask_login import UserMixin

import flask_app_basic

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}')"

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(20), nullable=False)
    subspecies = db.Column(db.String(40), nullable=False)
    lat = db.Column(db.String(20), nullable=False)
    lng = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"Area('{self.id}', '{self.area}')"

class PendingMapRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(20), nullable = False)
    author_name = db.Column(db.String(20), nullable=False)
    lat = db.Column(db.String(20), nullable=False)
    lng = db.Column(db.String(20), nullable=False)
    request_id = db.Column(db.Integer, nullable=False, unique=True)

    def __repr__(self):
        return f"PendingMapRequest('{self.id}', '{self.area}', '{self.author_name}')"

class ApprovedMapRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(20), nullable = False)
    author_name = db.Column(db.String(20), nullable=False)
    lat = db.Column(db.String(20), nullable=False)
    lng = db.Column(db.String(20), nullable=False)
    request_id = db.Column(db.Integer, nullable=False, unique=True)

    def __repr__(self):
        return f"PendingMapRequest('{self.id}', '{self.area}', '{self.author_name}')"

class MapState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(20))
    branch = db.Column(db.String(20), unique=True)
    graphics = db.Column(db.String(500000), nullable=False)
    edit_access = db.Column(db.String(5000))
    merge_access = db.Column(db.String(5000))

class MapChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(20))
    commit_number = db.Column(db.Integer, nullable=False)
    initial_graphics = db.Column(db.String(500000), nullable=False)
    final_graphics = db.Column(db.String(500000), nullable=False)
    notes = db.Column(db.String(5000), nullable=False)

    def __repr__(self):
        return f"MapChange('{self.branch}', '{self.commit_number}', '{self.notes}')"

class MergeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_branch = db.Column(db.String(20), nullable=False)
    to_branch = db.Column(db.String(20), nullable=False)
    from_graphics = db.Column(db.String(500000), nullable=False)
    to_graphics = db.Column(db.String(500000), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subspecies = db.Column(db.String(100), nullable=False)
    heading = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    sign_status = db.Column(db.String(100), nullable=False)
    scope = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100), nullable=False)

def re_init_db():
    db.drop_all()
    db.create_all()

    add_initial_db_data()
    
    db.session.commit()
    
def add_initial_db_data():
    graphics='''[{"geometry":{"rings":[[[5527917.18874737,9770313.714033205],[6799829.339412364,8263587.0124762105],[5116991.724686372,7402600.3258722145],[4353844.434287376,9046302.182116207],[5527917.18874737,9770313.714033205]]],"spatialReference":{"wkid":102100,"latestWkid":3857}},"symbol":{"color":[255,0,0,77],"outline":{"color":[0,0,0,255],"width":1,"type":"esriSLS","style":"esriSLSSolid"},"type":"esriSFS","style":"esriSFSSolid"}}]'''
    # file = open("flask_app_basic/static/shapes.txt", mode='r')
    # graphics = file.read()
    # file.close()
    branch="base-branch"
    author="jgi-admin"
    edit_access = ""
    merge_access = ""
    ms = MapState(
        author = author,
        branch = branch,
        graphics = graphics,
        edit_access = edit_access,
        merge_access = merge_access
    )

    subspecies = "Schweinfurthii (Eastern Chimpanzee)"
    heading = "Conserving the schweinfurthii subspecies"
    status = "[IN PROGRESS]"
    sign_status = "[SIGN NOT READY]"
    scope = "Thematic"
    target = "Validate/Improve Eastern chimpanzee Range map"
    project = Project(
        subspecies = subspecies,
        heading=heading,
        status = status,
        sign_status = sign_status,
        scope = scope,
        target = target,
    )

    db.session.add(ms)
    db.session.add(project)