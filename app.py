import os, json, random

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import Length, DataRequired, InputRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON

from flask_debugtoolbar import DebugToolbarExtension

NEED_IMPORT = False
SECRET_KEY = os.environ.get('SECRET_KEY')
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------------------------------------------------------
# database Models

teachers_goals = db.Table('teachers_goals',
                          db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.teacher_id')),
                          db.Column('goal_id', db.Integer, db.ForeignKey('goals.goal_id'))
                          )


class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    booking_ditails = db.Column(db.String(230))
    teacher_name = db.relationship('Teacher', back_populates='teacher_booking')
    week_day = db.Column(db.String(15))
    lesson_time = db.Column(db.String(10))
    client_name = db.Column(db.String(50))
    client_phone = db.Column(db.String(20))


class Teacher(db.Model):
    __tablename__ = 'teachers'
    teacher_id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(200))
    goal = db.relationship('Goal', secondary=teachers_goals, back_populates='teacher')
    schedule = db.Column(JSON)
    about = db.Column(db.Text)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'))
    teacher_booking = db.relationship('Booking', back_populates='teacher_name')


class RequestForm(db.Model):
    __tablename__ = 'reqforms'
    reqform_id = db.Column(db.Integer, primary_key=True)
    goal_name = db.Column(db.String(35))
    learning_time = db.Column(db.String(25))  # TimeForLearn
    client_name = db.Column(db.String(50))
    client_phone = db.Column(db.String(20))


class Goal(db.Model):
    __tablename__ = 'goals'
    goal_id = db.Column(db.Integer, primary_key=True)
    goal_cod = db.Column(db.String(15), unique=True, nullable=False)
    goal_name = db.Column(db.String(35), unique=True, nullable=False)
    teacher = db.relationship('Teacher', secondary=teachers_goals, back_populates='goal')


class Client(db.Model):
    __tablename__ = 'clients'
    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)


class TimeForLearn(db.Model):
    __tablename__ = 'timelearns'
    time_id = db.Column(db.Integer, primary_key=True)
    time_all = db.Column(JSON)


db.create_all()
# ---------------------------------------------------------
"""
Пример формирования запроса при связи many-to-many
teach_all = db.session.query(Teacher).filter(
    Teacher.goal.any(Goal.goal_cod == 'travel')).all()  # все репетиторы с целью, например travel
goal_all = db.session.query(Goal).filter(
    Goal.teacher.any(Teacher.teacher_id == 1)).all()  # все цели у одного репетитора
"""


class UserForm(FlaskForm):
    """
    name: поле формы для ввода имени
    tel: поле для ввода телефона
    goal: поле для отражения цели обучения
    time_hour: поле для отражения времени занятия
    submit: кнопка отправки текста на обработку
    """
    client = StringField('Имя пользователя', validators=[Length(min=0, max=100), InputRequired()])
    tel = StringField('Телефон пользователя', validators=[Length(min=0, max=15), InputRequired()])
    goal = RadioField('Какая цель занятий?',
                      choices=[('travel', 'Для путешествий'), ('study', 'Для учебы'), ('work', 'Для работы'),
                               ('relocate', 'Для переезда')], default='travel', validators=[DataRequired()])
    time_hour = RadioField('Учиться в неделю',
                           choices=[('1', '1-2 часа'), ('2', '3-5 часов'), ('3', '5-7 часов'), ('4', '7-10 часов')],
                           default='2', validators=[DataRequired()])
    submit = SubmitField('Запись данных')



timers_all = db.session.query(TimeForLearn).first()
timers = timers_all.time_all

goals = {}
goals_all = db.session.query(Goal).all()
for elem in goals_all:
    goals[elem.goal_cod] = elem.goal_name


