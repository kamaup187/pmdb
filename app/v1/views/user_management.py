
from flask_restful import Resource
from flask_login import login_user,logout_user
from flask_login import login_required, current_user

from flask import render_template,Response,request,flash,redirect,url_for,abort
from ..forms.forms import ModifyAccessRightForm
from ..forms.forms import UserRegForm

from app.v1.models.operations import *
from .helperfuncs import *
from app import db
from app import sms


class RegisterUserGroup(Resource):
    @login_required
    def get(self):
        pass

    @login_required
    def post(self):
        company_id = current_user.company.id
        name = request.form.get('name')
        description = request.form.get('description')
        new_group = CompanyUserGroupOp(name,description,company_id)
        new_group.save()
        msg='New group added.'
        flash(msg,"success")
        return redirect(url_for("api.modifyaccessright"))

class DeleteUserGroup(Resource):
    @login_required
    def get(self):
        """Handle GET request for this view. Url ---> /del/group"""
        user_group = current_user.company_user_group
        accessright = check_accessright(user_group,"grant_rights")
        if accessright != True:
            return Response(render_template('noaccess.html',name=current_user.name))

        usergroup_list = fetch_all_usergroups()
        if request.method == 'GET':
            return Response(render_template('del_usergroup.html',option_list=usergroup_list))
    def post(self):
        name = request.form.get('usergroup')

        del_group = UserGroupOp.fetch_usergroup_by_name(name)
        UserGroupOp.delete(del_group)
        
        msg='Group removed.'
        usergroup_list = fetch_all_usergroups()
    
        return Response(render_template('del_usergroup.html',option_list=usergroup_list,msgs=msg))
        
class AssignRole(Resource):
    @login_required
    def get(self):
        """Handle GET request for this view. Url ---> /assign/roles"""

        # user_group = current_user.company_user_group
        # accessright = check_accessright(user_group,"grant_rights")
        # if accessright != True:
        #     return Response(render_template('noaccess.html',name=current_user.name))

        # company = current_user.company
        # groups = company.groups

        # form = ModifyAccessRightForm()
        # usergroup_list = stringify_list_items(groups)
        # place_holder_item = '--Select Usergroup--'
        # usergroup_list.insert(0,place_holder_item)
        # form.usergroup.choices = usergroup_list

        # store = None

        # current_usergroup = f"{store}"

        # return Response(render_template('modifyaccessclone.html',option_list=groups,role_option_list=role_list,current_usergroup=current_usergroup,form=form,name=current_user.name))
        pass

    @login_required
    def post(self):
        """we are modifying roles here by assigning its fields with user and group data"""

        role = request.form.get('role')#this will be selected first within the form
        usergroup = request.form.get('usergroupsessionvar')#this will be selected within the form
        run = request.form.get('run')
        # import pdb; pdb.set_trace()

        if usergroup == '--Select Usergroup--':
            pass
        else:
            stored_usergroup = usergroup

        if run:
            usergroup_name = f"{stored_usergroup}"
            return render_template('ajaxusergroupname.html',usergroup_name=usergroup_name)
            
        if not role:
            role_list = filterroles(stored_usergroup)
            return render_template("ajaxassignroleoptions.html",role_options=role_list)

        grouprole_id = GroupRoleOp.fetch_role_by_name(role).id
        usergroup_obj = CompanyUserGroupOp.fetch_usergroup_by_name(stored_usergroup)
        usergroup_id = usergroup_obj.id
        user_id = current_user.id
        present = get_group_role_assgn_obj(usergroup_obj,role)
        if not present:
            assign_obj = AssignGroupRoleOp(usergroup_id,grouprole_id,user_id)
            assign_obj.save()

        msg='Role assigned.'
        flash(msg,"success")

        role_list = filterroles(stored_usergroup)
        company = current_user.company
        groups = company.groups

        form = ModifyAccessRightForm()
        usergroup_list = stringify_list_items(groups)
        place_holder_item = '--Select Usergroup--'
        usergroup_list.insert(0,place_holder_item)
        form.usergroup.choices = usergroup_list

        current_usergroup = f"{stored_usergroup}"

        return Response(render_template(
            'modifyaccessclone.html',
            option_list=groups,
            role_option_list=role_list,
            current_usergroup=current_usergroup,
            form=form,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))
           
