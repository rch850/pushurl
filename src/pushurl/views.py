from pushurl import app
from flask import (render_template, request, url_for, make_response, redirect)
from models import Page

@app.route('/')
def hello_world():
    return 'Hello World!!!'

@app.route('/<int:page_id>')
def page(page_id):
    if page_id <= 0 or 10 < page_id:
        return redirect(url_for('hello_world'))
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
    if page_id <= 0 or 10 < page_id:
        return redirect(url_for('hello_world'))
    page = Page.get_by_key_name(str(page_id))
    if request.method == 'POST':
        url = request.form['url']
        if url.startswith('http://') or url.startswith('https://'):
            if page:
                page.url = url
            else:
                page = Page(key_name=str(page_id), url=url)
            page.put()
        return redirect(url_for('manage', page_id=page_id))
    else:
        url = ''
        if page:
            url = page.url
        return render_template('manage.html',
                               page_id=page_id,
                               url=url)

