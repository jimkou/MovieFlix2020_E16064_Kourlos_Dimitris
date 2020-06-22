from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response , render_template
import json


client = MongoClient('mongodb://db:27017/')


db = client['MovieFlix']
users= db['Users']
movies = db['Movies']

login_email = "none"
login_name = "none"


app = Flask(__name__)


#REGISTER 
@app.route('/user_register')
def user_register():
    return render_template('register.html')

@app.route('/user_register', methods=['POST'])
def user_register_post():
    global login_name , login_email
    iterable = users.find({})
    try:
        email = request.form['email']
        name = request.form["name"]
        password = request.form['password']
        comments = []
        rating = []
        category = "user"
        
    except Exception as e:
        return render_template('register.html',status="error")
    if email == "" or name == "" or password == "":
        return render_template('register.html',status="null")
    if users.find({"email":email}).count()==0:
        user = {"email": email, "name": name,  "password": password, "comments": comments, "rating":rating, "category":category}
        users.insert(user)
        login_name = "none"
        login_email = "none"
        return render_template('register.html',status="registered")
    else:
        return render_template('register.html',status="email_exists")
        
#LOGIN 
@app.route('/user_login')
def user_login():
    return render_template('login.html')

@app.route('/user_login', methods=['POST'])
def user_login_post():
    global login_email
    global login_name
    iterable = users.find({})
    
    
    try:
        email = request.form['email']
        password = request.form['password']
    
    except Exception as e:
        return Response("bad content",status=401,mimetype='application/json')
    if email == "" or password == "":
        return "Email and password cant be blank"
    
    
    if users.find({"email":email}).count() == 0 :
        
        return render_template('login.html',status="email")
     
    else:
            
            
            if users.find({"email":email, "password":password}).count() != 0:
                
                    if users.find({"email":email,"category":"admin"}).count() >= 1:
                        login_name = "admin"
                    elif users.find({"email":email,"category":"user"}).count() >= 1:
                        login_name = "user"
                    
                    login_email = email
                    login_status = "none"
                    return render_template('main.html',privs=login_name)
                
            else:
                    
                    return render_template('login.html',status="password")
   
#ANAZHTHSH TAINIAS
@app.route('/search_movie')
def search_movie():
    return render_template('search_movie.html' ,login =  login_name)

@app.route('/search_movie', methods=['POST'])
def search_movie_post():
    iterable = movies.find({})
    output = []
    title = ""
    year = ""
    actor= ""
    try:
        title = request.form['title']
        year = request.form['year']
        actor = request.form['actor']
        
        
        
    except Exception as e:
        return render_template('search_movie.html',status="error")
    if title == "" and year == "" and actor == "":
        return render_template('search_movie.html',status="empty_fields")
    
    
    output =  movie_choose(title,year,actor,iterable)
    
    if len(output) == 0:
        return render_template('search_movie.html',status="empty_output")
    
        
    return jsonify(output)

#Compare every actor in list with given actor name. Can find movie even with name or surname of actor, individually.
def actors_search(actors , actor):
    counter = 0
    actor_word = actor.split(" ")
    for item in actors:
        item_split = item.split(" ")
        for i in item_split:
            for j in actor_word:
              if j.casefold() ==  i.casefold():
                  counter = 1
    if counter == 1:
            return True
    else:
        return False

def movie_search(movie , title):
    movie_split = movie.split(" ")
    title_split = title.split(" ")
    counter = 0

    for word in movie_split:
        for title_word in title_split:
            if word.casefold() == title_word.casefold():
                counter = 1
    if counter == 0:
        return False
    else:
        return True