class ModifyAccessRight(Resource):
    """class"""
    @login_required
    def get(self):
        if current_user.username.startswith('qc'):
            pass
        else:
            user_group = current_user.company_user_group
            accessright = check_accessright(user_group,"grant_rights")
            if accessright != True:
                return Response(render_template('noaccess.html',name=current_user.name))

        company = current_user.company
        groups = company.groups

        form = ModifyAccessRightForm()
        usergroup_list = stringify_list_items(groups)
        place_holder_item = '--Select Usergroup--'
        usergroup_list.insert(0,place_holder_item)
        form.usergroup.choices = usergroup_list

        return Response(render_template(
            'modifyaccess.html',
            option_list=groups,
            form=form,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))
    
    @login_required
    def post(self):
        form = ModifyAccessRightForm()
        run = None#run value will be supplied by ajax request
        run2 = None
        usergroup =  form.data.get('usergroup')
        grouprole =  form.data.get('grouprole')
        accessright = request.form.get('access')
        # acc = form.data.get('accessright')

        run = request.form.get('run')
        run2 = request.form.get('run2')
        runcheckall = request.form.get('runcheckall')
        modified_by = current_user.id

        if not accessright:
            accessright = "False"

        access = return_bool(accessright)

        company = current_user.company
        groups = company.groups
        for group in groups:
            if str(group) == usergroup:
                usergroup_obj = group
                break
        # usergroup_obj = CompanyUserGroupOp.fetch_usergroup_by_name(usergroup)

        if usergroup and run:
            usergroup_id = usergroup_obj.id
            assigngrouproleobjs_list = fetch_all_assigned_roles(usergroup_id)
            return render_template('ajaxaccessrights.html',assigngrouproleobjs_list=assigngrouproleobjs_list)

        if runcheckall:
            usergroup_id = usergroup_obj.id
            if usergroup == "Administrator" and access == False:
                pass
            else:
                assigngrouproleobjs_list = fetch_all_assigned_roles(usergroup_id)
                for item in assigngrouproleobjs_list:
                    AssignGroupRoleOp.update_accessright(item,access,modified_by)
            new_assigngrouproleobjs_list = fetch_all_assigned_roles(usergroup_id)
            return render_template('ajaxaccessrights.html',assigngrouproleobjs_list=new_assigngrouproleobjs_list)

        assign_obj = get_group_role_assgn_obj(usergroup_obj,grouprole)
        if usergroup == "Administrator" and grouprole == "grant_rights":
            assign_obj = None
        
        if assign_obj:
            AssignGroupRoleOp.update_accessright(assign_obj,access,modified_by)
            msg = "Database update success"
            flash(msg,"success")
        else:
            msg = "Update failed"
            flash(msg,"fail")
        return redirect(url_for('api.modifyaccessright'))


class Users(Resource):
    """class"""
    @login_required
    def get(self):

        update_login_history("users",current_user)
        target = request.args.get('target')


        if target == "add user":
            user = current_user

            usergroup_list = user.company.groups

            tenant_group = CompanyUserGroupOp.fetch_usergroup_by_name("Tenant")
            try:
                usergroup_list.remove(tenant_group)
            except:
                pass

            return render_template(
                'ajax_userform.html',
                groups=usergroup_list,
                savecontext="Submit",
                target_func="new",
                user_status="Active",
                user=None)

        elif target == "check email":
            email = request.args.get('email')
            if "@" not in email or ".com" not in email:
                return err + "invalid"
            user = fetch_user(email)
            if user:
                return err + "user exists"
            else:
                return proceed

        elif target == "check tel":
            tel = request.args.get('tel')
            if "+" in tel:
                return err + "invalid"
            user = fetch_user(tel)
            if user:
                return err + "user exists"
            else:
                return proceed

        elif target == "check id":
            natid = request.args.get('natid')
            if len(natid) < 6:
                return err + "invalid"
            user = fetch_user(natid)
            if user:
                return err + "user exists"
            else:
                return proceed

        else:
            users = current_user.company.users
            if current_user.username == "admin":
                users = fetch_all_users()

            user_data = user_details(users)

            userids = get_obj_ids(user_data)

            return render_template(
                "ajax_users.html",
                userids=userids,
                items=user_data
                )

    def post(self):
        #GLOBAL
        company = current_user.company

        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        national_id = request.form.get('natid')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        usergroup=request.form.get('usergroup')

        status = request.form.get('status')

        target = request.form.get('target')

        print("EMMMMMMAIL",email)

        if name and name != 'None':
            if len(name) < 4:
                return err + "name too short"

        if email and email != 'None':
            if "@" not in email or ".com" not in email:
                return err + "invalid email"
            user = fetch_user(email)
            if user and user.email != email:
                return err + "user exists"

        if phone and phone != "None":
            if "+" in phone:
                return err + "invalid number"
            user = fetch_user(phone)
            if user and user.phone != user.phone:
                return err + "user exists"

        if national_id and national_id != "None":
            if len(national_id) < 6:
                return err + "invalid id"
            user = fetch_user(national_id)
            if user and user.national_id != national_id:
                return err + "user exists"

        if pass1:
            validate_pass = ValidatePass.validate_password(pass1,pass2)
            if  validate_pass=="no match":
                return err + "password no match"

        user_group_id=None
        if usergroup:               
            user_group_id = get_company_usergroup_id(usergroup,company)
            

        if target == "update user":
            userid = request.form.get('userid')

            if not userid:
                update_user = current_user
            else:
                user_id = get_identifier(userid)
                update_user = UserOp.fetch_user_by_id(user_id)

            modified_by = current_user.id
            company_id = None

            UserOp.update_user(update_user,name,phone,national_id,email,pass1,user_group_id,company_id,modified_by)

            if status:
                status_bool = get_bool(status)
                UserOp.update_status(update_user,status_bool)

            return "Updated successfully" + proceed

        else:

            if not user_group_id:
                return err + "usergroup not defined"

            if not pass1 and not pass2:
                return err + "passwords missing"

            if not name:
                return err + "name is missing"

            usercode = usercode_generator()
            is_present  = UserOp.fetch_user_by_usercode(usercode)
            if is_present:
                usercode = usercode_generator()#generate code again

            if not email:
                username = username_extracter(name)
                is_present2  = UserOp.fetch_user_by_username(username)
                if is_present2:
                    username = username_extracternum(name)#append random numbers to name
                    is_present3 = UserOp.fetch_user_by_username(username)
                    if is_present3:
                        username = username_extracternum(name) #generate username again

            else:
                username = username_exctractermail(email)

            new_user = UserOp(name,usercode,username,national_id,phone,email,pass1,4,user_group_id,company.id,current_user.id)
            new_user.save()

            company_properties = company.props
            for prop in company_properties:
                UserOp.relate(new_user,prop)

            return "User created successfully" + proceed



