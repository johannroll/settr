import os
import spotipy
import json
import urllib.parse
import pdfkit
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, json 
from flask_login import login_required, current_user
from spotipy.oauth2 import SpotifyClientCredentials
from redmail import gmail
from .models import User, Setlist, Song, Email
from . import db


main = Blueprint('main', __name__)
    
gmail.username = os.environ['username']
gmail.password = os.environ['password']


@main.route('/')
def start():
    return render_template('index.html', isStart=True)


@main.route('/profile')
@login_required
def profile():
    return render_template('Profile.html', name=current_user.name)


@main.route('/newsetlist', methods=['GET', 'POST'])
@login_required
def newsetlist():
    if request.method == 'POST':

        setlst = request.form.get('setlist')
         
        setName = Setlist(set_name=setlst, user_id=current_user.id)
        db.session.add(setName)
        db.session.commit()
        flash('Setlist added!', category='success')
        
        setlist = Setlist.query.filter_by(set_name=setlst).first()
        songs= Song.query.filter_by(songs_id=setlist.set_id).order_by(Song.position.asc()).all()
        song_count = 0
        for song in songs:
            song_count += 1 
        return render_template('search.html', setlist=setlist, name=setlist.set_name, song_count=song_count)                                      
    else:
        return render_template('newsetlist.html')
        

@main.route('/search/<name>', methods=['GET','POST'])
@login_required
def search(name): 
    if request.method == 'POST':
        search = request.form.get('search')
        
        result = spotify_data(search)
        items = json.dumps(result.veri)
        results = json.loads(items)
        
        de_name = urllib.parse.unquote(name)
        setlist = Setlist.query.filter_by(set_name=de_name).first()    
        songs= Song.query.filter_by(songs_id=setlist.set_id).order_by(Song.position.asc()).all()   
        song_count = 0
        for song in songs:
            song_count += 1
        return render_template('search.html', results=results, setlist=setlist, name=de_name, songs=songs, song_count=song_count) 
    else:
        de_name = urllib.parse.unquote(name)
        setlist = Setlist.query.filter_by(set_name=de_name).first()    
        songs= Song.query.filter_by(songs_id=setlist.set_id).order_by(Song.position.asc()).all()
        song_count = 0
        for song in songs:
            song_count += 1   
        return render_template('search.html', setlist=setlist, name=de_name, songs=songs, song_count=song_count) 
    
 
@main.route('/viewsetlists', methods=['GET'])
@login_required
def viewsetlists():
    setlists = Setlist.query.filter_by(user_id=current_user.id)
    return render_template('viewsetlists.html', setlists=setlists, name=setlists)


@main.route('/songsinset/<name>')
@login_required
def songsinset(name):
    de_set_name = urllib.parse.unquote(name)  
    setlist = Setlist.query.filter_by(set_name=de_set_name).first()
    songs = Song.query.filter_by(songs_id=setlist.set_id).order_by(Song.position.asc()).all()
    #songs = Song.query.filter_by(songs_id=setlist.set_id).all() #.order_by(Song.position.asc())
    return render_template('songsinsetlist.html', setlist=setlist, songs=songs, name=setlist.set_name)


@main.route('/addrecipients/<name>/', methods=['GET','POST'])
@login_required
def addrecipients(name):
    de_set_name = urllib.parse.unquote(name)  
    setlist = Setlist.query.filter_by(set_name=de_set_name).first()
   
    try:
        if request.method == 'POST':
            email_address = request.form.get('recipient')
            new_recipient = Email(email_add=email_address, user_id=current_user.id, set_id=setlist.set_id)
            db.session.add(new_recipient)
            db.session.commit()
            recipients = Email.query.filter_by(set_id=setlist.set_id).all()
            return render_template('/addrecipients.html', recipients=recipients, setlist=setlist, name=setlist.set_name)
        else:
            recipients = Email.query.filter_by(set_id=setlist.set_id)
            return render_template('/addrecipients.html', recipients=recipients, setlist=setlist, name=setlist.set_name)
    except:
        ('Flash something went wrong!')
        recipients = Email.query.filter_by(set_id=setlist.set_id)
        return render_template('/addrecipients.html', recipients=recipients, setlist=setlist, name=setlist.set_name)
    
    
@main.route('/removerecipient/<int:id>/<name>', methods=['GET'])
@login_required
def removerecipient(id, name):
    recipient = Email.query.get(id)
    
    de_set_name = urllib.parse.unquote(name)
    setlist = Setlist.query.filter_by(set_name=de_set_name).first()
    
    try:
        db.session.delete(recipient)
        db.session.commit()
        recipients = Email.query.filter_by(set_id=setlist.set_id)
        setlist = Setlist.query.filter_by(set_name=de_set_name).first()
        return render_template('/addrecipients.html', recipients=recipients, setlist=setlist, name=de_set_name, id=id)
    except:
        flash('Something went wrong!')
        recipients = Email.query.filter_by(set_id=setlist.set_id)
        setlist = Setlist.query.filter_by(set_name=name).first()
        return render_template('/addrecipients.html', recipients=recipients, setlist=setlist, name=name, id=id)
    