#Search movies based on how many inputs filled by user.
def movie_choose(title,year,actor,iterable):
    output = []
    for movie in iterable:
        if title != "" and actor != "" and year != "":
                condition_actor = actors_search(movie['actors'],actor)
                condition_movie = movie_search(movie['title'] , title)
                if condition_movie  and movie['year'] == year and condition_actor:
                    if movie not in output:
                        output.append(movie)
        
        elif title != "" and actor != "" and year == "":
             condition_actor = actors_search(movie['actors'],actor)
             condition_movie = movie_search(movie['title'] , title)
             if condition_movie  and condition_actor :
                    if movie not in output:
                        output.append(movie)
        elif title != "" and actor == "" and year != "":
            condition_movie = movie_search(movie['title'] , title)
            if condition_movie   and movie['year'] == year:
                    if movie not in output:
                        output.append(movie)
        elif title != "" and actor == "" and year == "":
            condition_movie = movie_search(movie['title'] , title)
            if condition_movie  :
                if movie not in output:
                        output.append(movie)
        
        elif title == "" and actor != "" and year != "":
            condition_actor = actors_search(movie['actors'],actor)
            if movie['year']==year and  condition_actor :
                if movie not in output:
                        output.append(movie)
        elif title == "" and actor != "" and year == "":
            condition_actor = actors_search(movie['actors'],actor)
            if condition_actor :
                if movie not in output:
                        output.append(movie)
        elif title == "" and actor == "" and year != "":
            if movie["year"] == year:
                if movie not in output:
                    output.append(movie)

        movie["_id"]=None
    return output


#MOVIE INFO
@app.route('/movie_info')
def movie_info():
    return render_template('movie_info.html',login = login_name)
@app.route('/movie_info', methods=['POST'])
def movie_info_post():
    
    if login_name == "admin" or login_name == "user":
        output = []
        try:
            title = request.form['title']
        
        except Exception as e:
            return render_template('movie_info.html',status="error")
        if title == "":
            return render_template('movie_info.html',status="empty_fields")
        """
        
        if movies.find({"title":title}).count() == 0:
            return render_template('movie_info.html',status="movie_not_found")
        else:
            
            output.append("Movie information for :"+title)
            moviez = movies.find({})
            for movie in moviez:
                if movie['title'] == title:
                    movie['_id'] = ""
                    output.append(str(movie))
           """
#ADDED: NO CASE SENSITIVE SEARCH, same results on lower and uppercase searches.
        counter = 0
        try:
            moviez = movies.find({})
            title_split = title.split(" ")
            for movie in moviez:
                movie_split = movie['title'].split(" ")
                for i in movie_split:
                    for j in title_split:

                        if i.casefold() == j.casefold():
                            movie['_id'] = ""
                            if movie not in output:
                                output.append(str(movie))
                            counter = 1
            if counter == 0:
                return render_template('movie_info.html',status="movie_not_found")
            else:
                return jsonify(output)
        
        except Exception as e:
            render_template('movie_info.html',status="error")
                    
        
        
            
            #return jsonify(output)
    else:
        return render_template('movie_info.html',login = login_name ,status="not_logged_in")
   


@app.route('/ratings')
def ratings():
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
        return render_template('ratings.html',login = login_name)
    elif users.find({"email":login_email,"category":"user"}).count() >= 1:
        output = []
             
        if users.find({"email":login_email}).count() == 0:
                return render_template('ratings.html',status="not_found")
        else:
            user = users.find_one({"email":login_email})
            output.append("These are all the ratings from : "+login_email)
            for i in user['rating']:
               output.append(i)
            
            return jsonify(output)
    else:
       return render_template('ratings.html',login ="none")

@app.route('/ratings', methods=['POST'])
def ratings_post():
    global login_email
    output = []
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:

        try:
            user_email = request.form['user_email']
        except Exception as e:
             return render_template('ratings.html',login = login_name ,status='error')
             
        if user_email == "":
            return "Please type a movie."
             
        if users.find({"email":user_email}).count() == 0:
                return render_template('ratings.html',login = login_name ,status="not_found")
        else:
            
            user = users.find_one({"email":user_email})
            output.append("These are all the ratings from : "+user_email)
            for i in user['rating']:
               output.append(i)
            
            return jsonify(output)

@app.route('/comments')
def comments():
    return render_template('comments.html', login = login_name)

@app.route('/comments', methods=['POST'])
def comments_post():
    output = []
    
    try:
        title = request.form['title']
    except Exception as e:
         return render_template('comments.html',status='error')
         
    if title == "":
        return "Please type a movie."
         
    if movies.find({"title":title}).count()==0:
            return render_template('comments.html',status="not_found")
    else:
        movie = movies.find_one({"title":title})
        output.append("THESE ARE COMMENTS FOR THE MOVIE: "+title)
        for i in movie['comments']:
           output.append(i)
        
        return jsonify(output)
        