class AdminRegisterUser(Resource):
    """This class registers a new user --agents or caretakers."""
    @login_required
    def get(self):
        """admin action"""
        # form = UserRegForm()

        companies = CompanyOp.fetch_all_companies()
        company_usergroups = ["Manager","Accounts"]

        # owners = OwnerOp.fetch_all_owners()
        # place_holder_item = '--Select Owner--'
        # owners.insert(0,place_holder_item)
        # form.owner.choices = owners

        # user_group_list = fetch_all_usergroups()
        # tenant_group = UserGroupOp.fetch_usergroup_by_name("Tenant")
        # user_group_list.remove(tenant_group)
        # place_holder_item = '--Select Group--'
        # user_group_list.insert(0,place_holder_item)
        # form.usergroup.choices = user_group_list

        return Response(render_template(
            'admin_reg_user.html',
            companies=companies,
            company_usergroups=company_usergroups,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        """ Handle POST request for this view. Url ---> /signup """

        # form = UserRegForm()

        # uniquename = form.data.get('owner')
        # apartment = form.data.get('apartment')
        company = request.form.get('company')
        # ownerauto = request.form.get('ownerauto')

        email=request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        national_id = request.form.get('national_id')
        pass1 = request.form.get('p1')
        pass2 = request.form.get('p2')
        company_usergroup = request.form.get('usergroup')

        # if ownerauto:
        #     owner_id = OwnerOp.fetch_owner_by_uniquename(uniquename).id
        #     apartments = ApartmentOp.fetch_all_apartments_by_owner(owner_id)
        #     place_holder_item = '--Select Apartment--'
        #     apartments.insert(0,place_holder_item)
        #     form.apartment.choices = apartments
        #     return render_template('allocapartmentoptions.html', form=form)

        preventadmin = parse_for_admin(name)
        if preventadmin:
            flash("Please try a different name","fail")
            return redirect(url_for('api.adminregisteruser'))

        usercode = usercode_generator()

        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        if not email:
            username = username_extracter(name)
            is_present2  = UserOp.fetch_user_by_username(username)
            if is_present2:
                username = username_extracternum(name)#append random numbers to name
                is_present3 = UserOp.fetch_user_by_username(username)
                if is_present3:
                    username = username_extracternum(name) #generate username again

        else:
            check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
            if check_mail:
                flash("Email taken, try a different one or leave blank!","fail")
                return redirect(url_for('api.adminregisteruser'))
            username = username_exctractermail(email)

        if not national_id:
            national_id = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(national_id)
            nat_id = nationalid_generator() if check_dup else national_id
        else:
            nat_id = national_id

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        if not validate_pass:
            flash("Please set a password!","fail")
            return redirect(url_for('api.adminregisteruser'))
        elif validate_pass=="no match":
            flash("Passwords do not match","fail")
            return redirect(url_for('api.adminregisteruser'))
        else:
            company_usergroup_obj = None
            company_obj = CompanyOp.fetch_company_by_name(company) 
            print("Available Groups>>>>>>>",company_obj.groups)
            for obj in company_obj.groups:
                if str(obj) == company_usergroup:
                    company_usergroup_obj = obj
            if company_usergroup_obj:
                company_usergroup_id = company_usergroup_obj.id
            try:
                new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,4,company_usergroup_id,company_obj.id,1)
                new_user.save()

                company_properties = company_obj.props
                for prop in company_properties:
                    UserOp.relate(new_user,prop)

                msg=f"Registered, Note usercode: {usercode} & username: {username}."
                flash(msg,"success")
                
            except Exception as e:
                print("Registration failed>>>",e)
                msg=f"Registration failed"
                flash(msg,"fail")

            return redirect(url_for("api.adminregisteruser"))
        
class RegisterUser(Resource):
    """This class registers a new user."""
    @login_required
    def get(self):

        if current_user.username.startswith('qc'):
            pass
        else:
            user_group = current_user.company_user_group
            accessright = check_accessright(user_group,"add_user")
            if accessright != True:
                return Response(render_template('noaccess.html',name=current_user.name))

        props = fetch_all_apartments_by_user(current_user)

        # user_group_list = fetch_all_usergroups()
        # tenant_group = UserGroupOp.fetch_usergroup_by_name("Tenant")
        # user_group_list.remove(tenant_group)

        usergroups = ["Manager","Accounts","Caretaker"]

        return Response(render_template(
            'signup.html',
            name=current_user.name,
            company_usergroups=usergroups,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            props=props))

    @login_required
    def post(self):
        """ Handle POST request for this view. Url ---> /signup """

        prop = request.form.get('prop')
        email=request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        national_id = request.form.get('national_id')
        pass1 = request.form.get('p1')
        pass2 = request.form.get('p2')
        usergroup = request.form.get('usergroup')
        created_by = current_user.id

        usercode = usercode_generator()
        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        try:
            preventadmin = parse_for_admin(name)
            if preventadmin:
                flash("Please try a different name","fail")
                return redirect(url_for('api.registeruser'))

            if not email:
                username = username_extracter(name)
                is_present2  = UserOp.fetch_user_by_username(username)
                if is_present2:
                    username = username_extracternum(name)#append random numbers to name
                    is_present3 = UserOp.fetch_user_by_username(username)
                    if is_present3:
                        username = username_extracternum(name) #generate username again

            else:
                check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
                if check_mail:
                    flash("Email taken, try a different one or leave blank!","fail")
                    return redirect(url_for('api.registeruser'))
                username = username_exctractermail(email)
        except:
            flash("Check your inputs","fail")
            return redirect(url_for('api.registeruser'))

        if not national_id:
            national_id = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(national_id)
            nat_id = nationalid_generator() if check_dup else national_id
        else:
            nat_id = national_id

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        if not validate_pass:
            flash("Please set a password!","fail")
            return redirect(url_for('api.registeruser'))
        elif validate_pass=="no match":
            flash("Passwords do not match","fail")
            return redirect(url_for('api.registeruser'))
        else:
            company = current_user.company

            company_usergroup_obj = None
            for obj in company.groups:
                if str(obj) == usergroup:
                    company_usergroup_obj = obj
            if company_usergroup_obj:
                company_usergroup_id = company_usergroup_obj.id

            try:
                # REFACTOR REFACTOR 
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                if usergroup == "Caretaker":
                    new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,6,company_usergroup_id,company.id,current_user.id)
                    new_user.save()
                else:
                    new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,4,company_usergroup_id,company.id,current_user.id)
                    new_user.save()

                if usergroup == "Caretaker":
                    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
                    UserOp.relate(new_user,prop_obj)
                    ApartmentOp.update_caretaker(prop_obj,username)
                else:
                    company_properties = company.props
                    for prop in company_properties:
                        UserOp.relate(new_user,prop)

                msg=f"Registered, Note usercode: {usercode} & username: {username}."
                flash(msg,"success")
            except:
                msg=f"Registration failed."
                flash(msg,"fail")

            return redirect(url_for("api.registeruser"))