def teacher_info(uid):
    """
    Функция поиска данных по 1 репетитору
    :param uid: id репетитора в БД
    :return: list со словарем данных по 1 репетитору
    """
    rec = db.session.query(Teacher).get(uid)
    goal_all = db.session.query(Goal).filter(Goal.teacher.any(Teacher.teacher_id == uid)).all()
    tmp_list = [elem.goal_cod for elem in goal_all]
    teacher_info = []
    tmp_dict = {'id': rec.teacher_id, 'name': rec.teacher_name, 'rating': rec.rating, 'price': rec.price,
                'picture': rec.picture, 'about': rec.about, 'free': rec.schedule, 'goals': tmp_list}
    teacher_info.append(tmp_dict)
    return teacher_info


def all_teachers_info():
    """
    Фунция формирования всего списка данных о репетиторах
    :return: list со словарями данных по репетиторам
    """
    teachers = []
    teachers_all = db.session.query(Teacher).all()
    for elem in teachers_all:
        tmp = {}
        tmp['id'] = elem.teacher_id
        tmp['name'] = elem.teacher_name
        tmp['rating'] = elem.rating
        tmp['price'] = elem.price
        tmp['picture'] = elem.picture
        tmp['about'] = elem.about
        tmp['free'] = elem.schedule
        goal_all = db.session.query(Goal).filter(Goal.teacher.any(Teacher.teacher_id == elem.teacher_id)).all()
        tmp['goals'] = [elem.goal_cod for elem in goal_all]
        teachers.append(tmp)
    return teachers


@app.route('/')
def render_main():
    """
    Представление главной страницы
    :return: 'Здесь будет Главная страница'
    """
    teachers = all_teachers_info()
    list_teachers = random.sample(teachers, k=6)
    return render_template('index.html', list_goals=goals, list_teachers=list_teachers)


@app.route('/goals/<goal_id>/')
def render_goals(goal_id):
    """
    Представление страницы с репетиторами по целям изучения языка
    :return: 'Здесь будет список репетиторов с учетом целей'
    """
    one_goal = {key: val for key, val in goals.items() if key == goal_id}
    short_list_teachers = []
    teach_records = db.session.query(Teacher).filter(Teacher.goal.any(Goal.goal_cod == goal_id)).all()
    for rec in teach_records:  # формируем list со словарем данных по репетиторам, у которых есть нужная цель
        goal_all = db.session.query(Goal).filter(Goal.teacher.any(Teacher.teacher_id == rec.teacher_id)).all()
        tmp_list = [elem.goal_cod for elem in goal_all]
        tmp_dict = {'id': rec.teacher_id, 'name': rec.teacher_name, 'rating': rec.rating, 'price': rec.price,
                    'picture': rec.picture, 'about': rec.about, 'free': rec.schedule, 'goals': tmp_list}
        short_list_teachers.append(tmp_dict)
    return render_template('goal.html', list_goals=one_goal, list_teachers=short_list_teachers)


@app.route('/profiles/<int:teacher_id>/')
def render_teachers(teacher_id):
    """
    Представление страницы с профилем репетитора
    :return: 'Здесь будет профиль репетитора'
    """
    rec = db.session.query(Teacher).get_or_404(teacher_id)  # находим запись о репетиторе в БД или ошибка 404
    goal_all = db.session.query(Goal).filter(Goal.teacher.any(Teacher.teacher_id == teacher_id)).all()
    tmp_list = [elem.goal_cod for elem in goal_all]
    one_teacher = teacher_info(teacher_id)
    short_list_goals = {key: goal for key, goal in goals.items() if key in one_teacher[0]['goals']}
    list_free = []  # ищем свободные часы репетитора
    Mon = [hour for hour, val in one_teacher[0]['free']['mon'].items() if val == True]
    list_free.append({'Понедельник': Mon})
    Tue = [hour for hour, val in one_teacher[0]['free']['tue'].items() if val == True]
    list_free.append({'Вторник': Tue})
    Wed = [hour for hour, val in one_teacher[0]['free']['wed'].items() if val == True]
    list_free.append({'Среда': Wed})
    Thu = [hour for hour, val in one_teacher[0]['free']['thu'].items() if val == True]
    list_free.append({'Четверг': Thu})
    Fri = [hour for hour, val in one_teacher[0]['free']['fri'].items() if val == True]
    list_free.append({'Пятница': Fri})
    Sat = [hour for hour, val in one_teacher[0]['free']['sat'].items() if val == True]
    list_free.append({'Суббота': Sat})
    Sun = [hour for hour, val in one_teacher[0]['free']['sun'].items() if val == True]
    list_free.append({'Воскресенье': Sun})
    return render_template('profile.html', list_goals=short_list_goals, list_teachers=one_teacher, schedule=list_free)


