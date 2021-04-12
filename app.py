from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy
from operator import itemgetter
from flask_login import LoginManager ,  current_user , UserMixin  , login_user , login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import key


# setting up the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data0.db'

app.config['SECRET_KEY'] = key
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "login"


# translating sqlite things to python classes (but, I just ended up executing raw SQL commands)
class_lst = ["class1id", "class2id", "class3id", "class4id", "class5id", "class6id", "class7id", "class8id"]  
class_days = ["class1days", "class2days", "class3days","class4days","class5days","class6days", "class7days", "class8days"]
class Assistants(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.String, default = datetime.utcnow())
    namea = db.Column(db.String)
    nameb = db.Column(db.String)
    gender = db.Column(db.String)
    birthdate = db.Column(db.String)
    email = db.Column(db.String)
    contact = db.Column(db.String)
    class1id = db.Column(db.String)
    class1days = db.Column(db.String)
    class2id = db.Column(db.String)
    class2days = db.Column(db.String)
    class3id = db.Column(db.String)
    class3days = db.Column(db.String)
    class4id = db.Column(db.String)
    class4days = db.Column(db.String)
    class5id = db.Column(db.String)
    class5days = db.Column(db.String)
    class6id = db.Column(db.String)
    class6days = db.Column(db.String)
    class7id = db.Column(db.String)
    class7days = db.Column(db.String)
    class8id = db.Column(db.String)
    class8days = db.Column(db.String)

class Classes(db.Model):
    c_id = db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.String, default = datetime.utcnow())
    class_name = db.Column(db.String)
    time_from = db.Column(db.String)
    time_to = db.Column(db.String)
    main_name = db.Column(db.String)
    class_cat = db.Column(db.String)
    wd_or_we = db.Column(db.String)
    no_stu = db.Column(db.Integer)

class Result(db.Model):
    r_id = db.Column(db.Integer, primary_key = True)
    f_id = db.Column(db.Integer)
    content = db.Column(db.String)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String, unique = True)
    email_address = db.Column(db.String, unique = True)
    password_hash = db.Column(db.String)

    

    def __repr__(self):
        return f"<User {self.user_name}>"


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#James_the_user = User(user_name="JamesTheDev", email_address = "james@gmail.com", password_hash = "thisispassword123")

#James_the_user = User(user_name="NormalPeasant", email_address = "peasant@gmail.com", password_hash = "thisispassword123")
#James_the_user.set_password("passwordcontainsabignumber6")

#(x.set_password('DevPPstrong420420'))



# query functions 
def dict_factory(cursor, row): # to change cursor.raw_factory (which return a list) to this 'dict_factory' function 
    d = {}
    for idx, col in enumerate(cursor.description): # cursor.description is like it gives the headers (whcih will become keys)
        d[col[0]] = row[idx]  # column names are in index 0 (I guess)
    return d

def assistants_query(sort,filter = ('1','1')): # function for querying data from 'assistants' table 
    
    rt_dic = {}
    c = 0
    week = ['Sun','Mon', 'Tue', 'Wed', 'Thu', 'Fri', "Sat"]
    
    
    for i in class_lst: # outputting the joint table of ATs and their classes in the first two slots
        q = db.session.execute(f"""SELECT * FROM assistants JOIN classes WHERE assistants.{i} = classes.c_id AND {filter[0]} = {filter[1]}  """  )
        q.cursor.row_factory = dict_factory # changing the function (I guess)
        # *** BECAUSE OF THE STRUCTURE OF THE TABLE, I HAVE TO DO MULTIPLE QUERIES
        # After each query, I add all the dictionary output into one big dictionary
        temp = q.cursor.fetchall()
            
        for j in temp: # class day of the current query's class
            # days are in binary format, their indices indicating their value (mon, tue, etc)
            # but, 0001 is changed to 1 in database, so I had to reconstruct
            incomplete_days_format = j[class_days[class_lst.index(i)]]
            while len(incomplete_days_format) < 7:
                
                incomplete_days_format = "0" + incomplete_days_format
            
            
            # this is just turning the binary format into a more human-like visualization
            day_list =  []
            indx = 0
            for bi in incomplete_days_format:
                if bi == "1":    
                    day_list.append(week[indx])
                indx += 1
            j['query_no'] = class_days[class_lst.index(i)]
            j['class_day'] = day_list
            j[j['query_no']] = incomplete_days_format            
        for i in temp:
            c += 1
            rt_dic[c] = i
    
    # that one big dictionary got sorted by the key and a list of  k,v tuples is returned
    final_lst = sorted(rt_dic.items(), key= lambda x: x[1][str(sort)])
    return final_lst
       