@main.route('/sharesetlist/<int:id>')
@login_required
def sharesetlist(id):
    setlist = Setlist.query.get(id)
    songs = Song.query.filter_by(songs_id=setlist.set_id).order_by(Song.position.asc()).all()
    recipients = Email.query.filter_by(set_id=id).all()
    user = User.query.filter_by(id=setlist.user_id).first()
    rendered = render_template('setlisttable.html', songs=songs, user=user, setlist=setlist)
    pdf = pdfkit.from_string(rendered, False)
    
    for recipient in recipients:
        gmail.send(
        subject="Your Settr Setlist",
        receivers=[recipient.email_add],
        attachments= {f'Setlist for {setlist.set_name}.pdf': pdf},
        html= render_template('emailbody.html', songs=songs, user=user, setlist=setlist)
        )

    flash('Setlist Sent!')
    return render_template('index.html', isStart=True)
    
    
@main.route('/deletesetlist/<int:id>')
@login_required
def deletesetlist(id):
    songs = Song.query.filter_by(songs_id=id).all()
    setlst = Setlist.query.filter_by(set_id=id).first()
        
    for song in songs:
            
        db.session.delete(song)
            
    db.session.delete(setlst)
    db.session.commit()
    flash('Setlist Deleted')
    setlists = Setlist.query.filter_by(user_id=current_user.id)
    return render_template('viewsetlists.html', setlists=setlists)
       

@main.route('/editsetlistname/<int:id>', methods=['GET', 'POST'])
@login_required
def editsetlistname(id):
    oldname = Setlist.query.filter_by(set_id=id).first()
    if request.method == 'POST':    
        new_name = request.form.get('newsetname')
        oldname.set_name=new_name
        db.session.commit()
        
        
        flash('Setlist Name Updated!')
        setlists = Setlist.query.filter_by(set_id=current_user.id)        
        return redirect(url_for('main.viewsetlists'))
    else:
        setlist = Setlist.query.filter_by(set_id=id).first()
        return render_template('editsetlistname.html', name=setlist.set_name, id=setlist.set_id)
  
  
      
@main.route('/addsongs/<set_name>/<name>/<artist>/<album>/<key>/<tempo>/<sig>/<mode>//<path:preview>')
@login_required
def addsongs(set_name, name, artist, album, key, tempo, sig, mode, preview):
    
    de_set_name = urllib.parse.unquote(set_name)  
    de_name = urllib.parse.unquote(name)
    de_artist = urllib.parse.unquote(artist)
    de_album = urllib.parse.unquote(album)
    
    setlist = Setlist.query.filter_by(set_name=de_set_name).first()
                  
    try:
        add_song = Song(song_name=de_name, song_artist=de_artist, song_album=de_album ,song_key=key , song_tempo=tempo, song_sig=sig, song_mode=mode, song_preview=preview, songs_id=setlist.set_id)
        db.session.add(add_song)
        db.session.commit()
        count = Song.query.filter_by(song_id=add_song.song_id).first()
        count.position = count.song_id
        db.session.add(count)
        db.session.commit()
            
        songs = Song.query.filter_by(songs_id=setlist.set_id).all() 
        song_count = 0
        for song in songs:
            song_count += 1  
        return render_template('search.html', setlist=setlist, name=setlist.set_name, songs=songs, song_count=song_count)
    except: 
        songs = Song.query.filter_by(songs_id=setlist.set_id).all()
        song_count = 0
        for song in songs:
            song_count += 1     
        return render_template('search.html', setlist=setlist, name=setlist.set_name, songs=songs, song_count=song_count)
    
    
@main.route('/updateList',methods=['POST','GET'])
@login_required
def updateList():
    
    if request.method == 'POST':    
        getorder = request.form['order']
        print(getorder)
        getorder_seperate = getorder.split(',')
        setlist = getorder[0].split(',')
        setlist = ''.join(setlist)
        del getorder_seperate[0]
        getorder_seperate = [str(item) for item in getorder_seperate]
        
        print('setid', +int(setlist))
        
        number_of_rows= Song.query.filter_by(songs_id=setlist).all()
        rows=number_of_rows
        rows = len(rows)
        print('rows', +rows)     
        order = getorder_seperate  
        print(order)                                
        count=0   
        for value in order:
             count +=1
             print('count', int(count))
             print('song_id', int(value))
                                 
             new_order = Song.query.filter_by(song_id=value).first()
             new_order.position = count
             db.session.add(new_order)
             db.session.commit()       
    return jsonify("Successfully Updated")

    
