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

app = Flask(__name__, static_url_path='/static' )

@app.route('/')
def main_route():
    global login_name
    return render_template('/main.html', login = login_name , login_email = login_email)

@app.route('/', methods=['POST'])
def main_route_post():
    return "yo"
#REGISTER 

@app.route('/user_register')
def user_register():
    return render_template('register.html',login = login_name)

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
        if login_name == "user" or login_name == "none":
            login_name = "none"
            login_email = "none"
        if login_name == "admin":
            return redirect("/")
        return render_template('register.html',status="registered")
    else:
        return render_template('register.html',status="email_exists")


@app.route('/user_logout')
def user_logout():
    global login_name
    global login_email
    login_name = "none"
    login_email = "none"   
    return redirect("/")     
#LOGIN 
@app.route('/user_login')
def user_login():
    global login_name
    return render_template('login.html', login = login_name)

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
                    return redirect("/")
                
            else:
                    
                    return render_template('login.html',status="password")

@app.route('/all_movies')
def all_movies():
    global login_name
    global login_email
    if login_name != 'none':
        moviez = movies.find({})
        output = []

        for movie in moviez:
            output.append(movie)
        
        print(len(output))
        if len(output) == 0:
            return render_template('all_movies.html' ,login =  login_name , status = "movie_not_found")
        
        return render_template('all_movies.html' ,login =  login_name , output = output , status = 'movie_found')
    else:
        return render_template('all_movies.html' ,login = login_name, status = 'not_logged_in')
    



   

#ANAZHTHSH TAINIAS
@app.route('/search_movie')
def search_movie():
    return render_template('search_movie.html' ,login =  login_name)

@app.route('/search_movie', methods=['POST'])
def search_movie_post():
    global login_name
    global login_email

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
        return render_template('search_movie.html',status="error", login = login_name )
    if title == "" and year == "" and actor == "":
        return render_template('search_movie.html',status="empty_fields", login = login_name )
    
    
    output =  movie_choose(title,year,actor,iterable)
    
    if len(output) == 0:
        return render_template('search_movie.html',status="empty_output", login = login_name )
    
        
    return render_template('search_movie.html',status="movie_found" , output = output, login = login_name )

#Compare every actor in list with given actor name. Can find movie even with name or surname of actor, individually.
def actors_search(actors , actor):
    counter = 0
    actor_word = actor.split(" ")
    for item in actors:
        item_split = item.split(" ")
        for i in item_split:
            for j in actor_word:
              if j.casefold().strip() ==  i.casefold().strip():
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
            if word.casefold().strip() == title_word.casefold().strip():
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
    global login_name
    return render_template('movie_info.html',login = login_name)

@app.route('/movie_info', methods=['POST'])
def movie_info_post():
    global login_name
    
    if login_name == "admin" or login_name == "user":
        output = []
        try:
            title = request.form['title']
        
        except Exception as e:
            return render_template('movie_info.html',status="error", login = login_name)
        if title == "":
            return render_template('movie_info.html',status="empty_fields", login = login_name)
       
#ADDED: NO CASE SENSITIVE SEARCH, same results on lower and uppercase searches.
        counter = 0
        try:
            moviez = movies.find({})
            title_split = title.split(" ")
            for movie in moviez:
                movie_split = movie['title'].split(" ")
                for i in movie_split:
                    for j in title_split:

                        if i.casefold().strip() == j.casefold().strip():
                            movie['_id'] = ""
                            if movie not in output:
                                movie = {"title":movie['title'],"description":movie['description'],"year":movie['year'],"actors":movie['actors']}
                                output.append(movie)
                            counter = 1
            if counter == 0:
                return render_template('movie_info.html',status="movie_not_found", login = login_name)
            else:
                return render_template('movie_info.html',status="movie_found" , output = output, login = login_name)
                #return jsonify(output)
        
        except Exception as e:
            render_template('movie_info.html',status="error", login = login_name)
                    
        
        
            
            #return jsonify(output)
    else:
        return render_template('movie_info.html',login = login_name ,status="not_logged_in")
   


