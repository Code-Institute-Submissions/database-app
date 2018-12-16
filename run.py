import os
from flask import Flask, render_template, request, flash, json, session, redirect, url_for, redirect
from flask_pymongo import PyMongo
import bcrypt
from bson.objectid import ObjectId
from time import strftime
import datetime
from pymongo import TEXT

# [i for i in dbm.neo_nodes.find({"_id": ObjectId(obj_id_to_find)})]

app = Flask(__name__)
app.secret_key = 'mysecret'
app.config['MONGO_DBNAME']='recipifydb'
app.config['MONGO_URI']='mongodb://migacz:1migacz@ds113482.mlab.com:13482/recipifydb'
mongo = PyMongo(app)


# Main page show all recipes from all users:
@app.route('/', methods=["POST", "GET"])

def index():
    user='You are not logged'
    if 'username' in session:
        user='Cheff: '+session['username']
    dbresponse=[]
    dbrecipes = mongo.db.recipes
    
     # search="burger new"
            # {"username" : {$regex : ".*son.*"}}
        # db.users.findOne({"username" : /.*son.*/i}); /case insentitve
# {"published": "publish"}
    # dbrecipes.save()
    # dbrecipes.ensureIndex({"recipe-name":1})
    # dbrecipes.drop_index([("recipe-description", TEXT)])
    
    #dbrecipes.create_index( [("recipe-description", TEXT), ("recipe-title", TEXT)], default_language='english'  )


    dbrecipes.ensure_index([("recipe-description","text"), ("recipe-name", "text") ])
    
    recipes  = dbrecipes.find({"published": "publish"})

    for recipe in recipes:
        dbresponse.append(recipe) 
    
    # Default settings for form typ    
    option1=['all'] # All types
    option2=['900']  # Cooking time 900 min /all
    option3=[] # Allergens none
    option4='' # User last
    search=''
    if request.method == 'POST': 
           
       
        dbresponse=[]
        cooktime=200
     #   if request.form.getlist('recipe-type')!=[''] and request.form.getlist('cooking-time')!=[''] and request.form.getlist('alergens')!=[]:
        option1 = (request.form.getlist('recipe-type'))
        option2 = (request.form.getlist('cooking-time'))
        option3 = (request.form.getlist('alergens'))
        search = (request.form.getlist('search'))
        recipe_type =(request.form.getlist('recipe-type'))
        
        print(search)
        # print(option1, option2, option3)

        if recipe_type == ['']:
            recipe_type = ["Main course", "Starter", "Desserts", "Juices"]
            option1=['all']

        if request.form.getlist('like')!=[]:
            
            print(request.form.getlist('like'))
        if search!=['']:
            recipes  = dbrecipes.find({"$and": [{"alergens": {"$nin": option3 }}, { "$text": { "$search":  "/.*"+search[0]+".*/i" } }, {"published": "publish"} , {"recipe-type": {"$in": recipe_type }}, {"cooking-time": {"$lte": int(option2[0]) }}  ] }).sort('date',-1)
        else:
            recipes  = dbrecipes.find({"$and": [{"alergens": {"$nin": option3 }}, {"published": "publish"} , {"recipe-type": {"$in": recipe_type }}, {"cooking-time": {"$lte": int(option2[0]) }}  ] }).sort('date',-1)
        
        for recipe in recipes:
            dbresponse.append(recipe)

    return render_template(
        "home.html",
        recipes=dbresponse,
        option1=option1[0],   # option1,2,3 For filter to "remmember" settings
        option2=option2[0], 
        option3=option3,
        option4=option4, 
        option5=search,
        user=user)