def classes_query(sort, filter = ()):
    rt_dic = {}
    c = 0
    if filter == ():
        q = db.session.execute(f"""SELECT * FROM classes ORDER BY {sort}""")
        q.cursor.row_factory = dict_factory # changing the function (I guess)
            # *** BECAUSE OF THE STRUCTURE OF THE TABLE, I HAVE TO DO MULTIPLE QUERIES
            # After each query, I add all the dictionary output into one big dictionary
        for i in q.cursor.fetchall():
            c += 1
            rt_dic[c] = i
    else:
        q = db.session.execute(f"""SELECT * FROM classes WHERE {filter[0]} = '{filter[1]}'  ORDER BY {sort}""")
        q.cursor.row_factory = dict_factory # changing the function (I guess)
            # *** BECAUSE OF THE STRUCTURE OF THE TABLE, I HAVE TO DO MULTIPLE QUERIES
            # After each query, I add all the dictionary output into one big dictionary
        for i in q.cursor.fetchall():
            c += 1
            rt_dic[c] = i
    # that one big dictionary got sorted by the key and a list of  k,v tuples is returned
    final_lst = sorted(rt_dic.items(), key= lambda x: x[1][str(sort)])

    return final_lst

# updating functions

def assistants_update(fltr):
    q = db.session.execute(f"""
    SELECT id, namea, nameb, gender, birthdate, email, contact,
    class1id, class1days, class2id, class2days, class3id, class3days, class4id, class4days,
    class5id, class5days, class6id, class6days, class7id, class7days, class8id, class8days FROM assistants
    WHERE id = {fltr}""")
    q.cursor.row_factory = dict_factory
    temp = q.cursor.fetchall()
    for i in temp[0].keys():
        user_input = request.form.get(i)
        if user_input is not None:
            
            
            
                
            if i in class_days + class_lst:
                
                    try:
                        con = db.engine.connect()
                        int(user_input)
                        if int(user_input) == 0:
                            if i in ['class1id', 'class1days']:
                                pass
                            else:
                                con.execute(f"UPDATE assistants SET {i} = NULL WHERE id = {fltr}")
                            db.session.commit()
                        else:
                            con.execute(f"UPDATE assistants SET {i} = ? WHERE id = {fltr}", (user_input,))
                            db.session.commit()
                            con.close()
                    
            
                    except TypeError:
                        pass
                    except ValueError:
                        pass
            
            else:
                
                    con = db.engine.connect()
                    con.execute(f"UPDATE assistants SET {i} = ? WHERE id = {fltr}", (user_input,))
                    db.session.commit()
                    con.close()
    return temp

def classes_update(fltr):
    q = db.session.execute(f"SELECT * FROM classes WHERE c_id = {fltr}")
    q.cursor.row_factory = dict_factory
    temp = q.cursor.fetchall()
    for i in temp[0].keys():
        user_input = request.form.get(i)
        if user_input is not None:
            

            if i in ['c_id','time_from','time_to','no_stu' ]:
                try:
                    int(user_input)
                    con = db.engine.connect()
                    con.execute(f"UPDATE classes SET {i} =? WHERE c_id = {fltr}", (user_input,))
                    con.close()
                except TypeError:
                    pass
                except ValueError:
                    pass
            else:
                con = db.engine.connect()
                con.execute(f"UPDATE classes SET {i} = ? WHERE c_id = {fltr}", (user_input,))
                db.session.commit()
                con.close()

    
    return temp





# free-time-calculating functions

def compare(t1,t2):
    if int(t1[1]) < int(t2[0]):
        return (t1[1],t2[0])
    return ("It seems like the AT cannot be assigned in this time or something.", (t1,t2))

