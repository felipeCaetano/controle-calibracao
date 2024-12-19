# app.py
from flask import flash, Flask, jsonify, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
import os

# Configuração do banco de dados
def init_db():
    conn = sqlite3.connect('calibration.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS equipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment TEXT NOT NULL,
            location TEXT NOT NULL,
            code TEXT,
            model TEXT,
            place TEXT,
            calibration_date DATE,
            expiry_date DATE
        )
    ''')
    
    # Inserir dados iniciais se a tabela estiver vazia
    c.execute('SELECT COUNT(*) FROM equipments')
    if c.fetchone()[0] == 0:
        initial_data = [
            ('Termovisor', 'JRM', '156549', 'FLIR', 'Sala Comando JRM', '2023-06-22', '2024-06-17'),
            ('Termohigrômetro', 'JRM', 'MT-241', 'Minipa', 'Sala comando', '2023-12-22', '2024-12-22'),
            ('Termômetro', 'JRM', 'JRM01', 'Minipa', 'Cabana 230kV', '2023-12-21', '2024-12-21'),
            ('Termômetro', 'JRM', 'JRM02', 'Minipa', 'Cabana 69kV', '2023-12-21', '2024-12-21'),
            ('Termômetro', 'JRM', 'JRM04', 'Westner', 'Sala de baterias', '2022-09-09', '2023-09-09'),
            ('Densímetro digital', 'JRM', '80981947', 'Anton Paar', 'Sala comando', '2022-11-10', '2023-11-10'),
            ('Detector de tensão', 'JRM', '122025', 'RITZ', 'Sala comando', '2023-12-19', '2024-12-19'),
            ('Termovisor', 'BGI', '188997', 'FLIR', 'Sala Comando BGI', '2023-06-05', '2024-06-05')
        ]
        c.executemany('''
            INSERT INTO equipments (equipment, location, code, model, place, calibration_date, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', initial_data)
    
    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para flash messages
    
    # Inicializar o banco de dados
    with app.app_context():
        init_db()
    
    return app

app = create_app()

@app.route('/')
def index():
    location_filter = request.args.get('location', 'all')
    
    conn = sqlite3.connect('calibration.db')
    c = conn.cursor()
    
    if location_filter != 'all':
        c.execute('SELECT * FROM equipments WHERE location = ?', (location_filter,))
    else:
        c.execute('SELECT * FROM equipments')
    
    equipments = c.fetchall()
    conn.close()
    
    # Processar status de cada equipamento
    processed_equipments = []
    for eq in equipments:
        expiry_date = datetime.strptime(eq[7], '%Y-%m-%d')
        days_until_expiry = (expiry_date - datetime.now()).days
        
        if days_until_expiry < 0:
            status = 'expired'
            status_text = 'Vencido'
        elif days_until_expiry < 30:
            status = 'warning'
            status_text = 'Próximo ao vencimento'
        else:
            status = 'ok'
            status_text = 'Em dia'
            
        processed_equipments.append({
            'id': eq[0],
            'equipment': eq[1],
            'location': eq[2],
            'code': eq[3],
            'model': eq[4],
            'place': eq[5],
            'calibration_date': datetime.strptime(eq[6], '%Y-%m-%d').strftime('%d/%m/%Y'),
            'expiry_date': datetime.strptime(eq[7], '%Y-%m-%d').strftime('%d/%m/%Y'),
            'status': status,
            'status_text': status_text
        })
    
    return render_template('index.html', equipments=processed_equipments, current_filter=location_filter)

@app.route('/locations', methods=['GET'])
def get_locations():
    # Lista de locais (em um banco de dados real, você buscaria do banco)
    locations = [
        {'id': 'JRM', 'name': 'JRM'},
        {'id': 'BGI', 'name': 'BGI'},
    ]
    return jsonify(locations)

@app.route('/equipment_types', methods=['GET'])
def get_equipment_types():
    conn = sqlite3.connect('calibration.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM equipment_types ORDER BY name')
    types = [{'id': id, 'name': name} for id, name in c.fetchall()]
    conn.close()
    return jsonify(types)

@app.route('/equipment_models/<int:type_id>', methods=['GET'])
def get_equipment_models(type_id):
    conn = sqlite3.connect('calibration.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM equipment_models WHERE equipment_type_id = ? ORDER BY name', (type_id,))
    models = [{'id': id, 'name': name} for id, name in c.fetchall()]
    conn.close()
    return jsonify(models)

@app.route('/add_type', methods=['POST'])
def add_equipment_type():
    try:
        new_type = request.form['name'].strip()
        conn = sqlite3.connect('calibration.db')
        c = conn.cursor()
        c.execute('INSERT INTO equipment_types (name) VALUES (?)', (new_type,))
        type_id = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': type_id, 'name': new_type})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Tipo já existe'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add_model', methods=['POST'])
def add_equipment_model():
    try:
        new_model = request.form['name'].strip()
        type_id = request.form['type_id']
        conn = sqlite3.connect('calibration.db')
        c = conn.cursor()
        c.execute('INSERT INTO equipment_models (name, equipment_type_id) VALUES (?, ?)', 
                 (new_model, type_id))
        model_id = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': model_id, 'name': new_model})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Modelo já existe'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        try:
            # Converter datas do formato DD/MM/YYYY para YYYY-MM-DD
            calibration_date = datetime.strptime(request.form['calibration_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            expiry_date = datetime.strptime(request.form['expiry_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
            
            conn = sqlite3.connect('calibration.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO equipments (equipment, location, code, model, place, calibration_date, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['equipment'],
                request.form['location'],
                request.form['code'],
                request.form['model'],
                request.form['place'],
                calibration_date,
                expiry_date
            ))
            conn.commit()
            conn.close()
            
            flash('Equipamento adicionado com sucesso!', 'success')
            return redirect(url_for('add_equipment'))
        except Exception as e:
            flash(f'Erro ao adicionar equipamento: {str(e)}', 'error')
            return redirect(url_for('add_equipment'))
            
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)