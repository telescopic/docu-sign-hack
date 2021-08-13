from types import new_class
from flask import render_template, url_for, flash, request
from flask_app_basic import app, db, bcrypt
from flask_app_basic.models import User, Area, MapChange, MapState, MergeRequest, Project
from flask_app_basic.forms import RegistrationForm, LoginForm, UpdateAccountForm, SubmitMapRequestForm, CommitNotesForm, CloneMapForm, GetBranchForm, DeleteBranchForm, MergeRequestForm
from flask_login import login_user as log_in_user
from flask_login import logout_user as log_out_user
from flask_login import current_user, login_required
from flask import session
from ds.esign import DSUtil
from flask_app_basic.pdf_gen import PDFUtil
from PIL import Image
from werkzeug.utils import redirect
import urllib

@app.route('/')
def home():
    return render_template('main_page.html', title="Home",  image_file=url_for('static', filename='profile_pics/flower.jpeg'))

@app.route('/view_areas')
def view_areas():
    areas = Area.query.all()
    return render_template('view_areas.html', title="Habitats", areas=areas)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account Created Successfully! You can now Log in :)', 'success')
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = user.email
            session['name'] = user.username
            log_in_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Check username/password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout_user():
    log_out_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account details have been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('account.html', title='Account',
                            image_file=url_for('static', filename='profile_pics/user.png'), form=form)


## DEPRECATE
@app.route('/submit_request', methods=['GET', 'POST'])
@login_required
def submit_map_request():
    form = SubmitMapRequestForm()

    if form.validate_on_submit():
        session['lat'] = form.latitude.data
        session['lng'] = form.longitude.data
        return redirect(url_for('embedded_signing'))

    return render_template('map_request.html', title="Submit", 
                            image_file=url_for('static', filename='profile_pics/user_image.png'), form=form, navbar_false=True)

## DEPRECATE
@app.route('/sign', methods=['GET', 'POST'])
def embedded_signing():
    user_email = session['email']
    user_name = session['name']
    pdf_util = PDFUtil()
    ds_util = DSUtil()
    doc_path = "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/generated_pdfs/hello.pdf"

    contents = pdf_util.get_formatted_contents(area="area", author=user_name, lat=session['lat'], lng=session['lng'])
    pdf_util.create_pdf(doc_path, contents)

    args = ds_util.get_args_for_esign(signer_name=user_name, signer_email=user_email, doc_path=doc_path)
    results = ds_util.worker(args)
    print(results)

    return redirect(results['redirect_url'])


@app.route('/map_draw', methods=['POST', 'GET'])
def map_draw():
    return render_template('map_draw.html')

@app.route('/map_edit', methods=['POST', 'GET'])
def map_edit():
    return render_template('map_edit.html')

@app.route('/view_map', methods=['GET', 'POST'])
@login_required
def view_map():
    form = CommitNotesForm()
    
    map_author = session['author']
    map_branch = session['branch']
    
    if form.validate_on_submit():
        commit_number = form.commitNumber.data
        initial_graphics = form.initialGraphics.data
        final_graphics = form.finalGraphics.data
        notes = form.notes.data
        branch = session['branch']
        
        map_change = MapChange(
            branch = branch,
            commit_number=commit_number,
            initial_graphics=initial_graphics,
            final_graphics=final_graphics,
            notes=notes
        )

        map_state = MapState.query.filter_by(branch=branch).first()
        map_state.graphics = final_graphics

        db.session.add(map_change)
        db.session.commit()

        session['branch'] = branch
        print(notes)
        return redirect(url_for('commit_history'))
    else:
        print(form.errors)

    return render_template('view_map.html', navbar_false=True, form=form, author=map_author, branch=map_branch)

@app.route('/map_base')
def map_base():
    return render_template('map_base.html')

@app.route('/commit_history')
def commit_history():
    branch = session['branch']
    author = session['author']
    changes = MapChange.query.filter_by(branch=branch).all()[::-1]
    return render_template('commit_history.html', changes=changes, author_name=author, branch_name=branch)

@app.route('/temp')
def temp():
    return render_template('temp.html')