@app.route('/ratings')
def ratings():

    global login_name
    global login_email
    if login_name == "admin":
        return render_template('ratings.html',login = login_name)
   
    elif login_name == "user":
        output = []
             
        if users.find({"email":login_email}).count() == 0:
                return render_template('ratings.html',status="not_found", login = login_name )
        else:
            user = users.find_one({"email":login_email})
            
            for i in user['rating']:
               output.append(i)
            
            if len(output) == 0 :
                 return render_template('ratings.html',status = "ratings_not_found" , login = login_name )
            
            return render_template('ratings.html',status = "ratings_found" , output = output , login = login_name )
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
             return render_template('ratings.html',login = login_name ,status='error' )
             
        if user_email == "":
            return "Please type a movie."
             
        if users.find({"email":user_email}).count() == 0:
                return render_template('ratings.html',login = login_name ,status="not_found" )
        else:
            
            user = users.find_one({"email":user_email})
            
            for i in user['rating']:
               output.append(i)
            
            if len(output) == 0 :
                 return render_template('ratings.html',status = "ratings_not_found", login = login_name  )
            
            return render_template('ratings.html',status = "ratings_found" , output = output , user = user_email, login = login_name )


            

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
    
    moviez = movies.find({})    
    counter  = 0
    for movie in moviez:
        if title.casefold().strip() == movie['title'].casefold().strip():
           counter  = counter + 1 
           for i in movie['comments']:
                output.append(i)
            
    if counter >= 2:
           return redirect("http://localhost:5000/comments_many")  
    
  
            
    
        
        
    if len(output) == 0:
        return  render_template('comments.html',status="comments_not_found")

    return  render_template('comments.html',status="comments_found",output = output , title = title)
        
@app.route('/all_comments')
def all_comments():
    global login_name
    global login_email

    if login_name == 'user':
            output = []
            user = users.find_one({"email":login_email})
            
            for i in user['comments']:
                output.append(i)
            if len(output) == 0:
                return render_template('all_comments.html',status="comments_not_found" , login = login_name)
            
            
            return render_template('all_comments.html',status="comments_found" , output = output , user = login_email , login = login_name)

    elif login_name == "admin":
        return render_template('all_comments.html',login="admin")
    else:
        return render_template('all_comments.html',login="none")

        

        
        

@app.route('/all_comments', methods=['POST'])
def all_comments_post():
    global login_name
    global login_email
    output = []

    if login_name == 'admin':
        try:
            email = request.form['email']
        except Exception as e:
            return render_template('all_comments.html',status="error" , login = login_name)
        
        if users.find({"email":email}).count() == 0:
            return render_template('all_comments.html',status="not_found" , login = login_name)
        else:
            user = users.find_one({"email":email})
            
            
            for i in user["comments"]:
                output.append(i)

            if len(output) == 0:
                return render_template('all_comments.html',status="comments_not_found" , login = login_name)

            return render_template('all_comments.html',status="comments_found" ,output = output , user = login_email , login = login_name)

    elif login_name == 'user':
        if users.find({"email":login_email}).count() == 0:
            return render_template('all_comments.html',status="error" , login = login_name)
        else:
            user = users.find_one({"email":login_email})
            
            for i in user['comments']:
                output.append(i)
            if len(output) == 0:
                return render_template('all_comments.html',status="comments_not_found")

        return render_template('all_comments.html',status="comments_found" ,output = output , user = login_email , login = login_name)
    else:
        return render_template('all_comments.html',status="none" , login = login_name)



@app.route('/delete_rating')
def delete_rating():
    global login_name
    return render_template('delete_rating.html',login = login_name)