class SignUpCategory(Resource):
    """class"""
    def get(self):
        return Response(render_template("signupcategory.html"))
    def post(self):
        category=request.form.get('category')
        if not category:
            flash("Please select category","fail")
            return redirect(url_for('api.signupcategory'))
        elif category == "tenant":
            return redirect(url_for('api.tenantusersignupstageone'))
        elif category == "agent":
            return redirect(url_for('api.selfuserregisteragent'))
        else:
            return redirect(url_for('api.selfuserregisterowner'))

class AdminCreateAgent(Resource):
    """class"""
    def get(self):
        return Response(render_template("admin_createagent.html"))

    def post(self):
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        phone=request.form.get('tel')
        natid=request.form.get('natid')
        email=request.form.get('email')
        company_name = request.form.get('company')
        address = request.form.get('address')
        mail_box = request.form.get('mailbox')
        tel = request.form.get('company_tel')
        mail = request.form.get('company_mail')
        description = request.form.get('desc')
        pass1 = request.form.get('p1')
        pass2 = request.form.get('p2')

        created_by = 1
        usergroup_id = 3

        name = fname + " " + lname

        is_present  = UserOp.fetch_user_by_national_id(natid)
        
        if is_present:
            flash("Account exists already","fail")
            return redirect(url_for('api.userlogin'))

        if not natid:
            natid = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(natid)
            nat_id = nationalid_generator() if check_dup else natid
        else:
            nat_id = natid

        usercode = usercode_generator()
        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
        if check_mail:
            flash("Registration failed, email taken, try a different one","fail")
            return redirect(url_for('api.userlogin'))
        username = username_exctractermail(email)

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        if not validate_pass:
            flash("Please set a password!","fail")
            return redirect(url_for('api.admincreateagent'))
        elif validate_pass=="no match":
            flash("Passwords do not match","fail")
            return redirect(url_for('api.admincreateagent'))
        else:
            co = CompanyOp.fetch_company_by_name(company_name)
            if not co:
                company_obj = CompanyOp(company_name,address,mail_box,mail,tel,description)
                company_obj.save()

                group1 = CompanyUserGroupOp("Manager","administrator",company_obj.id)
                group1.save()
                group2 = CompanyUserGroupOp("Accounts","accounting officer",company_obj.id)
                group2.save()
                group3 = CompanyUserGroupOp("Caretaker","property caretaker",company_obj.id)
                group3.save()
                group4 = CompanyUserGroupOp("Tenant","property client",company_obj.id)
                group4.save()

                auto_assign_company_group_roles(company_name)

                user = UserOp(name,usercode,username,nat_id,phone,email,pass1,usergroup_id,group1.id,company_obj.id,created_by)
                user.save()

                msg='Account created successfully.'
                flash(msg,"success")
            else:
                msg='Account creation failed.'
                flash(msg,"success")

            return redirect(url_for('api.index'))