@app.route('/fork', methods=['GET', 'POST'])
def fork_branch():
    form = CloneMapForm()

    from_author = session['name']
    from_branch = session['branch']
    to_author = session['name']
    all_user_data = User.query.all()
    users = [user.username for user in all_user_data if user!=to_author]

    if form.validate_on_submit():
        to_branch = form.branch_name.data
        edit_access = form.edit_access.data
        merge_access = form.merge_access.data

        # TODO: copy map state
        old_map_state = MapState.query.filter_by(branch=from_branch).first()
        new_map_state = MapState(
            author = to_author,
            branch = to_branch,
            graphics = old_map_state.graphics,
            edit_access = edit_access,
            merge_access = merge_access
        )

        db.session.add(new_map_state)
        db.session.commit()

        # TODO: copy map changes for that map
        old_map_changes = MapChange.query.filter_by(branch=from_branch).all()
        for old_change in old_map_changes:
            mc = MapChange(
                branch = to_branch,
                commit_number = old_change.commit_number,
                initial_graphics = old_change.initial_graphics,
                final_graphics = old_change.final_graphics,
                notes = old_change.notes
            )
            db.session.add(mc)
        
        db.session.commit()
        
        return redirect(url_for('branches'))
    else:
        print(form.errors)
    
    return render_template('fork.html', form=form, from_author=from_author, from_branch=from_branch, to_author=to_author, users=users)

@app.route('/merge', methods=['GET', 'POST'])
def merge_branch():
    map_states = MapState.query.all()
    all_map_states = [
        [map_state.author, map_state.branch] for map_state in map_states
    ]
    cur_branch = session['branch']
    cur_author = session['author']

    all_merge_requests = MergeRequest.query.filter_by(to_branch=cur_branch).all()

    merge_form = MergeRequestForm()

    if merge_form.validate_on_submit():
        if merge_form.merge_req_type.data == 'request':
            merge_from_branch = merge_form.from_branch.data
            # print("DEBUG", merge_from_branch)

            merge_from_map_state = MapState.query.filter_by(branch=merge_from_branch).all()
            merge_from_map_state = merge_from_map_state[0]
            merge_from_graphics = merge_from_map_state.graphics

            merge_to_branch = merge_form.to_branch.data
            # print(merge_to_branch)
            merge_to_map_state = MapState.query.filter_by(branch=merge_to_branch).all()
            merge_to_map_state = merge_to_map_state[0]
            merge_to_graphics = merge_to_map_state.graphics

            merge_req = MergeRequest(
                from_branch=merge_from_branch,
                to_branch=merge_to_branch,
                from_graphics=merge_from_graphics,
                to_graphics=merge_to_graphics
            )

            db.session.add(merge_req)
            db.session.commit()
            return redirect(url_for('branches'))
        else:
            # this map is the one with final changes
            # rename these to the other branch
            merge_from_branch = merge_form.from_branch.data
            merge_from_map_state = MapState.query.filter_by(branch=merge_from_branch).all()
            merge_from_map_state = merge_from_map_state[0]
            merge_from_graphics = merge_from_map_state.graphics
            
            # this map is the one that will be updated
            # delete this data
            merge_to_branch = merge_form.to_branch.data
            merge_to_map_state = MapState.query.filter_by(branch=merge_to_branch).all()

            map_branch_to_delete = merge_to_branch
            merge_to_map_state = merge_to_map_state[0]
            merge_to_graphics = merge_to_map_state.graphics

            # delete map state and map changes (its history)
            MapState.query.filter_by(branch=map_branch_to_delete).delete()
            MapChange.query.filter_by(branch=map_branch_to_delete).delete()
            db.session.commit()

            # rename branch data
            merge_from_map_states = MapState.query.filter_by(branch=merge_from_branch).all()
            for map_state in merge_from_map_states:
                map_state.branch = map_branch_to_delete
            
            merge_from_map_changes = MapChange.query.filter_by(branch=merge_from_branch).all()
            for map_change in merge_from_map_changes:
                map_change.branch = map_branch_to_delete
            

            merge_change_note = "subject=Merge Request|body=Merged map "+merge_from_branch+" to current map"

            # Add a MapChange signifying the merge
            merge_map_change = MapChange(
                branch = map_branch_to_delete,
                commit_number = 0000,
                initial_graphics = merge_to_graphics,
                final_graphics = merge_from_graphics,
                notes = merge_change_note
            )

            # now delete the original merge request
            MergeRequest.query.filter_by(from_branch=merge_from_branch, to_branch=merge_to_branch).delete()

            db.session.add(merge_map_change)

            db.session.commit()
            return redirect(url_for('branches'))
    else:
        print(merge_form.errors)
    

    return render_template(
        'merge.html', 
        map_states=all_map_states,
        from_author=cur_author,
        from_branch=cur_branch,
        merge=merge_form,
        merge_requests=all_merge_requests)