@app.route('/booking/<int:teacher_id>/<day>/<hour>/', methods=['GET', 'POST'])
def render_booking_done(teacher_id, day, hour):
    """
    Представление страницы с оформлением бронирования урока репетитора и подтверждением принятия брони
    :return: 'Здесь будет приема и подтверждение брони'
    """
    form = UserForm()
    one_teacher = teacher_info(teacher_id)
    if request.method == "POST":
        fio = form.client.data
        phone = form.tel.data
        teach = db.session.query(Teacher).get(teacher_id)
        one_booking = Booking(week_day=day, lesson_time=hour, client_name=fio, client_phone=phone,
                              booking_ditails=day + ' ' + hour + ' ' + fio + ' ' + phone)
        db.session.add(one_booking)
        one_booking.teacher_name.append(teach)
        db.session.commit()

        return render_template('booking_done.html', list_teachers=one_teacher, day=day, hour=hour, client=fio,
                               tel=phone, form=form)
    else:
        return render_template('booking.html', list_teachers=one_teacher, day=day, hour=hour, form=form)


@app.route('/request/', methods=['GET', 'POST'])
def render_request_done():
    """
    Представление страницы с подтверждением принятия заявки на подбор репетитора
    :return: 'Здесь будет подтверждение принятия заявки на подбор репетитора'
    """
    teachers = all_teachers_info()
    form = UserForm()
    if request.method == "POST":
        fio = form.client.data
        phone = form.tel.data
        goal = form.goal.data
        cl_goal = goals.get(goal)[2:]
        timer = form.time_hour.data
        cl_timer = timers.get(timer)
        one_req = RequestForm(goal_name=cl_goal, learning_time=cl_timer, client_name=fio, client_phone=phone)
        db.session.add(one_req)
        db.session.commit()

        return render_template('request_done.html', list_teachers=teachers, client=fio, tel=phone, goal=cl_goal,
                               timer=cl_timer, form=form)
    else:
        return render_template('request.html', list_goals=goals, form=form)


@app.route('/about/')
def render_about():
    """
    Представление страницы "О сервисе"
    :return: Описание сервиса
    """
    return render_template('about.html')


if __name__ == '__main__':
    if NEED_IMPORT:  # для первичного импорта имеющихся данных из файлов
        with open('goals.txt', 'r') as f:
            goals = json.load(f)
        for k, v in goals.items():
            print(k, v, type(k), type(v))
            goal = Goal(goal_name=v, goal_cod=k)
            db.session.add(goal)
        db.session.commit()

        timers = {'1': '1-2 часа', '2': '3-5 часов', '3': '5-7 часов', '4': '7-10 часов'}
        timelearn = TimeForLearn(time_all=timers)
        db.session.add(timelearn)
        db.session.commit()

        with open('teachers.txt', 'r') as f:
            teachers = json.load(f)
        for teach in teachers:
            pass
            teacher = Teacher(teacher_name=teach['name'], rating=teach['rating'], price=teach['price'],
                              picture=teach['picture'], schedule=teach['free'], about=teach['about'])
            db.session.add(teacher)
            for elem in teach['goals']:
                goal_one = db.session.query(Goal).filter(Goal.goal_cod == elem).first()
                teacher.goal.append(goal_one)  # отношение teacher - goal as many-to-many

        db.session.commit()

    # app.run('127.0.0.1', 7788, debug=True)
    app.run()  # for gunicorn server
# toolbar = DebugToolbarExtension(app)