# function returning the free time of an AT
def free(lst:list): # take in a list of tuples
    lst.append(("0000","600"))
    lst.append(("2400","600"))
    transformed = [(int(xx), int(yy)) for (xx,yy) in lst] # transform items in each tuple to strings
    temp = sorted(transformed, key=itemgetter(0))
    rt_lst = []
    for i in temp:
        try:
            # put each tuple pair into 'compare' function and append the result into a list
            rt_lst.append(compare(i,temp[temp.index(i)+1]))

        except IndexError:
            # return the list at the end of the loop
            return rt_lst
    return rt_lst



def freetime_of_at(list_of_at):
    cls_lst = [("class1id", "class1days"), ("class2id", "class2days"), ("class3id", "class3days"),
               ("class4id", "class4days"), ("class5id", "class5days"), ("class6id", "class6days"),
               ("class7id", "class7days"), ("class8id", "class8days")]
    week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    rt_lst = []

    for i0 in list_of_at.keys():

        for day in week:
            temp_lst = []

            for x in cls_lst:
                if x[0] in list_of_at[i0].keys():
                    
                    if list_of_at[i0][x[1]][week.index(day)] == "1":
                        temp_lst.append(list_of_at[i0][x[0]])

            for i in temp_lst:
                if i is None:
                    temp_lst.remove(i)
            rt_tuple = (day, i0, free(temp_lst))
            rt_lst.append(rt_tuple)
    return rt_lst






# defining some variables I guess
q = db.session.execute("SELECT id FROM assistants ORDER BY id")
assistants_id_list = [i[0] for i in q.cursor.fetchall()]

q = db.session.execute("SELECT c_id FROM classes ORDER BY c_id")
classes_id_list = [i[0] for i in q.cursor.fetchall()]



@app.route('/')
def index():
    q = db.session.execute("SELECT id FROM assistants ORDER BY id")
    assistants_id_list = [i[0] for i in q.cursor.fetchall()]

    q = db.session.execute("SELECT c_id FROM classes ORDER BY c_id")
    classes_id_list = [i[0] for i in q.cursor.fetchall()]
    
    return render_template('index.html')

@app.route('/register', methods = ["POST"])
def register():
    search = request.form.get("search")
    if search == "mmsp":
        return ("okay")
    else:
        return render_template('register.html', search = search)

@app.route('/assistants', methods = ["POST", "GET"])
@login_required
def assistants():
    
    try:
        
        at_to_show = assistants_query("namea")
        

        
        return render_template("assistants.html", at_to_show = at_to_show)
    except ValueError:
        pass

@app.route('/classes', methods=["POST", "GET"])
@login_required
def classes():
    
    if request.form.get('filter-class') and  request.form.get('filter-class') != "NONE":
        cat = request.form.get('filter-class')
        try:
            class_lst = classes_query('class_name', ('class_cat', cat))
            return render_template("classes.html", class_lst = class_lst)
        except ValueError:
            pass
    else:
        try:
            class_lst = classes_query("c_id")
            return render_template("classes.html", class_lst = class_lst)
        except ValueError:
            pass

sortable_lst_assistants = {"sort_id":"id", "sort_namea":"namea",
                "sort_gender":"gender", "sort_c_id":"class_name"}
@app.route('/assistants/s/<sort>')
@login_required
def sorted_assistants(sort):
    x = None
    if sort in sortable_lst_assistants:
        x = sortable_lst_assistants[sort]
    else:
        return render_template('fourofour.html')
        
    
    at_to_show = assistants_query(x)
    return render_template('assistants.html', at_to_show=at_to_show)



@app.route('/assistants/p/<id>')
@login_required
def assistant_personal(id):
    x = None
    
    if (id) in [str(o) for o in assistants_id_list]:
        x = id
        
    else:
        return render_template('fourofour.html')
    
    at_to_show = assistants_query("namea", ("id", int(x)))
    c = 0
    free_time_dic = {}
    class_lst = ["class1id", "class2id", "class3id", "class4id", "class5id", "class6id", "class7id", "class8id"]
    for i in at_to_show:
        free_time_dic[class_lst[c]] = (i[1]['time_from'], i[1]['time_to'])
        free_time_dic[i[1]['query_no']] = (i[1][i[1]['query_no']])
        
        c += 1
    final_dic = {at_to_show[0][1]['namea']: free_time_dic}
    free_time = freetime_of_at(final_dic)

    
    return render_template('assistant.html', at_to_show=at_to_show, free_time = free_time)