@app.route('/all_comments')
def all_comments():
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
        return render_template('all_comments.html',status="admin")
    elif  users.find({"email":login_email , "category":"user"}).count() >= 1:
        if users.find({"email":login_email}).count() == 0:
            return render_template('all_comments.html',status="error")
        else:
            output = []
            user = users.find_one({"email":login_email})
            
            for i in user['comments']:
                output.append(i)
                
        return jsonify(output)
    else:
        return render_template('all_comments.html',status="none")
        

        
        

@app.route('/all_comments', methods=['POST'])
def all_comments_post():
    output = []
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
        try:
            email = request.form['email']
        except Exception as e:
            return render_template('all_comments.html',status="error")
        
        if users.find({"email":email}).count() == 0:
            return render_template('all_comments.html',status="not_found")
        else:
            user = users.find_one({"email":email})
            
            output.append("These are the comments from user:"+email)
            for i in user["comments"]:
                output.append(i)
            return jsonify(output)
    elif users.find({"email":login_email,"category":"user"}).count() >= 1:
        if users.find({"email":login_email}).count() == 0:
            return render_template('all_comments.html',status="error")
        else:
            user = users.find_one({"email":login_email})
            
            for i in user['comments']:
                output.append(i)
                
        return jsonify(output)
        

@app.route('/delete_rating')
def delete_rating():
    return render_template('delete_rating.html',login = login_name)

@app.route('/delete_rating', methods=['POST'])
def delete_rating_post():
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
        try:
            title = request.form['title']
            user_email = request.form['user']
            rating = "0"
        except Exception as e:
                 return "ERROR!! Something went wrong with the data provided."
        if title == "" or rating == "" or user_email == "":
                return "You must fill both fields"
        else:
            if movies.find({"title":title}).count() == 0:
              return render_template('delete_rating.html',login = login_name , status = "movie_not_found")
            if users.find({"email":user_email}).count() == 0:
                return render_template('delete_rating.html',login = login_name , status = "user_not_found")
            else:
                
                
                ratings_list = []
                ratings_list_users = []
                movie = movies.find_one({"title":title})
                user = users.find_one({"email":user_email})
                
                string = user_email+":"+rating
                
                del_counter = 0
                for i in movie['rating']:
                    if user_email not in  i:
                            ratings_list.append(i)
                    else:
                        del_counter = del_counter + 1
                
                if del_counter == 0:
                      return render_template('delete_rating.html',login = login_name , status= "rating_not_found") 
                
                string = title+":"+rating
                for i in user["rating"]:
                    if title not in  i:
                       ratings_list_users.append(i)
              
                try: 
                        
                    movie = movies.update_one({"title":title}, 
                            {"$set":
                                    {"rating":ratings_list
                                        }})
                    
                    user = users.update_one({"email":user_email}, 
                        {"$set":
                            {"rating":ratings_list_users
                                }})
                                
                   
                        
                    return render_template('delete_rating.html',login = login_name , status= "success")
                    
                except Exception as e:
                   return render_template('delete_rating.html',login = login_name , status = "error")
    
    elif users.find({"email":login_email,"category":"user"}).count() >= 1:
        try:
            title = request.form['title']
            
            rating = "0"
        except Exception as e:
                 return render_template('delete_rating.html',login = login_name , status = "error")
        if title == "" or rating == "" or login_email == "":
                return "You must fill both fields"
        else:
            if movies.find({"title":title}).count() == 0:
             return render_template('delete_rating.html',login = login_name , status = "movie_not_found")
            else:
                
                
                ratings_list = []
                ratings_list_users = []
                movie = movies.find_one({"title":title})
                user = users.find_one({"email":login_email})
                
                
                del_counter = 0
                #ANAZHTHSH SXOLIOU STHN TAINIA
                string = login_email+":"+rating
                
                for i in movie['rating']:
                    if login_email not in i:
                    
                       ratings_list.append(i)
                    else:
                        del_counter = del_counter + 1    
                    
                del_counter_user = 0        
                #ANAZHTHSH SXOLIOU STON USER
                string = title+":"+rating       
                for i in user["rating"]:
                    if title not in i :
                        ratings_list_users.append(i)
                    else:
                        del_counter_user = del_counter_user + 1
                if del_counter == 0 :
                        return render_template('delete_rating.html',login = login_name , status="rating_not_found")
                try: 
                   
                        movie = movies.update_one({"title":title}, 
                                {"$set":
                                        {"rating":ratings_list
                                            }})
                      
                        user = users.update_one({"email":login_email}, 
                            {"$set":
                                {"rating":ratings_list_users
                                    }})
                                
                        return render_template('delete_rating.html',login = login_name , status = "success")
                    
                except Exception as e:
                    return "An error has occured!"
    
    else:
        return "Login to delete your comments!"

    
