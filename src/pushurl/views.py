from pushurl import app
from flask import (render_template, request, url_for, make_response, redirect)

urls = {}

@app.route('/')
def hello_world():
    return 'Hello World!!!'

@app.route('/<int:page_id>')
def page(page_id):
    return render_template('page.html', page_id=page_id)

@app.route('/<int:page_id>/event')
def event(page_id):
    s = ''
    if page_id in urls:
        s = 'data: %s\r\n\r\n' % urls[page_id]
    resp = make_response(s)
    resp.headers['Content-Type'] = 'text/event-stream'
    return resp

@app.route('/<int:page_id>/manage', methods=['GET', 'POST'])
def manage(page_id):
    if request.method == 'POST':
        urls[page_id] = request.form['url']
        return redirect(url_for('manage', page_id=page_id))
    else:
        return render_template('manage.html',
                               page_id=page_id,
                               url=urls.get(page_id, ''))