class SelfUserRegisterAgent(Resource):
    """class"""
    def get(self):
        return Response(render_template("selfsignupagent.html"))
    def post(self):
        remember = False
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        phone=request.form.get('phone')
        natid=request.form.get('natid')
        email=request.form.get('email')
        company_name = request.form.get('company')
        address = request.form.get('address')
        mail_box = request.form.get('mailbox')
        tel = request.form.get('company_tel')
        mail = request.form.get('company_mail')
        password = request.form.get('password')
        description = request.form.get('desc')

        created_by = 1
        usergroup_id = 3

        name = fname + " " + lname

        is_present  = UserOp.fetch_user_by_national_id(natid)
        
        if is_present:
            flash("Account exists already","fail")
            return redirect(url_for('api.userlogin'))

        usercode = usercode_generator()
        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
        if check_mail:
            flash("Registration failed, email taken, try a different one","fail")
            return redirect(url_for('api.signupcategory'))
        username = username_exctractermail(email)

        company_obj = CompanyOp(company_name,address,mail_box,mail,tel,description)
        company_obj.save()

        group1 = CompanyUserGroupOp("Manager","administrator",company_obj.id)
        group1.save()
        group2 = CompanyUserGroupOp("Accounts","accounting officer",company_obj.id)
        group2.save()
        group3 = CompanyUserGroupOp("Caretaker","property caretaker",company_obj.id)
        group3.save()
        group4 = CompanyUserGroupOp("Tenant","property client",company_obj.id)
        group4.save()

        auto_assign_company_group_roles(company_name)

        user = UserOp(name,usercode,username,natid,phone,email,password,usergroup_id,group1.id,company_obj.id,created_by)
        user.save()

        try:
            message1 = f"{fname} {lname} of Phone: {phone} & Email: {email} has just signed up as an agent({company_name}). \nPlease follow up immediately. \n\nThis message was auto sent by the system."
            # response = sms.send(message1, ["+254716674695","+254725538750","+254796247957"],"KIOTAPAY")
            response = sms.send(message1, ["+254716674695"],sender)

            recipient = [sms_phone_number_formatter(phone)]
            message2 = f"Dear {fname} {lname}, \nThank you for registering with us. We will be in touch as soon as possible. \nKiotaPay customer relations manager."
            response = sms.send(message2, recipient,sender)

        except:
            pass

        UserOp.update_status(user,False)

        login_user(user, remember=remember)
        return redirect(url_for('api.index'))