@app.route('/atupdate/<id>', methods = ['POST', 'GET'])
@login_required
def assistant_update(id):
    if (session.get('_user_id')) != "1":
        return redirect(url_for('wentwrong'))
    else:
        x = None
    
        if (id) in [str(o) for o in assistants_id_list]:
            x = id
        
        else:
            return render_template('fourofour.html')
        at_to_show = assistants_update(int(x))

        return render_template("at-update.html", at_to_show = at_to_show)

sortable_lst_classes = {"sort_id":"c_id", "sort_name":"class_name",
                "sort_cats":"class_cat", "sort_time":"time_from",
                "sort_stu_no": "no_stu", "sort_mt":"main_name"}
@app.route('/classes/s/<sort>')
@login_required
def sorted_classes(sort):
    x = None
    
    if sort in sortable_lst_classes:
        x = sortable_lst_classes[sort]
        
    else:
        return render_template('fourofour.html')
    class_lst = classes_query(x)
    return render_template("classes.html", class_lst = class_lst)

@app.route('/classes/p/<id>')
@login_required
def class_personal(id):
    x = None
    
    if id in [str(o) for o in classes_id_list]:
        x = id
        
    else:
        return render_template('fourofour.html')
    
    class_to_show = classes_query('c_id', filter=("c_id", int(id)))
    at_to_show = assistants_query('namea', filter=("c_id", int(id)))
    no = len(at_to_show)

    return render_template('class.html', class_to_show = class_to_show, at_to_show=at_to_show, no = no)

@app.route('/clsupdate/<id>' , methods=["POST", "GET"])
@login_required
def class_update(id):
    if (session.get('_user_id')) != "1":
        return redirect(url_for('wentworong'))
    else:
        x = None
    
        if id in [str(o) for o in classes_id_list]:
            x = id
        
        else:
            return render_template('fourofour.html')
    
        class_to_show = classes_update(int(x))

        return render_template("cls-update.html", class_to_show = class_to_show)

# inserting new entry
@app.route('/assistants/insert', methods = ["GET", "POST"])
@login_required
def assistant_insert():
    if (session.get('_user_id')) != "1":
        return redirect(url_for('wentwrong'))
    else:
        if request.method == "POST":
            lst = {}
            lst['id'] = (assistants_id_list[-1] + 1)
            lst['date_created'] = (datetime.utcnow())
            
            for i in ['namea', 'nameb', 'gender', 'birthdate', 'email','contact',
    'class1id', 'class1days', 'class2id', 'class2days', 'class3id', 'class3days', 'class4id', 'class4days',
    'class5id', 'class5days', 'class6id', 'class6days', 'class7id', 'class7days', 'class8id', 'class8days']:
                x = request.form.get(i)
                
                if i in ['class1id', 'class1days', 'class2id', 'class2days', 'class3id', 'class3days', 'class4id', 'class4days',
                        'class5id', 'class5days', 'class6id', 'class6days', 'class7id', 'class7days', 'class8id', 'class8days']:
                        
                        try:
                            
                            if x is not None:
                                int(x)
                                lst[i] = x
                            else:
                                lst[i] = ''
                        except ValueError:
                            if i == "class1id" or i == "class1days":
                                return redirect(url_for('wentwrong'))
                            else:
                                lst[i] = None
                else:
                    lst[i] = x
            c = 0
            while len([(a,b) for (a,b) in lst.items()]) < 24:
                lst[str(c)] = None
                c += 1       
            
            con = db.engine.connect()
            con.execute('INSERT INTO assistants VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', tuple(lst.values()))
            db.session.commit()
            con.close()
            assistants_id_list.append(lst['id'])
        return render_template('at-insert.html')

@app.route("/classes/insert", methods = ["POST", "GET"])
@login_required
def class_insert():
    if (session.get('_user_id')) != "1":
        return redirect(url_for('wentwrong'))
    else:
        if request.method == "POST":
            lst = {}
            lst['c_id'] = classes_id_list[-1] + 1
            lst['date_created'] = datetime.utcnow()
            for i in ['class_name', 'time_from', "time_to", "main_name", "class_cat", "wd_or_we", "no_stu"]:
                lst[i] = None
                x = request.form.get(i)
                if i in ['time_from', "time_to", "no_stu"]:
                    try:
                        if x is not None:
                            int(x)
                            lst[i] = x

                    except ValueError:
                        return redirect(url_for('wentwrong'))
                else:
                    lst[i] = x
            con = db.engine.connect()
            con.execute('INSERT INTO classes VALUES (?,?,?,?,?,?,?,?,?)', tuple(lst.values()))
            db.session.commit()
            con.close()
            classes_id_list.append(lst['c_id'])
        return render_template('cls-insert.html')