@app.route('/rate_movie')
def rate_movie():
    return render_template('rate_movie.html' , login = login_name)

@app.route('/rate_movie', methods=['POST'])
def rate_movie_post():
    global login_email   
    if users.find({"email":login_email,"category":"admin"}).count() >= 1 or users.find({"email":login_email,"category":"user"}).count() >= 1:    
        try:
            
            title = request.form['title']
            rating = request.form['rating']
            rating =str(rating)
        except Exception as e:
             return render_template('rate_movie.html', status = "error")
             
        if title == "" or rating == "":
            return "Please fill all the fields."
            
        if movies.find({"title":title}).count() == 0:
            return render_template('rate_movie.html',status = "movie_not_found")
        else:
            try:  
                    #GOES ON MOVIE
                    new_rating = login_email+":"+rating
                    
                    #GOES ON USER
                    new_rating_user = title+":"+rating
                    
                    ratings_list = []
                    ratings_list_user = []
                    
                    movie = movies.find_one({"title":title})
                    user = users.find_one({"email":login_email})
                    
                    for i in movie['rating']:
                        ratings_list.append(i)
                    for i in user['rating']:
                        ratings_list_user.append(i)
                    
                    rating_counter = 0
                    
                    if len(ratings_list) > 0:
                        for i in  ratings_list:
                            
                            if login_email  in i:
                                rating_counter = rating_counter + 1
                                #ratings_list.append(i)
                        
                                
                    if rating_counter == 0:
                        ratings_list.append(new_rating)
                    else:
                        return render_template('rate_movie.html',status = "already_rated")
                        
                   
                         
                         
                    if len(ratings_list_user) > 0:
                        for i in ratings_list_user:
                            if title not in i:
                                ratings_list_user.append(new_rating_user)
                    else:
                        ratings_list_user.append(new_rating_user)
                    
                        
                        
                    movie = movies.update_one({"title":title}, 
                        {"$set":
                                {"rating":ratings_list}})
                    user = users.update_one({"email":login_email},
                        {"$set":
                                {"rating":ratings_list_user}})
                    
                    return render_template('rate_movie.html',status = "success")
            except Exception as e:
                    return render_template('rate_movie.html',status = "error")
    else:
        return render_template('rate_movie.html',status = "login")
    
         
@app.route('/make_comment')
def make_comment():
    return render_template('make_comment.html',login = login_name)

@app.route('/make_comment', methods=['POST'])
def make_comment_post(): 
    global login_email   
    if users.find({"email":login_email,"category":"admin"}).count() >= 1 or users.find({"email":login_email,"category":"user"}).count() >= 1:    
        try:
            
            title = request.form['title']
            comment = request.form['comment']
        except Exception as e:
             return render_template('make_comment.html',status = "error")
             
        if title == "" or comment == "":
            return "Please fill all the fields."
            
        if movies.find({"title":title}).count() == 0:
            return render_template('make_comment.html',status = "movie_not_found")
        else:
            try:  
                    #GOES ON MOVIE
                    new_comment = login_email+":"+comment
                    #GOES ON USER
                    new_comment_user = title+":"+comment
                    
                    comments_list = []
                    comments_list_user = []
                    
                    movie = movies.find_one({"title":title})
                    user = users.find_one({"email":login_email})
                    
                    for i in movie['comments']:
                        comments_list.append(i)
                    for i in user['comments']:
                        comments_list_user.append(i)
                    
                    if new_comment not in comments_list:
                        comments_list.append(new_comment)
                    
                    if new_comment_user not in comments_list_user:
                        comments_list_user.append(new_comment_user)
                    
                    movie = movies.update_one({"title":title}, 
                        {"$set":
                                {"comments":comments_list}})
                    user = users.update_one({"email":login_email},
                        {"$set":
                                {"comments":comments_list_user}})
                    
                    return render_template('make_comment.html',status = "success")
            except Exception as e:
                    return render_template('make_comment.html',status = "error")
    else:
        return "You are not logged in"
    
