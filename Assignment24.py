from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning
db = SQLAlchemy(app)

# Define Member model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    workout_sessions = db.relationship('WorkoutSession', backref='member', lazy=True)

# Define WorkoutSession model
class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer)  # Duration in minutes
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# CRUD operations for Members
@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member added successfully!'}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'email': m.email} for m in members])

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    member = Member.query.get(id)
    if not member:
        return jsonify({'message': 'Member not found!'}), 404
    member.name = data['name']
    member.email = data['email']
    db.session.commit()
    return jsonify({'message': 'Member updated successfully!'})

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'message': 'Member not found!'}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully!'})

# CRUD operations for Workout Sessions
@app.route('/workouts', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_session = WorkoutSession(date=data['date'], duration=data['duration'], member_id=data['member_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully!'}), 201

@app.route('/workouts', methods=['GET'])
def get_workouts():
    sessions = WorkoutSession.query.all()
    return jsonify([{'id': s.id, 'date': s.date, 'duration': s.duration, 'member_id': s.member_id} for s in sessions])

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    return jsonify([{'id': s.id, 'date': s.date, 'duration': s.duration} for s in sessions])

if __name__ == '__main__':
    app.run(debug=True)