@app.route('/assistants/delete/<id>', methods = ['GET', 'POST'])
def assistant_delete(id):
    
    if int(id) not in assistants_id_list:
        return render_template("fourofour.html")
    else:

        if (session.get('_user_id')) != "1":
            return redirect(url_for('wentwrong'))
        else:
            x = assistants_query('id', filter = ('id',id))
            if request.method == "POST":
                pw = request.form.get('password')
                user = User.query.filter_by(id = session['_user_id']).first()
                if user.check_password(pw):
                    db.session.execute(f"DELETE FROM assistants WHERE id = {id}")
                    db.session.commit()
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('wentwrong'))
        return render_template("at-delete.html", x = x)


@app.route('/classes/delete/<id>', methods = ['GET', 'POST'])
def classes_delete(id):
    
    if int(id) not in classes_id_list:
        return render_template("fourofour.html")
    else:

        if (session.get('_user_id')) != "1":
            return redirect(url_for('wentwrong'))
        else:
            x = classes_query('c_id', filter = ('c_id',id))
            if request.method == "POST":
                pw = request.form.get('password')
                user = User.query.filter_by(id = session['_user_id']).first()
                if user.check_password(pw):
                    db.session.execute(f"DELETE FROM classes WHERE c_id = {id}")
                    db.session.commit()
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('wentwrong'))
        return render_template("cls-delete.html", x = x)

# search query
@app.route('/results', methods = ['GET', "POST"])
def search():
    q = request.form.get('q')
    con = db.engine.connect()
    for i in q:
        if i == '"' or i == "'":
            return redirect(url_for('index'))
    else:
        ata = con.execute(f"SELECT id, namea FROM assistants WHERE namea LIKE '%{q}%'")
        atb = con.execute(f"SELECT id, nameb FROM assistants WHERE nameb LIKE '%{q}%'")
        clses = con.execute(f"SELECT c_id, class_name FROM classes WHERE class_name LIKE '%{q}%'")

        x = ata.fetchall()
        y = atb.fetchall()
        z = clses.fetchall()
        clst = []
        for i in x + y:
            i = (i[0], i[1], "assistants")
            clst.append(i)
            
        for i in z:
            i = (i[0], i[1], "classes")
            clst.append(i)
        
        
        
        c = 1
        for i in clst:
            
            i = (str(c), i[0], i[1], i[2])
            
            c+=1
            
            con.execute("INSERT INTO result VALUES (?,?,?,?)", i)
            db.session.commit()
        
        results = con.execute(f"SELECT f_id, content, type FROM result WHERE content LIKE '%{q}%'")
        result = results.fetchall()
        result0 = []
        idx_lst = []
        for i in result:
            if q.lower() in i[1].lower():
                idx_lst.append(i[1].lower().index(q.lower()))
        c = 0
        for i in result:
            result0.append((i[0],i[1],i[2],idx_lst[c]))
            c+=1
        result0 = sorted(result0, key = lambda x:x[3])

        
        con.execute("DELETE FROM result WHERE 1 = 1")
        db.session.commit()
        x = len(result0)
        
    con.close()

    return render_template('results.html', result = result0, q = q, x = x)

# user authentication stuffs
@app.route('/login', methods = ['POST', "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user_input = request.form.get('name')
    if user_input is not None:
        
    
        user = User.query.filter_by(user_name = user_input).first()
        if user is None or not user.check_password(request.form.get('password')):
            return redirect(url_for('login'))
        else:
            login_user(user)
            next_page = request.args.get('next')
            print(next_page)
            session.permanent = True
            if next_page is not None:
                return redirect(url_for(next_page))
            
            
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('assistants')
    
    return render_template('login.html')
    





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/wentwrong')
def wentwrong():
    return render_template('wentwrong.html')

if __name__ == "__main__":
    app.run(debug=True)