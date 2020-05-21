import os, json, random
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import Length, DataRequired, InputRequired

# from flask_debugtoolbar import DebugToolbarExtension
# import data

SECRET_KEY = os.urandom(32)
timers = {'1': '1-2 часа', '2': '3-5 часов', '3': '5-7 часов', '4': '7-10 часов'}
with open('goals.txt', 'r') as f:
    goals = json.load(f)
with open('teachers.txt', 'r') as f:
    teachers = json.load(f)

app = Flask(__name__)
app.secret_key = SECRET_KEY


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


@app.route('/')
def render_main():
    """
    Представление главной страницы
    :return: 'Здесь будет Главная страница'
    """
    list_teachers = random.sample(teachers, k=6)
    return render_template('index.html', list_goals=goals, list_teachers=list_teachers)


@app.route('/goals/<goal_id>/')
def render_goals(goal_id):
    """
    Представление страницы с репетиторами по направлениями
    :return: 'Здесь будет список репетиторов с учетом направлений'
    """
    one_goal = {key: val for key, val in goals.items() if key == goal_id}
    short_list_teachers = [teacher for teacher in teachers if goal_id in teacher['goals']]
    return render_template('goal.html', list_goals=one_goal, list_teachers=short_list_teachers)


@app.route('/profiles/<int:teacher_id>/')
def render_teachers(teacher_id):
    """
    Представление страницы с профилем репетитора
    :return: 'Здесь будет профиль репетитора'
    """
    one_teacher = [teacher for teacher in teachers if teacher['id'] == teacher_id]
    short_list_goals = {key: goal for key, goal in goals.items() if key in one_teacher[0]['goals']}
    list_free = []
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


@app.route('/booking/<int:teacher_id>/<day>/<hour>/')
def render_booking(teacher_id, day, hour):
    """
    Представление страницы с оформлением бронирования урока репетитора
    :return: 'Здесь будет форма бронирования урока репетитора'
    """
    form = UserForm()
    one_teacher = [teacher for teacher in teachers if teacher['id'] == teacher_id]
    return render_template('booking.html', list_teachers=one_teacher, day=day, hour=hour, form=form)


@app.route('/booking_done/<int:teacher_id>/<day>/<hour>/', methods=['POST'])
def render_booking_done(teacher_id, day, hour):
    """
    Представление страницы с подтверждением принятия брони
    :return: 'Здесь будет подтверждение брони'
    """
    form = UserForm()
    if request.method == "POST":
        fio = form.client.data
        phone = form.tel.data
        one_teacher = [teacher for teacher in teachers if teacher['id'] == teacher_id]
        result = {'teacher': teacher_id, 'dayofweek': day, 'hour': hour, 'client': fio, 'phone': phone}
        tmp_file = []
        if os.path.exists('booking.json'):
            with open('booking.json', 'r') as f:
                tmp_file = json.load(f)
        tmp_file.append(result)
        with open('booking.json', 'w') as f:
            json.dump(tmp_file, f)

        return render_template('booking_done.html', list_teachers=one_teacher, day=day, hour=hour, client=fio,
                               tel=phone,
                               form=form)
    else:
        return render_template('booking.html')


@app.route('/request/')
def render_request():
    """
    Представление страницы для оформления заявки на репетитора
    :return: 'Здесь будет форма заявки на репетитора'
    """
    form = UserForm()
    return render_template('request.html', list_goals=goals, form=form)


@app.route('/request_done/', methods=['POST'])
def render_request_done():
    """
    Представление страницы с подтверждением принятия заявки на подбор репетитора
    :return: 'Здесь будет подтверждение принятия заявки на подбор репетитора'
    """
    form = UserForm()
    if request.method == "POST":
        fio = form.client.data
        phone = form.tel.data
        goal = form.goal.data
        cl_goal = goals.get(goal)[2:]
        timer = form.time_hour.data
        cl_timer = timers.get(timer)
        result = {'goal': goals.get(goal), 'time': cl_timer, 'client': fio, 'phone': phone}
        tmp_file = []
        if os.path.exists('request.json'):
            with open('request.json', 'r') as f:
                tmp_file = json.load(f)
        tmp_file.append(result)
        with open('request.json', 'w') as f:
            json.dump(tmp_file, f)

        return render_template('request_done.html', list_teachers=teachers, client=fio, tel=phone, goal=cl_goal,
                               timer=cl_timer, form=form)
    else:
        return render_template('request.html')


@app.route('/about/')
def render_about():
    """
    Представление страницы "О сервисе"
    :return: Описание сервиса
    """
    return render_template('about.html')


if __name__ == '__main__':
    # with open('goals.txt', 'w') as f:
    #     json.dump(data.goals, f)
    # with open('teachers.txt', 'w') as f:
    #     json.dump(data.teachers, f)

    # with open('goals.txt', 'r') as f:
    #     goals = json.load(f)
    # with open('teachers.txt', 'r') as f:
    #     teachers = json.load(f)

    # app.run('127.0.0.1', 7788, debug=True)
    app.run()  # for gunicorn server

#    toolbar = DebugToolbarExtension(app)
