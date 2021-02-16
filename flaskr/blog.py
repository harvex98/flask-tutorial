from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'select p.id, title, body, created, author_id, username'
        ' from post p join user u on p.author_id = u.id'
        ' order by created desc'
    ).fetchall ()
    return render_template('blog/index.html', posts=posts)

@bp.route('/basePost', methods=('GET', 'POST'))
@login_required
def create():
    g.mode = 'create'
    g.title = 'New Post'
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'insert into post(title, body, author_id)'
                ' values (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/basePost.html')

@bp.route('/<int:id>/basePost', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    g.mode = "update"

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        g.title = "Edit " + title
        error = None
        
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'update post set title = ?, body = ?'
                ' where id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/basePost.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('delete from post where id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

def get_post(id, check_author=True):
    post = get_db().execute(
        'Select p.id, title, body, created, author_id, username'
        ' from post p join user u on p.author_id = u.id'
        ' where p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post