@main.route('/viewsongs/<name>')
@login_required
def viewsongs(name):
    
    setid = Setlist.query.filter_by(set_name=name).first()
    songs = Song.query.filter_by(songs_id=setid.set_id).order_by(Song.position.asc()).all() 
    setlist = Setlist.query.filter_by(set_id=setid.set_id).first()
    return render_template('search.html', songs=songs, setlist=setlist, name=name)


@main.route('/addperformancekey/<int:id>', methods=['POST', 'GET'])
@login_required
def addperformancekey(id):
    
    song = Song.query.filter_by(song_id=id).first() 
    setname = Setlist.query.filter_by(set_id=song.songs_id).first()
    
    if request.method == 'POST':
        perform_key = request.form.get('performkey')
        
        if not perform_key.isalpha():
            flash("Please enter a valid musical key between letters A-G!")
            songs = Song.query.filter_by(songs_id=setname.set_id).order_by(Song.position.asc()).all() 
            setlist = Setlist.query.filter_by(set_id=setname.set_id).first()
            
            return render_template('search.html', songs=songs, setlist=setlist, name=setlist.set_name)
        
        song.song_performance_key=perform_key
        db.session.commit()
        
        songs = Song.query.filter_by(songs_id=setname.set_id).order_by(Song.position.asc()).all()
        song_count = 0
        for song in songs:
            song_count += 1   
        setlist = Setlist.query.filter_by(set_id=setname.set_id).first()
        
        return render_template('search.html', songs=songs, setlist=setlist, name=setlist.set_name, song_count=song_count)
    else:
        songs = Song.query.filter_by(songs_id=setname.set_id).order_by(Song.position.asc()).all()
        song_count = 0
        for song in songs:
            song_count += 1   
        setlist = Setlist.query.filter_by(set_id=setname.set_id).first()
        
        return render_template('/viewsongs.html', songs=songs, setlist=setlist, name=setlist.set_name, song_count=song_count)    
    

@main.route('/deletesongs/<int:id>')
@login_required
def deletesongs(id):
    
    song = Song.query.get_or_404(id)
    setname = Setlist.query.filter_by(set_id=song.songs_id).first()
    tid = setname.set_id
    tname = setname.set_name
    
    try:
        db.session.delete(song)
        db.session.commit()
        
        flash('Song Deleted')
        
        songs = Song.query.filter_by(songs_id=tid).order_by(Song.position.asc()).all()
        song_count = 0
        for song in songs:
            song_count += 1 
        return render_template('search.html', songs=songs, setlist=setname, name=tname, song_count=song_count)
    except:
        song_count = 0
        for song in songs:
            song_count += 1
        flash('Something went wrong! Try Again!')
        return render_template('search.html', songs=songs, setlist=setname, name=tname, song_count=song_count)
         

class spotify_data():
    def __init__(self,name):
        os.environ['SPOTIPY_CLIENT_ID']        #os.getenv("Client_ID")  
        os.environ['SPOTIPY_CLIENT_SECRET']      #os.getenv("Client_Secret") 
        search_str = name
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.result = sp.search(search_str,5)
        self.veri=dict()
        #self.veri['raw']=self.result
        for track in self.result['tracks']['items']:
            
            my_dict={}
            my_dict["id"]=track['id']
            my_dict["cover_img"]=track['album']['images'][0]['url']
            my_dict["name"]=track['name']
            my_dict["preview"]=track["preview_url"]
            my_dict["artist"]=track['album']['artists'][0]['name']
            my_dict["album"]=track['album']['name']
            af = sp.audio_features(track['id'])
            my_dict["bpm"]=af[0]['tempo']
            my_dict["sig"]=af[0]['time_signature']
            my_dict["minor"]=af[0]['mode']
            raw_key = af[0]['key']
            
            if raw_key == 0:
                raw_key = 'C'
            elif raw_key == 1:
                raw_key = 'Db'
            elif raw_key == 2:
                raw_key = 'D'
            elif raw_key == 3:
                raw_key = 'Eb'
            elif raw_key == 4:
                raw_key = 'E'
            elif raw_key == 5:
                raw_key = 'F'
            elif raw_key == 6:
                raw_key = 'Gb'
            elif raw_key == 7:
                raw_key = 'G'
            elif raw_key == 8:
                raw_key = 'Ab'
            elif raw_key == 9:
                raw_key = 'A'
            elif raw_key == 10:
                raw_key = 'Bb'
            elif raw_key == 11:
                raw_key = 'B'
                
            my_dict["key"]= raw_key
            self.veri[my_dict["id"]] = my_dict
            
            
@main.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
    
