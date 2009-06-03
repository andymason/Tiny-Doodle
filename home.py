import os
import base64
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import images

class Doodle(db.Model):
    image = db.BlobProperty()
    thumb = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    views = db.IntegerProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {
            'title': '',
            'heading': 'Tiny Doodle',
            'domain': os.environ["SERVER_NAME"],
            'mobile':   False,
            }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        
        # Detect if the user is using a mobile (iphone/android)
        # and use different theme
        uastring = self.request.headers.get('user_agent')
        if "Mobile" in uastring and "Safari" in uastring:
            path = os.path.join(os.path.dirname(__file__), 'templates/mobile.html')
            template_values['mobile'] = True
            
        self.response.out.write(template.render(path, template_values))

class SaveImage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Error: You can only POST here.')
    
    def post(self):
        # Get the date that's been posted
        img_base64 = self.request.get('img');
        update_id = self.request.get('key');
        
        #try:
        # Convert to PNG
        img_png = base64.decodestring(img_base64[22:])

        # Build thumb image
        img = images.Image(img_png)
        img.resize(width=32, height=32)
        img.im_feeling_lucky()
        thumb = img.execute_transforms(output_encoding=images.PNG)

        # Store or update in the DB
        if update_id == '' or update_id == False:
            im = Doodle()            
        else:
            doodle = Doodle()
            im = doodle.get_by_id(int(update_id))
        
        im.image = db.Blob(img_png)
        im.thumb = db.Blob(thumb)
        im.views = 0
        key = im.put()
    
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(key.id())
        
        #except Error:
            # Clear output and return an error code.
            #self.error(500)
        
class Image(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'));
        im = Doodle()
        result = im.get_by_id(int(id))
        result.views += 1
        result.put()
        
        result = im.get_by_id(id)
        if (result):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(result.image)
        else:
            self.response.out.write('no image found')

class Thumb(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'));
        im = Doodle()
        result = im.get_by_id(id)
        if (result):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(result.thumb)
        else:
            self.response.out.write('no image found')

class View(webapp.RequestHandler):
    def get(self, id):
        im = Doodle()
        result = im.get_by_id(int(id))
        
        template_values = {
            'title': 'Doodle ' + id,
            'heading': 'Doodle #' + id,
            'id': id,
            'views': result.views,
            'domain': os.environ["SERVER_NAME"],
            }
        path = os.path.join(os.path.dirname(__file__), 'templates/view.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
    [
        ('/', MainPage),
        ('/save', SaveImage),
        ('/image', Image),
        ('/thumb', Thumb),
        (r'/(.*)', View),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