class SelfUserRegisterOwner(Resource):
    """class"""
    def get(self):
        return Response(render_template("selfsignupowner.html"))
    def post(self):
        remember = False
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        phone=request.form.get('phone')
        natid=request.form.get('natid')
        email=request.form.get('email')
        company_name = request.form.get('company')
        address = request.form.get('address')
        mail_box = request.form.get('mailbox')
        tel = request.form.get('company_tel')
        mail = request.form.get('company_mail')
        password = request.form.get('password')
        description = request.form.get('desc')

        created_by = 1
        usergroup_id = 2

        name = fname + " " + lname

        is_present  = UserOp.fetch_user_by_national_id(natid)
        
        if is_present:
            flash("Account exists already","fail")
            return redirect(url_for('api.userlogin'))

        usercode = usercode_generator()
        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
        if check_mail:
            flash("Registration failed, email taken, try a different one","fail")
            return redirect(url_for('api.selfuserregisterowner'))
        username = username_exctractermail(email)

        company_obj = CompanyOp(company_name,address,mail_box,mail,tel,description)
        company_obj.save()

        group1 = CompanyUserGroupOp("Owner","administrator",company_obj.id)
        group1.save()
        group2 = CompanyUserGroupOp("Accounts","accounting officer",company_obj.id)
        group2.save()
        group3 = CompanyUserGroupOp("Caretaker","property caretaker",company_obj.id)
        group3.save()
        group4 = CompanyUserGroupOp("Tenant","property client",company_obj.id)
        group4.save()

        auto_assign_company_group_roles(company_name)

        user = UserOp(name,usercode,username,natid,phone,email,password,usergroup_id,group1.id,company_obj.id,created_by)
        user.save()

        try:
            message1 = f"{fname} {lname} of Phone: {phone} & Email: {email} has just signed up as an owner({company_name}). \nPlease follow up immediately. \n\nThis message was auto sent by the system."
            response = sms.send(message1, ["+254716674695"],sender)

            recipient = [sms_phone_number_formatter(phone)]
            message2 = f"Dear {fname} {lname}, \nThank you for registering with us. We will be in touch as soon as possible. \nKiotaPay Customer relations manager."
            response = sms.send(message2, recipient,sender)

        except:
            pass

        # owner_user = UserOp(name,usercode,username,natid,phone,email,password,usergroup_id,company_name,created_by)
        # owner_user.save()

        owner_obj = OwnerOp.fetch_owner_by_phone(phone)
        if owner_obj:
            OwnerOp.update_natid(owner_obj,natid)
            owner_obj_apartments = owner_obj.apartments
            no_flush_err_owner_user = UserOp.fetch_user_by_national_id(natid)
            for apartment in owner_obj_apartments:
                ApartmentOp.relate(apartment,no_flush_err_owner_user)
                if not apartment.agency_managed:
                    owner_co_id = no_flush_err_owner_user.company_id
                    ApartmentOp.update_company(apartment,owner_co_id)
        else:
            UserOp.update_status(user,False)

        login_user(user, remember=remember)
        return redirect(url_for('api.index'))

        
class TenantUserSignUpStageOne(Resource):
    def get(self):
        return Response(render_template('tenantidsignup.html'))

    def post(self):
        national_id = request.form.get("national_id")
        existing_user = UserOp.fetch_user_by_national_id(national_id)
        if existing_user:
            flash("Account already set up, please login","success")
            return redirect(url_for("api.tenantusersignupstageone")) 
        tenant = TenantOp.fetch_tenant_by_nat_id(national_id)
        if tenant:
            if not tenant.house_allocated:
                flash("Contact management for house allocation","fail")
                return redirect(url_for("api.tenantusersignupstageone"))
            name = tenant.name
            tenantid = tenant.national_id
            return Response(render_template('tenantsignup.html',name=name,tenantid=tenantid))
        flash("Seems you haven't been allocated a house yet","fail")
        return redirect(url_for("api.tenantusersignupstageone"))

class TenantUserSignUpStageTwo(Resource):
    def get(self):
        pass

    def post(self):
        national_id = request.form.get("tenantid")
        pass1 = request.form.get("passwordone")
        pass2 = request.form.get("passwordtwo")
        remember = False

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(national_id)
        name = tenant_obj.name
        nat_id = national_id
        phone = tenant_obj.phone
        email = tenant_obj.email
        usergroup = 5

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        if not validate_pass:
            flash("Please set a password!","fail")
            return Response(render_template('tenantsignup.html',name=name,tenantid=national_id))
        elif validate_pass=="no match":
            flash("Passwords do not match","fail")
            return Response(render_template('tenantsignup.html',name=name,tenantid=national_id))
        else:
            password = pass1
            usercode = usercode_generator()
            if email:
                username = username_exctractermail(email)
            else:
                username = username_extracter(name)
                is_present2  = UserOp.fetch_user_by_username(username)
                if is_present2:
                    username = username_extracternum(name)#append random numbers to name
                    is_present3 = UserOp.fetch_user_by_username(username)
                    if is_present3:
                        username = username_extracternum(name) #generate username again

            is_present  = UserOp.fetch_user_by_usercode(usercode)
            if is_present:
                usercode = usercode_generator()#generate code again
            
            new_user = UserOp(name,usercode,username,nat_id,phone,email,password,usergroup)
            new_user.save()
            login_user(new_user, remember=remember)
            return redirect(url_for('api.index'))

class LandingPage(Resource):
    def get(self):
        if os.getenv("CURRENT_APP") == "app1":
            # return Response(render_template("landingtwo.html"))
            return redirect("https://kiotapay.co.ke")
        else:
            return redirect(url_for('api.userlogin'))
 
    def post(self):
        pass