@app.route('/delete_rating', methods=['POST'])
def delete_rating_post():
    global login_name
    global login_email

    if login_name == "admin":
        try:
            title = request.form['title']
            title = title.strip()

            year = request.form['year']
            year = year.strip()

            user_email = request.form['user']
            user_email = user_email.strip()
            rating = "0"
            
        except Exception as e:
                 return render_template('delete_rating.html',login = login_name , status = "user_not_found")
        if title == "" or rating == "" or user_email == "":
                return "You must fill both fields"
        else:
            if movies.find({"title":title , "year":year}).count() == 0:
              return render_template('delete_rating.html',login = login_name , status = "movie_not_found")
            elif movies.find({"title":title , "year":year}).count() >= 1:
                if users.find({"email":user_email}).count() == 0:
                    return render_template('delete_rating.html',login = login_name , status = "user_not_found")
                else:
                    
                    
                    ratings_list = []
                    ratings_list_users = []
                    movie = movies.find_one({"title":title , "year":year})
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
                        if title+":"+year not in  i:
                            ratings_list_users.append(i)
                
                    try: 
                            
                        movie = movies.update_one({"title":title , "year":year}, 
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

            elif movies.find({"title":title}).count() >= 2:
                 return redirect('/delete_rating_many')

    elif login_name == "user":
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
            elif  movies.find({"title":title}).count() == 1:
                
                
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
            
            elif movies.find({"title":title}).count() >= 2:
                return redirect('/delete_rating_many')
    
    else:
        return render_template('delete_rating.html',login = login_name )
     



@app.route('/rate_movie')
def rate_movie():
    return render_template('rate_movie.html' , login = login_name)

@app.route('/rate_movie', methods=['POST'])
def rate_movie_post():
    global login_email   
    global login_name

    if login_name != 'none':    
        try:
            
            title = request.form['title']
            title = title.strip()
            year = request.form['year']
            year = year.strip()
            rating = request.form['rating']
            rating =str(rating)
            rating = rating.strip()
        except Exception as e:
             
             return render_template('rate_movie.html', status = "error", login = login_name )
             
        if title == "" or rating == "":
            return "Please fill all the fields."
            
        if movies.find({"title":title , "year":year}).count() == 0:
            return render_template('rate_movie.html',status = "movie_not_found", login = login_name )
        
        elif movies.find({"title":title , "year":year}).count() < 0:
            return redirect('/rate_movie_many')
        else:


            try:  
                    movie = movies.find_one({"title":title ,"year":year})
                    user = users.find_one({"email":login_email})
                    
                    #GOES ON MOVIE
                    new_rating = login_email+":"+rating
                    
                    #GOES ON USER
                    new_rating_user = title+":"+year+":"+rating
                    
                    ratings_list = []
                    ratings_list_user = []
                    
                    
                    
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
                        return render_template('rate_movie.html',status = "already_rated", login = login_name )
                        
                   
                         
                         
                    if len(ratings_list_user) > 0:
                            counter = 0
                            for  i in ratings_list_user:
                                i.split(":")
                                a_rating = i[0]+":"+i[1]
                                if a_rating == title+":"+rating:
                                    counter = 1
                            if counter == 0:   
                                ratings_list_user.append(new_rating_user)
                    else:
                        ratings_list_user.append(new_rating_user)
                    
                        
                    
                    movie = movies.update_one({"title":title , "year":year}, 
                        {"$set":
                                {"rating":ratings_list}})
                    user = users.update_one({"email":login_email},
                        {"$set":
                                {"rating":ratings_list_user}})
                    
                    return render_template('rate_movie.html',status = "success", login = login_name )
            except Exception as e:
                    
                    return render_template('rate_movie.html',status = "error", login = login_name )
    else:
        return render_template('rate_movie.html',status = "login", login = login_name )
    







@app.route('/make_comment')
def make_comment():
    return render_template('make_comment.html',login = login_name)

@app.route('/make_comment', methods=['POST'])
def make_comment_post(): 
    global login_email   
    global login_name

    if login_name == 'user' or login_name == "admin":    
        try:
            
            title = request.form['title']
            title = title.strip()
            print(title)
            year = request.form['year']
            year = str(year)
            comment = request.form['comment']
            comment = comment.strip()
        except Exception as e:
             return render_template('make_comment.html',status = "error", login = login_name)
             
        if title == "" or comment == "":
            return "Please fill all the fields."
            
        if movies.find({"title":title , "year":year}).count() == 0:
            return render_template('make_comment.html',status = "movie_not_found", login = login_name)
        
        elif movies.find({"title":title , "year":year}).count() >= 1:
            try:    
                    
                    movie = movies.find_one({"title":title , "year":year})
                    user = users.find_one({"email":login_email})
                    #GOES ON MOVIE
                    new_comment = login_email+":"+comment
                    #GOES ON USER
                    new_comment_user = title+":"+year+":"+comment
                    
                    comments_list = []
                    comments_list_user = []
                    
                    
                    
                    for i in movie['comments']:
                        comments_list.append(i)
                    for i in user['comments']:
                        comments_list_user.append(i)
                    
                    if new_comment not in comments_list:
                        comments_list.append(new_comment)
                    
                    if new_comment_user not in comments_list_user:
                        comments_list_user.append(new_comment_user)
                    
                    movie = movies.update_one({"title":title , "year":year}, 
                        {"$set":
                                {"comments":comments_list}})
                    user = users.update_one({"email":login_email},
                        {"$set":
                                {"comments":comments_list_user}})
                    
                    return render_template('make_comment.html',status = "success" , login = login_name)
            except Exception as e:
                    return render_template('make_comment.html',status = "error", login = login_name) 
        else:
            return redirect('/make_comment_many') 
    else:
        return "You are not logged in"


@app.route('/insert_movie')
def insert_movie():
    return render_template('insert_movie.html',login = login_name)

@app.route('/insert_movie', methods=['POST'])
def insert_movie_post():
    global login_email
    output = []
    comments_list = []
    rating_list = []
    iterable = users.find({})
    try:
        title = request.form['title']
        title = title.strip()
        year = request.form["year"]
        year = str(year)
        year = year.strip()
        description = request.form['description']
        description = description.strip()
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
                comments = comments.strip()
                comments_list.append(login_email+":"+comments)
            
        if rating != "":
            rating = rating.strip()
            rating_list.append(login_email+":"+rating)
        

        actors = actors.split(",")
        for actor in actors:
            actor.strip()

        moviez = movies.find({})
        
        counter = 0
        for movie in moviez:
            if movie['title'].casefold().strip() == title.casefold().strip() and movie['year'].strip() == year.strip():
                counter = 1
        
        if counter == 1:
            return render_template('insert_movie.html',login = login_name,status= "movie_exists")

        movie = {"title":title,"year":year,"description":description,"actors":actors,"rating":rating_list , "comments":comments_list}
        movies.insert(movie)
        
        user_ratings_list = []
        user_comments_list = []

        user = users.find_one({"email":login_email})
        if users.find({"email":login_email}).count() > 0:
            
            
            for a_rating in user['rating']:
                    user_ratings_list.append(a_rating)
            for comment in user['comments']:
                user_comments_list.append(comment)

            if rating != "":
                user_ratings_list.append(title+":"+year+":"+rating)

            if comments != "":
                user_comments_list.append(title+":"+year+":"+comments)

                

                try: 
                        
                       user = users.update_one({"email":login_email}, 
                            {"$set":
                                    {"comments":user_comments_list,
                                    "rating":user_ratings_list
                                    
                                    
                                        }})
                except Exception as e:
                    return render_template('insert_movie.html',login = login_name,status= "error")

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
        title = title.strip()
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
            
            remove_comments_ratings(title , str(min_year))
            
            movies.delete_one({"title":title,"year":str(min_year)})

               

            return render_template('delete_movie.html' , login = login_name , status = "success")
        else:
            
            try:
                movie = movies.find_one({"title":title})
                movie_year = movie['year']
                
                remove_comments_ratings(title , movie_year)
                movies.delete_one({"title":title})

                
            except Exception as e:
                return render_template('delete_movie.html' , login = login_name , status = "error")

            return render_template('delete_movie.html' , login = login_name , status = "success")

def remove_comments_ratings(title , year):
            movie = movies.find_one({"title":title , "year":str(year)})
            

            #DELETE USER COMMENTS
            users_list = []
            for comment in movie['comments']:
                comment = comment.split(":")
                
                users_list.append(comment[0])

            movie_comment = title+":"+str(year)
            for user in users_list:

                user1 = users.find_one({"email":user})
                comments_list = []
                counter = 0
                
                for comment in user1["comments"]:
                    a_comment = comment.split(":")
                    user_comment = a_comment[0]+":"+a_comment[1]
                    if movie_comment.casefold().strip() != user_comment.casefold().strip():
                        comments_list.append(comment)

                user = users.update_one({"email":user}, 
                        {"$set":
                                {"comments":comments_list
                                    }})

            users_list = []
            for rating in movie['rating']:
                rating = rating.split(":")
                
                users_list.append(rating[0])

            movie_rating = title+":"+str(year)
            for user in users_list:

                user1 = users.find_one({"email":user})
                ratings_list = []
                counter = 0
                
                for rating in user1["rating"]:
                    a_rating = rating.split(":")
                    user_rating = a_rating[0]+":"+a_rating[1]
                    if movie_rating.casefold().strip() != user_rating.casefold().strip():
                        ratings_list.append(rating)

                user = users.update_one({"email":user}, 
                        {"$set":
                                {"rating":ratings_list
                                    }})
      
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
                                print(1)
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
                                print(1)
                except Exception as e:
                    return "error"
@app.route('/delete_user')
def delete_user():
    return render_template('delete_user.html',login = login_name)

@app.route('/delete_user', methods=['POST'])
def delete_user_post():
    global login_name
    global login_email
    if login_name == 'admin':
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
                    if users.find({"email":email,"category":"user"}).count() == 0 and email != login_email:
                        return render_template('delete_user.html',login = login_name , status = "cant_del_admin")
                    else:
                        try:
                            users.delete_one({"email":email})
                            delete_user_comments(email)
                            delete_user_ratings(email)
                            return render_template('delete_user.html',login = login_name , status = "success")
                        except Exception as e :
                            return render_template('delete_user.html',login = login_name , status = "error")
    elif login_name == 'user':
       
        try:
            response = request.form['response']
        except Exception as e:
            return render_template('delete_user.html',login = login_name , status = "error")
        string = "yes"
        
        if response.casefold().strip() == string.casefold().strip():
            try:
                users.delete_one({"email":login_email})
                delete_user_comments(login_email)
                delete_user_ratings(login_email)
                login_email = 'none'
                login_name = 'none'
                return render_template('delete_user.html',login = login_name , status = "deleted")
            except Exception as e:
                return render_template('delete_user.html',login = login_name , status = "error")
        else:
            return render_template('delete_user.html',login = login_name)
    else:
        return render_template('delete_user.html',login = login_name, status = "not_admin")
    
        
        
    
@app.route('/update_movie')
def update_movie():
    return render_template('update_movie.html',login = login_name)

@app.route('/update_movie', methods=['POST'])
def update_movie_post():
    global login_name
    global login_email

    if login_name == 'admin':
    
        try:
            title_up = request.form['title_up']
            title_up = title_up.strip()

            year_up = request.form['year_up']
            year_up = year_up.strip()

            title = request.form['title']
            title = title.strip()

            year = request.form['year']
            year = year.strip()

            description = request.form['description']
            description = description.strip()

            actors = request.form['actors']
            actors = actors.strip()

            actors_del = request.form['actors_del']
            actors_del = actors_del.strip()
            
        except Exception as e:
             return render_template('update_movie.html',login = login_name , status = "error")
        if title_up == "":
            return "You must type a Movie to update"
        if title == "" and year == "" and description == "" and actors == "" and actors_del == "":
             return render_template('update_movie.html',login = login_name , status = "empty")
        else:
            if movies.find({"title":title_up , "year":year_up}).count() == 0:
               return render_template('update_movie.html',login = login_name , status = "movie_not_found")
            else:
                movie1 = movies.find_one({"title":title_up ,"year":year_up})
                if title == "":
                    title = movie1["title"]
                if year == "":
                    year = movie1['year']
                if description == "":
                    description = movie1["description"]


          

                actors_list = []

                for actor in movie1['actors']:
                   
                    actors_list.append(actor)

               
                if actors != "" and actors_del != "":
                    
                    counter =  0
                    for actor in actors_list:
                    
                        if str(actor).casefold().strip() == actors.casefold().strip():
                            counter  = 1
                    if counter == 0:
                        actors_list.append(actors)

                    for actor in actors_list:
                        actor_del = actor
                        actor = str(actor).strip().casefold()
                        if actors_del.casefold().strip() == actor:

                            actors_list.remove(actor_del)

            
                elif actors!="" and actors_del =="":
                    
                    counter = 0
                    for actor in actors_list:
                        if str(actor).casefold().strip() == actors.casefold().strip():
                            counter = 1

                    if counter  == 0:
                        actors_list.append(actors)
                
                elif  actors == "" and actors_del != "":
                     for actor in actors_list:
                        actor_del = actor
                        actor = str(actor).strip().casefold()
                        if actors_del.casefold().strip() == actor:
                            actors_list.remove(actor_del)

                try: 
                    
                    movie = movies.update_one({"title":title_up , "year":year_up}, 
                        {"$set":
                                {"title":title,
                                 "year":year,
                                 "description":description,
                                 "actors":actors_list
                                    }})
                    
                    if title != title_up or year!= year_up:

                        comments_after_update(title , title_up , year , year_up)
                        ratings_after_update(title , title_up , year , year_up) 
                        
                    return render_template('update_movie.html',login = login_name , status = "success")
                except Exception as e:
                    return render_template('update_movie.html',login = login_name , status = "error")
    else:
         return render_template('update_movie.html',login = login_name , status = "not_logged")
    
def ratings_after_update(title , title_up , year , year_up):
                
                   

                #new_comment_user = title+":"+comment
                        
                        ratings_list = []
                        ratings_list_user = []
                        users_list = []
                        movie = movies.find_one({"title":title})
                        #user = users.find_one({"email":login_email})
                        counter = 0
                        
                        for i in movie['rating']:
                            ratings_list.append(i)
                       
                        
                        for i in ratings_list:
                            rating = i.split(":")
                            if rating[0] not in users_list:
                                users_list.append(rating[0])
                                

                        
                        
                        for user1 in users_list:
                            ratings_list_user = []

                            user2 = users.find_one({"email":user1})
                            
                            for rating in user2['rating']:
                                
                                a_rating = rating.split(":")
                                movie_name = a_rating[0]+":"+a_rating[1]
                                

                                
                                if movie_name ==   title_up+":"+year_up:
                                    movie_name = title
                                    movie_year  = year
                                    
                                    new_rating_user = movie_name +":"+movie_year+":"+a_rating[2]
                                    old_rating_user = title_up+":"+":"+year_up+":"+a_rating[2]

                                    if old_rating_user in ratings_list_user:
                                        ratings_list_user.pop(old_rating_user)

                                    if new_rating_user not in ratings_list_user:
                                        ratings_list_user.append(new_rating_user)

                            user = users.update_one({"email":user1},
                            {"$set":
                                    {"rating":ratings_list_user}})
    

def comments_after_update(title , title_up , year , year_up):
    
                        #new_comment_user = title+":"+comment
                        
                        comments_list = []
                        comments_list_user = []
                        users_list = []
                        movie = movies.find_one({"title":title , "year":year})
                        #user = users.find_one({"email":login_email})
                        
                        for i in movie['comments']:
                            comments_list.append(i)
                       
                        
                        for i in comments_list:
                            comment = i.split(":")
                            if comment[0] not in users_list:
                                users_list.append(comment[0])
                                

                        
                        
                        for user1 in users_list:
                            comments_list_user = []
                            user2 = users.find_one({"email":user1})
                            
                            for comment in user2['comments']:
                                
                                a_comment = comment.split(":")
                                movie_name = a_comment[0]
                                movie_year = a_comment[1]
                                

                                
                                    
                                if movie_name+":"+movie_year == title_up+":"+year_up:
                                    movie_name = title
                                    movie_year = year
                                    
                                new_comment_user = movie_name +":"+movie_year+":"+a_comment[2]
                                old_comment_user = title_up+":"+year_up+":"+a_comment[2]

                                if old_comment_user in comments_list_user:
                                    comments_list_user.pop(old_comment_user)

                                if new_comment_user not in comments_list_user:
                                    comments_list_user.append(new_comment_user)

                            user = users.update_one({"email":user1},
                            {"$set":
                                    {"comments":comments_list_user}})


@app.route('/delete_comment')
def delete_comment(): 
    return render_template('delete_comment.html',login = login_name )

@app.route('/delete_comment', methods=['POST'])
def delete_comment_post(): 
    global login_name
    global login_email

    if login_name == "admin":
            try:
                title = request.form['title']
                title = title.strip()
                year = request.form['year']
                year= str(year)
                year = year.strip()
                user_email = request.form['user']
                user_email = user_email.strip()
                comment = request.form['comment']
                comment = comment.strip()
            except Exception as e:
                return render_template('delete_comment.html',login = login_name , status="error")
        
            if users.find({"email":user_email}).count() == 0:
                return render_template('delete_comment.html',login = login_name , status="user_not_found")
            if movies.find({"title":title , "year":year}).count() == 0:
               
               return render_template('delete_comment.html',login = login_name , status = "movie_not_found")
            elif movies.find({"title":title , "year":year}).count() >= 1:
            
                
                
                comments_list = []
                comments_list_users = []
                movie = movies.find_one({"title":title , "year":year})
                user = users.find_one({"email":user_email})
                
                string = user_email+":"+comment
                counter_del = 0 
                for i in movie['comments']:
                    if string.strip() != i.strip():
                            comments_list.append(i)
                    else:
                        counter_del = counter_del + 1
                
                if counter_del == 0:
                    return render_template('delete_comment.html',login = login_name , status="comment_not_found")

                string = title+":"+year+":"+comment
                for i in user["comments"]:
                    if string.casefold().strip() != i.casefold().strip():
                        comments_list_users.append(i)
              
                try: 
                        
                    movie = movies.update_one({"title":title , "year":year}, 
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

            
            
    elif login_name == "user":
        try:
            title = request.form['title']
            title = title.strip()

            year = request.form['year']
            year = str(year)
            year = year.strip()

            comment = request.form['comment']
            comment = comment.strip()

        except Exception as e:
            return render_template('delete_comment.html',login = login_name , status = "movie_not_found")
                 
        if title == "" or comment == "" or login_email == "":
                return "You must fill both fields"
        else:
            if movies.find({"title":title , "year":year}).count() == 0:
             return render_template('delete_comment.html',login = login_name , status = "movie_not_found")
            elif movies.find({"title":title , "year":year}).count() >= 1:
                
                
                comments_list = []
                comments_list_users = []
                movie = movies.find_one({"title":title , "year":year})
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
                string = title+":"+year+":"+comment        
                for i in user["comments"]:
                    if i.strip() != string:
                        comments_list_users.append(i)
                    else:
                        del_counter_user = del_counter_user + 1
                   
                try: 
                    if del_counter >= 1:
                        movie = movies.update_one({"title":title , "year":year}, 
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
                    return render_template('delete_comment.html',login = login_name , status = "error")        
    else:
        return render_template('delete_comment.html',login = login_name )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