@app.route('/insert_movie')
def insert_movie():
    return render_template('insert_movie.html',login = login_name)

@app.route('/insert_movie', methods=['POST'])
def insert_movie_post():
    output = []
    comments_list = []
    rating_list = []
    iterable = users.find({})
    try:
        title = request.form['title']
        year = request.form["year"]
        year = str(year)
        description = request.form['description']
        actors = request.form['actors']
        rating = request.form['rating']
        rating = str(rating)
        comments = request.form['comments']
    except Exception as e:
         return render_template('insert_movie.html',login = login_name,status= "error")
    
    if title == ""  and actor == "":
        return "You must fill at least title and 1 actor"
    else:
        if comments != "":
            comments_list.append(login_email+":"+comments)
            
        if rating != "":
            rating_list.append(login_email+":"+rating)
        actors = actors.split(",")
        
        movie = {"title":title,"year":year,"description":description,"actors":actors,"rating":rating_list , "comments":comments_list}
        movies.insert(movie)
        return render_template('insert_movie.html',login = login_name,status= "success")

@app.route('/delete_movie')
def delete_movie():
    return render_template('delete_movie.html' , login = login_name)

@app.route('/delete_movie', methods=['POST'])
def delete_movie_post():
    output = []
    iterable = movies.find({})
    try:
        title = request.form['title']
    except Exception as e:
        return render_template('delete_movie.html' , login = login_name , status = "error")
    
    if title == "" :
        return "You must fill one movie title to delete."
    else:
       if movies.find({"title":title}).count() == 0:
           return render_template('delete_movie.html' , login = login_name , status = "movie_not_found")
       elif movies.find({"title":title}).count() >= 2:
            for movie in iterable:
                if movie["title"] == title:
                    output.append(movie)
            min_year = 2020
            for movie in output:
                if int(movie["year"]) <= min_year:
                     min_year = int(movie["year"])
            
            movies.delete_one({"title":title,"year":str(min_year)})
            return render_template('delete_movie.html' , login = login_name , status = "success")
       else:
            movies.delete_one({"title":title})
            return render_template('delete_movie.html' , login = login_name , status = "success")
            
@app.route('/upgrade_user')
def upgrade_user():
    return render_template('upgrade_user.html' ,login = login_name)

@app.route('/upgrade_user', methods=['POST'])
def upgrade_user_post():
    try:
        email = request.form['email']
    except Exception as e:
        return render_template('upgrade_user.html' ,login = login_name , status = "error")
    if email == "" :
        return "You must fill one email to upgrade."
    else:
        if users.find({"email":email}).count() == 0:
           return render_template('upgrade_user.html' ,login = login_name , status = "user_not_found")
        else:
            try: 
                user = users.update_one({"email":email}, 
                    {"$set":
                            {"category":"admin"}})
                return render_template('upgrade_user.html' ,login = login_name , status = "success")
            except Exception as e:
                return render_template('upgrade_user.html' ,login = login_name , status = "error")
            
def delete_user_comments(user_email):
                comments_list = []
                comments_list_users = []
                movie_list = movies.find({})
                
                """
                string = user_email 
                counter_del = 0 
                for i in movie['comments']:
                    if string != i:
                            comments_list.append(i)
                            
                    else:
                        counter_del = counter_del + 1
                """
                #if counter_del == 0:
                   # return render_template('delete_comment.html',login = login_name , status="comment_not_found")

              
                try: 
                    for movie in movie_list:
                        if len(movie['comments']) > 0:
                            
                            
                            del_counter = 0
                            comments_list.clear()
                            for i in movie["comments"]:
                                if user_email not in i:
                                    comments_list.append(i)
                                else:
                                    del_counter = del_counter +1
                            if del_counter > 0:
                                
                                movie1= movies.update_one({"title":movie["title"]}, 
                                        {"$set":
                                                {"comments":comments_list
                                                    }})
                                
                            else:
                                print("lol")
                except Exception as e:
                    return "error"

