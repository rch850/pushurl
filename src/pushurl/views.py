from pushurl import app
from flask import (render_template, request, url_for, make_response, redirect)
from models import Page

@app.route('/')
def hello_world():
    return 'Hello World!!!'

@app.route('/<int:page_id>')
def page(page_id):
    return render_template('page.html', page_id=page_id)

@app.route('/<int:page_id>/event')
def event(page_id):
    s = ''
    page = Page.get_by_key_name(str(page_id))
    if page:
        s = 'data: %s\r\n\r\n' % page.url
    resp = make_response(s)
    resp.headers['Content-Type'] = 'text/event-stream'
    return resp

@app.route('/<int:page_id>/manage', methods=['GET', 'POST'])
def manage(page_id):
    if request.method == 'POST':
        Page.get_or_insert(str(page_id), url=request.form['url'])
        return redirect(url_for('manage', page_id=page_id))
    else:
        url = ''
        page = Page.get_by_key_name(str(page_id))
        if page:
            url = page.url
        return render_template('manage.html',
                               page_id=page_id,
                               url=url)