class ContactUs(Resource):
    def get(self):
        return Response(render_template('contact.html'))
        
    def post(self):
        email = request.form.get('email')
        name = request.form.get('name')
        txt = request.form.get('message')

        if len(txt) > 500 or len(txt) < 10:
            print(">>>>>>>>>> ERIC AKO HII MTAA, LENGHT", len(txt),"Message", txt)
            abort(400)
        else:
            print(">>>>>>>> Message accepted",len(txt),"Message: ",txt)
            txt_obj = TextMessagesOp(name,email,txt)
            txt_obj.save()

class Features(Resource):
    def get(self):
        return Response(render_template('features.html'))
    def post(self):
        return None

class AboutUs(Resource):
    def get(self):
        return Response(render_template('aboutus.html'))
    def post(self):
        return None

class Pricing(Resource):
    def get(self):
        return Response(render_template('pricing.html'))
    def post(self):
        return None

class Privacy(Resource):
    def get(self):
        return Response(render_template('privacy.html'))
    def post(self):
        return None

class DbInitializer(Resource):
    def post(self):
        pass

    def get(self):

        g=CreateGroups()
        g.create_groups()
        ##################################################################################
        # c=CreateCompany()
        # c.create_companies()

        # cg=CreateCompanyGroups()
        # cg.create_groups()

        # up=UpdateUserCompany()
        # up.update_user_company()
        ##################################################################################
        a=CreateAdmin()
        a.create_admin_user()

        r=CreateRoles()
        r.create_roles()

        r.auto_assign_admin_roles()
        # r.auto_assign_roles()



        l=MakeRegions()
        l.make_regions()

        c=CreateChargeTypes()
        c.create_charge_types()

        return "Initialized"       
            
class UserLogin(Resource):
    """Handles login and access token generation."""

    def get(self):
        """Handle GET request for this view. Url ---> /signin"""

        loginpage = "login.html" if os.getenv("CURRENT_APP") == "app1" else "login2.html"

        return Response(render_template(loginpage))

    def post(self):
        identity = request.form.get('identifier')
        runcode = request.form.get('runcode')
        password = request.form.get('password')
        remember = False
        downtime = False

        print("Supplied logins >>>> ", "IDENTITY:",identity,"PASSW:",password)
        ### remember = True if request.form.get('remember') else False
        try:
            user = fetch_user(identity)
        except Exception as e:
            user = None
            downtime = True
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Login fail error",e)

        
        if runcode:
            if user:
                name = f'{user.name}'
                return render_template('ajaxloginname.html',alert=name)
            else:
                name = "Searching..."
                return render_template('ajaxloginsearching.html',alert=name)

        if user:
            if UserOp.password_is_valid(user,password):
                login_user(user, remember=remember)
                return redirect(url_for('api.index'))
            flash('Incorrect password!','fail')
            return redirect(url_for('api.userlogin'))
        elif downtime:
            response = sms.send("Login is experiencing issues", ["+254716674695"],sender)
            flash('Login failed, system undergoing maintenance!','fail')
            return redirect(url_for('api.userlogin'))
        flash('It seems you have no account yet!.','fail')
        return redirect(url_for('api.userlogin'))

class TenantDemoLogin(Resource):
    def get(self):
        print("XXXXXXXXXXXXX DEMO HIT XXXXXXXXXXXXXXX DEMO HIT XXXXXXXXXXXXXXXXXX DEMO HIT XXXXXXXXXXXXXXXXX DEMO HIT XXXXX")
        response = sms.send("Tenant Demo account has been accessed by ycombinator",["+254716674695","+254725538750"],"KIOTAPAY")
        user = UserOp.fetch_user_by_national_id("12341234")
        remember = False
        login_user(user, remember=remember)
        return redirect(url_for('api.index'))

class LandlordDemoLogin(Resource):
    def get(self):
        print("XXXXXXXXXXXXX DEMO HIT XXXXXXXXXXXXXXX DEMO HIT XXXXXXXXXXXXXXXXXX DEMO HIT XXXXXXXXXXXXXXXXX DEMO HIT XXXXX")
        response = sms.send("Agent/Landlord Demo account has been accessed by ycombinator",["+254716674695","+254725538750"],"KIOTAPAY")
        user = UserOp.fetch_user_by_national_id("12345678")
        remember = False
        login_user(user, remember=remember)
        return redirect(url_for('api.index'))

class ReportBug(Resource):
    def get(self):
        return Response(render_template('reportbugs.html'))
    def post(self):
        description = request.form.get('description')
        created_by = current_user.name
        bug_obj = BugsReportOp(description,created_by)
        bug_obj.save()
        msg = "Report success"
        return Response(render_template('reportbugs.html',name=current_user.name))

class ViewBugs(Resource):
    def get(self):
        bugs_list = []
        table = []
        # bug_list = BugsReport.query.all()
        # for bug in bug_list:
        #     bug_item = BugsReportOp.view(bug)
        #     bugs_list.append(bug_item)
        # table = BugTable(bugs_list)
        return Response(render_template('viewbugs.html',table=table))
  