def delete_user_ratings(user_email):
                
                rating_list = []
                
                movie_list = movies.find({})
   
                try: 
                    for movie in movie_list:
                        if len(movie['rating']) > 0:
                       
                            
                            del_counter = 0
                            rating_list.clear()
                            for i in movie["rating"]:
                                if user_email not in i:
                                    rating_list.append(i)
                                else:
                                    del_counter = del_counter +1
                            if del_counter > 0:
                                
                                movie1= movies.update_one({"title":movie["title"]}, 
                                        {"$set":
                                                {"rating":rating_list
                                                    }})
                                
                            else:
                                print("lol")
                except Exception as e:
                    return "error"
@app.route('/delete_user')
def delete_user():
    return render_template('delete_user.html',login = login_name)

@app.route('/delete_user', methods=['POST'])
def delete_user_post():
    
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
        try:
                email = request.form['email']
        except Exception as e:
                 return render_template('delete_user.html',login = login_name , status = "error")
        if email == "" :
                return "You must fill one email to delete."
        else:
                if users.find({"email":email}).count() == 0:
                    return render_template('delete_user.html',login = login_name , status = "user_not_found")
                else:
                    if users.find({"email":email,"category":"user"}).count() == 0:
                        return render_template('delete_user.html',login = login_name , status = "cant_del_admin")
                    else:
                        try:
                            users.delete_one({"email":email})
                            delete_user_comments(email)
                            delete_user_ratings(email)
                            return render_template('delete_user.html',login = login_name , status = "success")
                        except Exception as e :
                            return render_template('delete_user.html',login = login_name , status = "error")
    else:
        return render_template('delete_user.html',login = login_name, status = "not_admin")
        
        
    
@app.route('/update_movie')
def update_movie():
    return render_template('update_movie.html',login = login_name)

@app.route('/update_movie', methods=['POST'])
def update_movie_post():
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
    
        try:
            title_up = request.form['title_up']
            title = request.form['title']
            year = request.form['year']
            description = request.form['description']
            actors = request.form['actors']
            actors_del = request.form['actors_del']
            
        except Exception as e:
             return render_template('update_movie.html',login = login_name , status = "error")
        if title_up == "":
            return "You must type a Movie to update"
        if title == "" and year == "" and description == "" and actors == "" and actors_del == "":
             return render_template('update_movie.html',login = login_name , status = "empty")
        else:
            if movies.find({"title":title_up}).count() == 0:
               return render_template('update_movie.html',login = login_name , status = "movie_not_found")
            else:
                movie1 = movies.find_one({"title":title_up})
                if title == "":
                    title = movie1["title"]
                if year == "":
                    year = movie1['year']
                if description == "":
                    description = movie1["description"]
                if actors == "" and actors_del == "":
                    actors_list = []
                    actors = movie1['actors']
                    for i in movie1["actors"]:
                        actors_list.append(i)
                        
                elif ((actors!="" and actors_del != "")or (actors!="" and actors_del=="")):
                    actors_list=[]
                    actors_list.append(actors)
                    for i in movie1['actors']:
                        if i != actors_del and i not in actors_list:
                            actors_list.append(i)
                
                
                    
                    
                try: 
                    
                    movie = movies.update_one({"title":title_up}, 
                        {"$set":
                                {"title":title,
                                 "year":year,
                                 "description":description,
                                 "actors":actors_list
                                    }})
                    return render_template('update_movie.html',login = login_name , status = "success")
                except Exception as e:
                    return render_template('update_movie.html',login = login_name , status = "error")
    else:
         return "Only admin can update movies"
    


    
    
@app.route('/delete_comment')
def delete_comment():
    return render_template('delete_comment.html',login = login_name)