@app.route('/branches', methods=['GET', 'POST'])
def branches():
    form = GetBranchForm()
    branches = [ map_item.branch for map_item in MapState.query.all() ]
    if form.validate_on_submit():
        branch_name = form.branch_name.data
        map_state = MapState.query.filter_by(branch=branch_name).first()
        
        session['branch'] = branch_name
        session['author'] = map_state.author

        if map_state == None:
            map_state_graphics = ""
        else:
            map_state_graphics = map_state.graphics
        return redirect(url_for('temp', graphics=map_state_graphics))
    return render_template('branches.html', form=form, branches=branches)

@app.route('/branch_info', methods=['GET', 'POST'])
def branch_info():
    form = DeleteBranchForm()

    if form.validate_on_submit():
        branch_to_delete = session['branch']
        MapState.query.filter_by(branch=branch_to_delete).delete()
        MapChange.query.filter_by(branch=branch_to_delete).delete()
        db.session.commit()
        return redirect(url_for('branches'))
    return render_template('branch_info.html', author=session['author'], branch=session['branch'], form=form)

@app.route('/projects', methods=['GET', 'POST'])
def projects():
    all_projects = Project.query.all()
    session['project'] = all_projects[0].heading
    drop_down = "none"
    if all_projects[0].status == "[COMPLETE]":
        drop_down = "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/saved_pdfs/cert.jpg"
    return render_template('projects.html', projects=all_projects, drop_down=drop_down)

@app.route('/gen_sign', methods=['GET', 'POST'])
def gen_sign():
    '''
    Generate the sign for the given map branch
    '''

    url = request.form["HREF"]
    save_path = "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/saved_pdfs/final_map.png"
    urllib.request.urlretrieve(url, save_path)

    im = Image.open(save_path)
    w, h = im.size
    img1 = im.crop((100, 200, w-100,h-200))
    img1.resize((200, 200))
    img1.save(save_path)

    branch = session['branch']
    author = session['author']
    email = session['email']
    project = session['project']

    # generate the required PDF
    pdf_util = PDFUtil()

    contents = pdf_util.get_formatted_contents(area=project, author=author)
    doc_path = "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/generated_pdfs/final_"+project+"_"+branch+".pdf"

    pdf_util.create_pdf(doc_path, contents)

    session['sign_doc_path'] = doc_path

    projects = Project.query.all()

    for project in projects:
        project.sign_status = "[SIGN READY]"
    
    db.session.commit()

    return redirect(url_for('projects'))

@app.route('/embed_sign_doc', methods=['POST', 'GET'])
def embed_sign_doc():
    '''
    Do the embedded signing for the final map that is to be distributed
    '''
    doc_path = session['sign_doc_path']
    user_email = session['email']
    user_name = session['name']

    ds_util = DSUtil()

    args = ds_util.get_args_for_esign(signer_name=user_name, signer_email=user_email, doc_path=doc_path)
    results = ds_util.worker(args)
    session['e_id'] = results["envelope_id"]

    return redirect(results['redirect_url'])

@app.route('/post_sign', methods=['POST', 'GET'])
def post_sign():
    flash('Signing succesful! The final map is now ready!', 'success')

    # modify db
    all_projects = Project.query.all()
    project = all_projects[0]
    project.status = "[COMPLETE]"
    project.sign_status = "[SIGN COMPLETE]"
    db.session.commit()

    # save the retreived doc
    ds_util = DSUtil()
    envelope_id = session['e_id']
    doc_id = 1
    dest_path = "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/saved_pdfs/cert.jpg"
    
    args = ds_util.get_args_for_doc_retrieval(doc_id, envelope_id)
    ds_util.envelope_doc_to_img(args, dest_path)

    return redirect(url_for('projects'))

@app.route('/print_map', methods=['POST', 'GET'])
def print_map():
    return render_template('print_map.html')

@app.route('/progress', methods=['POST', 'GET'])
def progress():
    cur_branch = session['branch']
    map_state = MapState.query.filter_by(branch=cur_branch).all()
    map_state = map_state[0]
    graphics = map_state.graphics

    return render_template('progress.html', graphics=graphics)