class UserLogout(Resource):
    @login_required
    def get(self):
        logout_user()
        return redirect(url_for('api.userlogin'))
        
class DeleteUser(Resource):
    @login_required
    def get(self):
        """Handle GET request for this view. Url ---> /"""
        user_group = current_user.company_user_group
        accessright = check_accessright(user_group,"update_user")
        if accessright != True:
            return Response(render_template('noaccess.html',name=current_user.name))
        users_list = fetch_all_users()
        if request.method == 'GET':
            return Response(render_template('del_user.html',name=current_user.name,option_list=users_list))
    def post(self):
        usercode = request.form.get('usercode')

        del_user = UserOp.fetch_user_by_usercode(usercode)
        UserOp.delete(del_user)
        
        msg='User removed.'
        users_list = fetch_all_users()
    
        return Response (render_template('del_user.html',option_list=users_list,msgs=msg))

class UpdateUser(Resource):
    @login_required
    def get(self):
        """Handle GET request for this view. Url ---> /update/user"""

        userid = request.args.get('userid')

        user_id = get_identifier(userid)

        user = UserOp.fetch_user_by_id(user_id)

        if not user:
            print("chelaaal")
            user = current_user

        usergroup_list = user.company.groups

        tenant_group = CompanyUserGroupOp.fetch_usergroup_by_name("Tenant")
        try:
            usergroup_list.remove(tenant_group)
        except:
            pass

        return render_template(
            'ajax_userform.html',
            groups=usergroup_list,
            user_status="Active" if user.active else "Dormant",
            savecontext="Save Changes",
            user=user)

    @login_required
    def post(self):
        #GLOBAL
        company = current_user.company

        userid = request.form.get('userid')#this will be selected within the form
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        national_id = request.form.get('natid')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        usergroup=request.form.get('usergroup')

        tenantcheck = request.form.get('tenantcheck')


        if not userid:
            print("chelaaal")
            update_user = current_user
        else:
            user_id = get_identifier(userid)
            update_user = UserOp.fetch_user_by_id(user_id)



        if tenantcheck:
            if update_user.user_group_id == 5:
                return render_template("ajaxtenantuserupdate.html",tenantname=update_user.name)
            else:
                usergroup_list = company.groups
                for item in usergroup_list:
                    if item.name == "Tenant":
                        usergroup_list.remove(item)
                return render_template("restoreform.html",usergroup_option_list=usergroup_list)

        user_group_id=None

        if usergroup:
            # user_group_id = get_usergroup_id(usergroup)
            
            user_group_id = get_company_usergroup_id(usergroup,company)

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        
        if  validate_pass=="no match":
            flash("Passwords do not match!","fail")
            return redirect(url_for('api.updateuser'))

        modified_by = current_user.id
        company_id = None

        UserOp.update_user(update_user,name,phone,national_id,email,pass1,user_group_id,company_id,modified_by)
        
        msg='User info updated.'
        flash(msg,"success")

        return redirect(url_for("api.updateuser"))

# class UserAccount(Resource):
#     @login_required
#     def get(self):
#         results=[]
#         status = "active"
#         logged_user = current_user.username
#         user_obj_id = UserOp.fetch_user_by_username(logged_user).id
#         if logged_user == "admin":
#             apartment_list = Apartment.query.order_by(Apartment.id).all()
#             for apartment in apartment_list:
#                 dict_obj = ApartmentOp.view(apartment)
#                 results.append(dict_obj)
#             table = ApartmentTable(results)
#             return Response(render_template('account.html',status=status,table=table,name=current_user.name))
            
#         apartment_list = fetch_all_apartments_by_member(user_obj_id)#fetch all apartments associated with logged in user

#         for apartment in apartment_list:
#             dict_obj = ApartmentOp.view(apartment)
#             results.append(dict_obj)

#         table = ApartmentTable(results)

#         return Response(render_template('account.html',status=status,table=table,name=current_user.name))

class GetStarted(Resource):
    def get(self):
        return Response(render_template("getstarted.html"))

class ViewClients(Resource):
    @login_required
    def get(self):
        pass
    @login_required
    def post(self):
        pass     


class ViewNewClients(Resource):
    @login_required
    def get(self):
        user_id = current_user.id
        if user_id != 1 and user_id != 2:
            return Response(render_template('noaccess.html',name=current_user.name))
        else:
            dict_users = []
            userids = []
            new_clients = UserOp.fetch_all_inactive_users()
            for client in new_clients:
                userids.append(client.id)
                dict_user = UserOp.view(client)
                dict_users.append(dict_user)
            
            return Response(render_template(
                "view_new_clients.html",
                userids = userids,
                items=dict_users,
                name=current_user.name,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                group=current_user.company_user_group.name,
            ))
        
    @login_required
    def post(self):
        pass     