@app.route('/delete_comment', methods=['POST'])
def delete_comment_post(): 
    if users.find({"email":login_email,"category":"admin"}).count() >= 1:
        try:
            title = request.form['title']
            user_email = request.form['user']
            comment = request.form['comment']
        except Exception as e:
                return render_template('delete_comment.html',login = login_name , status="error")
        if title == "" or comment == "" or user_email == "":
                return "You must fill both fields"
        else:
            if movies.find({"title":title}).count() == 0:
               return render_template('delete_comment.html',login = login_name , status = "movie_not_found")
            if users.find({"email":user_email}).count() == 0:
                return render_template('delete_comment.html',login = login_name , status="user_not_found")
            else:
                
                
                comments_list = []
                comments_list_users = []
                movie = movies.find_one({"title":title})
                user = users.find_one({"email":user_email})
                
                string = user_email+":"+comment
                counter_del = 0 
                for i in movie['comments']:
                    if string != i:
                            comments_list.append(i)
                    else:
                        counter_del = counter_del + 1
                
                if counter_del == 0:
                    return render_template('delete_comment.html',login = login_name , status="comment_not_found")
                string = title+":"+comment
                for i in user["comments"]:
                    if string != i:
                        comments_list_users.append(i)
              
                try: 
                        
                    movie = movies.update_one({"title":title}, 
                            {"$set":
                                    {"comments":comments_list
                                        }})
                    
                    user = users.update_one({"email":user_email}, 
                        {"$set":
                            {"comments":comments_list_users
                                }})
                                
                   
                        
                    return render_template('delete_comment.html',login = login_name , status = "success")

                    
                except Exception as e:
                    return render_template('delete_comment.html',login = login_name , status = "error")

    
    elif users.find({"email":login_email,"category":"user"}).count() >= 1:
        try:
            title = request.form['title']
            
            comment = request.form['comment']
        except Exception as e:
                 return "ERROR!! Something went wrong with the data provided."
        if title == "" or comment == "" or login_email == "":
                return "You must fill both fields"
        else:
            if movies.find({"title":title}).count() == 0:
             return render_template('delete_comment.html',login = login_name , status = "movie_not_found")
            else:
                
                
                comments_list = []
                comments_list_users = []
                movie = movies.find_one({"title":title})
                user = users.find_one({"email":login_email})
                
                
                del_counter = 0
                #ANAZHTHSH SXOLIOU STHN TAINIA
                string = login_email+":"+comment
                for i in movie['comments']:
                    if i != string:
                    
                        comments_list.append(i)
                    else:
                        del_counter = del_counter + 1    
                    
                del_counter_user = 0        
                #Search the comment
                string = title+":"+comment        
                for i in user["comments"]:
                    if i != string:
                        comments_list_users.append(i)
                    else:
                        del_counter_user = del_counter_user + 1
                   
                try: 
                    if del_counter >= 1:
                        movie = movies.update_one({"title":title}, 
                                {"$set":
                                        {"comments":comments_list
                                            }})
                    if del_counter_user >= 1:    
                        user = users.update_one({"email":login_email}, 
                            {"$set":
                                {"comments":comments_list_users
                                    }})
                                
                   
                    if del_counter == 0 :
                        return render_template('delete_comment.html',login = login_name , status = "comment_not_found")
                   
                    else:
                        return render_template('delete_comment.html',login = login_name , status = "success")
                    
                except Exception as e:
                    return "An error has occured!"
    
    else:
        return "Login to delete your comments!"
            
            
    
           
@app.route('/user_add', methods=['POST'])
def user_add():
    
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=401,mimetype='application/json')
    if data == None:
        return Response("bad request",status=400,mimetype='application/json')
    if not "email" in data or not "password" in data:
        return Response("Information incompleted",status=500,mimetype="application/json")
    
    if users.find({"email":data["email"]}).count() == 0 :
        user = {"email": data['email'], "name": data['name'],  "password":data['password']}
        users.insert(user)
        return Response("was added to the MongoDB",status=200,mimetype='application/json') 
    else:
            return Response("was NOT added to the MongoDB",status=200,mimetype='application/json') 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