# Show only users recipes and allow user to edit them nicely
@app.route('/user_recipes', methods=["POST", "GET"])
def user_recipes():
    user='You are not logged'
    if 'username' in session:
        user='Cheff: '+session['username']
    else: 
       return redirect(url_for('index'))

    show_tooltips = 1
    dbrecipes = mongo.db.recipes
    recipes  = dbrecipes.find({"author": session['username']}).sort('date',-1)

    
    if request.method == 'POST':
        show_tooltips = 0
        ### Delete db querie:
        if request.form.getlist('delete')!=[]:
            dbrecipes.remove( {"_id": ObjectId(request.form.getlist('delete')[0])})
        ### Update db queries:
        # Cuisine 
        idrecipe = request.form.getlist('cuisine')[-1:]
        cuisinelist= request.form.getlist('cuisine')[0:len(request.form.getlist('cuisine'))-1]
        if request.form.getlist('cuisine')!=[]:
            dbrecipes.update( {"_id": ObjectId( idrecipe[0]) } ,{ "$set": {"cuisine": cuisinelist} }     )
        # Alergens
        idalergen = request.form.getlist('alergens')[-1:]
        alergenlist= request.form.getlist('alergens')[0:len(request.form.getlist('alergens'))-1]
        if request.form.getlist('alergens')!=[]:
            dbrecipes.update( {"_id": ObjectId( idalergen[0]) } ,{ "$set": {"alergens": alergenlist} }     )
        # Photo
        if request.form.getlist('image-url')!=[]:
            photo = request.form.getlist('image-url')[0]
            idphoto= request.form.getlist('idphoto')[0]
            dbrecipes.update( {"_id": ObjectId( idphoto) } ,{ "$set": {"image-url": photo} } )
        # Type
        if request.form.getlist('type')!=[]:
            rtype = request.form.getlist('recipe-type')[0]
            idtype= request.form.getlist('type')[0]
            dbrecipes.update_one( {"_id": ObjectId( idtype) } ,{ "$set": {"recipe-type": rtype } } )            
        # Time
        if request.form.getlist('time')!=[]:
            rtime = request.form.getlist('cooking-time')[0]
            idtime= request.form.getlist('time')[0]
            dbrecipes.update_one( {"_id": ObjectId( idtime) } ,{ "$set": {"cooking-time": rtime } } )
        # Name
        if request.form.getlist('name')!=[]:
            rname = request.form.getlist('recipe-name')[0]
            idname= request.form.getlist('name')[0]
            dbrecipes.update_one( {"_id": ObjectId( idname) } ,{ "$set": {"recipe-name": rname } } )
        # Ingredients
        if request.form.getlist('ingredients')!=[]:
            ring = request.form.getlist('ing')[0]
            iding= request.form.getlist('ingredients')[0]
            dbrecipes.update_one( {"_id": ObjectId( iding) } ,{ "$set": {"ingredients": ring.split(",") } } )
        # Description
        if request.form.getlist('description')!=[]:
            desc = request.form.getlist('recipe-description')[0]
            iddesc= request.form.getlist('description')[0]
            dbrecipes.update_one( {"_id": ObjectId( iddesc) } ,{ "$set": {"recipe-description": desc } } )
           # print(rname,idname)
        # Time
        if request.form.getlist('publish')!=[]:

            rid = request.form.getlist('publish')[0]
            rstage= request.form.getlist('stage')[0]
            dbrecipes.update_one( {"_id": ObjectId( rid) } ,{ "$set": {"published": rstage } } )      
            print(rid,rstage)
    dbresponse=[]

    for recipe in recipes:
        dbresponse.append(recipe)

    return render_template(
        "user_recipes.html",
        recipes=dbresponse,
        show_tooltips=show_tooltips, 
        user=user)

@app.route('/login', methods=["POST", "GET"])
def login():
    user='You are not logged'
    msg=''
    if 'username' in session:
        user='Cheff: '+session['username']

    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name' : request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        msg='Invalid username/password combination' 
    
    return render_template('login.html', user=user, msg=msg)
@app.route('/signup', methods=["POST", "GET"])
def signup():
    user='You are not logged'
    msg=''
    if 'username' in session:
        user='Cheff: '+session['username']

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})
    
        if existing_user is None:
            if request.form['password_check']==request.form['password'] and request.form['password'] is not None:
                if not len(request.form['password'])<5:
                    hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()) 
                    users.insert_one({'name' : request.form['username'], 'password' : hashpass})
                    session['username'] = request.form['username']
                    return redirect(url_for('index'))            
                else:
                    msg='Password is to short try at least 5 chars'
            else: 
                msg = 'Passwords dose not match'
        else: 
            msg='That username already exists!'  

    return render_template('signup.html', user=user, msg=msg)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('index'))


@app.route('/add_recipe', methods=["GET", "POST"])
def add_recipe():
    user='You are not logged'
    if 'username' in session:
        user='Cheff: '+session['username']
    else:
        return redirect(url_for('index'))  # Only for registerred users

    recipes=mongo.db.recipes
    recipes.insert({
    'likes': 0,
    'recipe-name' : "My new recipe" , #request.form['recipe-name'] 
    'recipe-type' : "Starter" , 
    'cooking-time': 15 , # Always change to int if its need to be int ...
    'cuisine': [] ,
    'alergens': [],
    'recipe-description': "Write here how to connect ingredients to make you delicious recipe",
    'image-url' : "",
    'ingredients' : [], # Convert string to list where "," is separator
    'author': session['username'],
    'date': strftime("%d/%m/%Y %H:%M"),
    'published': "draft"
    })

    return redirect(url_for('user_recipes'))

        # Here is a easy acces to all variables from form:
        # request.form['recipe-name']
        # request.form['cooking-time']
        # str(request.form.getlist('cuisine'))
        # str(request.form.getlist('alergens'))
        # request.form['recipe-description']
        # request.form['image-url']
        # request.form['ing']
        # session['username']
    
    #return render_template("add_recipe.html", user=user) 
    
@app.route('/stats', methods=["GET", "POST"])
def stats():
    user='You are not logged'
    if 'username' in session:
        user='Cheff: '+session['username']
    else:
        return redirect(url_for('index')) # Only for registerred users

    return render_template("stats.html", user=user)
    
    
if __name__ == '__main__':
     app.run(host=os.getenv('IP'), port=os.getenv('PORT'), debug=True, threaded=True)

    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port)