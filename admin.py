from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, request, flash, render_template

class AdminUser(UserMixin):
    def __init__(self):
        self.id = 1
        self.username = 'admin'
        self.password_hash = generate_password_hash('admin123')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

admin_user = AdminUser()
login_manager = LoginManager()

def init_login(app):
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    @login_manager.user_loader
    def load_user(user_id):
        return admin_user if str(user_id) == '1' else None

class AdminModelView(ModelView):
    column_list = ['id', 'company', 'content', 'category', 'created_at', 'reports', 'is_blocked', 'last_moderated_at', 'moderation_reason']
    column_searchable_list = ['company', 'content', 'category']
    column_filters = ['company', 'category', 'is_blocked', 'reports', 'created_at', 'last_moderated_at']
    column_sortable_list = ['id', 'company', 'created_at', 'reports', 'last_moderated_at']
    can_edit = True
    can_delete = True
    can_create = True
    can_view_details = True
    column_default_sort = ('created_at', True)  # Ordenar por data de criação, mais recente primeiro
    
    def is_accessible(self):
        return current_user.is_authenticated

class CommentModelView(ModelView):
    column_list = ['id', 'gossip_id', 'content', 'created_at', 'is_blocked', 'reports']
    column_searchable_list = ['content']
    column_filters = ['is_blocked', 'reports', 'created_at', 'gossip_id']
    column_sortable_list = ['id', 'gossip_id', 'created_at', 'reports']
    can_edit = True
    can_delete = True
    can_create = True
    can_view_details = True
    column_default_sort = ('created_at', True)  # Ordenar por data de criação, mais recente primeiro
    
    def is_accessible(self):
        return current_user.is_authenticated

class AdminHomeView(AdminIndexView):
    def __init__(self, gossip_model=None, comment_model=None, db=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gossip_model = gossip_model
        self.comment_model = comment_model
        self.db = db

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin.login'))
        
        stats = {
            'gossips': {
                'total': self.gossip_model.query.count(),
                'blocked': self.gossip_model.query.filter_by(is_blocked=True).count()
            },
            'comments': {
                'total': self.comment_model.query.count(),
                'blocked': self.comment_model.query.filter_by(is_blocked=True).count()
            }
        }
        
        return self.render('admin/dashboard.html', stats=stats)

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for('.index'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if (username == admin_user.username and 
                admin_user.check_password(password)):
                login_user(admin_user)
                return redirect(url_for('.index'))
            
            flash('Usuário ou senha inválidos', 'error')

        return render_template('admin/login.html')

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect(url_for('.login'))

def init_admin(app, gossip_model, comment_model, db):
    init_login(app)
    
    admin = Admin(
        app, 
        name='Tarot Admin', 
        template_mode='bootstrap3', 
        index_view=AdminHomeView(
            gossip_model=gossip_model, 
            comment_model=comment_model, 
            db=db,
            name='Home'
        )
    )
    admin.add_view(AdminModelView(gossip_model, db.session, name='Fofocas'))
    admin.add_view(CommentModelView(comment_model, db.session, name='Comentários'))
