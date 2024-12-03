from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
from admin import init_admin
from flask_bootstrap import Bootstrap

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gossips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

logger.info("Inicializando aplicação Tarot Gossip")

class Gossip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reports = db.Column(db.Integer, default=0)
    is_blocked = db.Column(db.Boolean, default=False)
    last_moderated_at = db.Column(db.DateTime)
    moderation_reason = db.Column(db.String(200))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gossip_id = db.Column(db.Integer, db.ForeignKey('gossip.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_blocked = db.Column(db.Boolean, default=False)
    reports = db.Column(db.Integer, default=0)

    # Relacionamento com a fofoca
    gossip = db.relationship('Gossip', backref=db.backref('comments', lazy='dynamic', order_by='Comment.created_at'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/gossips', methods=['POST'])
def post_gossip():
    data = request.get_json()
    
    company = data.get('company', '').strip()
    content = data.get('content', '').strip()
    category = data.get('category', '').strip()
    
    if not company or not content:
        return jsonify({'error': 'Empresa e conteúdo são obrigatórios'}), 400
    
    gossip = Gossip(
        company=company,
        content=content,
        category=category
    )
    
    db.session.add(gossip)
    db.session.commit()
    
    return jsonify({'message': 'Fofoca postada com sucesso'}), 201

@app.route('/gossips')
def get_gossips():
    try:
        page = int(request.args.get('page', 1))
        company = request.args.get('company', '').strip()
        category = request.args.get('category', '').strip()
        sort = request.args.get('sort', 'newest')

        per_page = 10
        query = Gossip.query.filter_by(is_blocked=False)

        # Aplicar filtros
        if company:
            query = query.filter(Gossip.company.ilike(f'%{company}%'))
        if category:
            query = query.filter_by(category=category)

        # Aplicar ordenação
        if sort == 'oldest':
            query = query.order_by(Gossip.created_at.asc())
        elif sort == 'reports':
            query = query.order_by(Gossip.reports.desc(), Gossip.created_at.desc())
        else:  # newest
            query = query.order_by(Gossip.created_at.desc())

        # Paginação
        total = query.count()
        gossips = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Converter para dicionário
        gossips_list = []
        for gossip in gossips:
            gossip_dict = {
                'id': gossip.id,
                'company': gossip.company,
                'content': gossip.content,
                'category': gossip.category,
                'created_at': gossip.created_at.isoformat(),
                'reports': gossip.reports,
                'comments_count': gossip.comments.count()
            }
            gossips_list.append(gossip_dict)

        return jsonify({
            'gossips': gossips_list,
            'has_more': total > page * per_page
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar fofocas: {e}", exc_info=True)
        return jsonify({'error': 'Erro ao buscar fofocas'}), 500

@app.route('/api/gossips/<int:gossip_id>/report', methods=['POST'])
def report_gossip(gossip_id):
    gossip = Gossip.query.get_or_404(gossip_id)
    
    # Incrementa o número de denúncias
    gossip.reports = (gossip.reports or 0) + 1
    
    # Se atingir um limite de denúncias, bloqueia automaticamente
    if gossip.reports >= 5:
        gossip.is_blocked = True
        gossip.moderation_reason = 'Múltiplas denúncias'
        gossip.last_moderated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Fofoca denunciada com sucesso' if not gossip.is_blocked else 'Fofoca bloqueada por múltiplas denúncias',
        'reports': gossip.reports,
        'is_blocked': gossip.is_blocked,
        'moderation_reason': gossip.moderation_reason
    }), 200

@app.route('/api/gossips/<int:gossip_id>/comments', methods=['POST'])
def add_comment(gossip_id):
    gossip = Gossip.query.get_or_404(gossip_id)
    
    # Se a fofoca estiver bloqueada, não permite comentários
    if gossip.is_blocked:
        return jsonify({'error': 'Não é possível comentar em uma fofoca bloqueada'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Conteúdo do comentário não pode estar vazio'}), 400
    
    comment = Comment(
        gossip_id=gossip_id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat()
    }), 201

@app.route('/api/gossips/<int:gossip_id>/comments', methods=['GET'])
def get_comments(gossip_id):
    gossip = Gossip.query.get_or_404(gossip_id)
    
    comments = Comment.query.filter_by(gossip_id=gossip_id, is_blocked=False) \
        .order_by(Comment.created_at.desc()) \
        .all()
    
    comments_list = [{
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'reports': comment.reports
    } for comment in comments]
    
    return jsonify(comments_list), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Inicializar admin com logs
    try:
        logger.info("Inicializando admin")
        init_admin(app, Gossip, Comment, db)
        logger.info("Admin inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}", exc_info=True)
    
    app.run(debug=True, port=5001)
