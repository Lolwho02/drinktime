from app import db, login, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
	)


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index = True, unique = True)
	regtime = db.Column(db.DateTime, index = True, default = datetime.utcnow())
	last_seen = db.Column(db.DateTime, default = datetime.utcnow())
	email = db.Column(db.String(128), index = True, unique = True)
	password_hash = db.Column(db.String(128))
	drink = db.relationship('Drinks', backref='author', lazy='dynamic')
	private_stat = db.Column(db.Boolean)
	current_state = db.Column(db.Integer, default = 0)
	followed = db.relationship('User', secondary=followers,
    	primaryjoin=(followers.c.follower_id == id),
    	secondaryjoin=(followers.c.followed_id == id),
    	backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)



	def followed_drinks(self):
		followed = Drinks.query.join(
            followers, (followers.c.followed_id == Drinks.user_id)).filter(
                followers.c.follower_id == self.id)
		own = Drinks.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Drinks.drinkTime.desc())

	def det_currentstate(self):
		d = Drinks.query.filter_by(user_id=self.id).order_by(Drinks.drinkTime.desc()).all()
		if len(d) != 0:
			self.current_state = (datetime.utcnow() - d[0].drinkTime).days
		else: self.current_state = None


	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_reset_password_token(self, token_lifetime = 600):
		return jwt.encode({ 'reset_password':self.id,
							'exp':time()+token_lifetime }, app.config['SECRET_KEY'],
						  algorithm= 'HS256').decode('utf-8')
	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'], algorithms = ['HS256'])['reset_password']
		except:
			return None
		return User.query.get(id).firstI

@login.user_loader #настройка flask_login user_loader на БД
def load_user(id):
	return User.query.get(int(id))


class Drinks(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	isDrinking = db.Column(db.Boolean)
	drinkTime = db.Column(db.DateTime, index = True, default = datetime.utcnow())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))