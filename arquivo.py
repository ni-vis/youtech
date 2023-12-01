from flask import Flask, render_template, request,redirect, session
import sqlite3 as sql
import uuid
import os

app = Flask(__name__)
app.secret_key = "youtech"

# Nome e senha para entrar no site como administrador
usuario = "..."
senha = "..."
# Caso um dos dois ou ambos estiverem errado não entrará, por isso o false
login = False

# Verificar a sessão do arquivo (login)
def verifica_sessao():
    if "login" in session and session['login']:
        return True
    else :
        return False

# Verificar o database, ou seja os dados conectados ao arquivo sql
def conecta_database():
    conexao = sql.connect("db_tech.db")
    conexao.row_factory = sql.Row
    return conexao

# Iniciar o arquivo sql
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

# rota para a página home
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    # Quando clicar em um produto ele será identificado pelo id 
    vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vaga DESC').fetchall()
    conexao.close()
    # Onde na parte {{title}} do modelo, será trocada pelo nome Home, para mostrar que está na página home
    title = "Home"
    return render_template("home.html", vagas=vagas,title=title)

# Rota de Login
@app.route("/login")
def login():
    # Onde na parte {{title}} do modelo, será trocada pelo nome Login, para mostrar que está na página login
    title="Login"
    return render_template("login.html", title=title)

#Rota para a página de acesso
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')

    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

# Rota do ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vaga DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", vagas=vagas, title=title)
    else:
        return redirect("/login")

# Rota de logout
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

# Rota da página de cadastro
@app.route("/cadvaga")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de cargos"
        return render_template("cadvaga.html", title=title)
    else:
        return redirect("/login")

# Rota da página de cadastro no banco
@app.route("/cadastro",methods=["post"])
def cadastro():
    if verifica_sessao():
        cargo_vaga=request.form['cargo_vaga']
        tipo_vaga=request.form['tipo_vaga']
        local_vaga=request.form['local_vaga']
        requisitos_vaga=request.form['requisitos_vaga']
        email_vaga=request.form['email_vaga']
        salario_vaga=request.form['salario_vaga']
        desc_vaga = request.form['desc_vaga']
        img_vaga=request.files['img_vaga']
        id_vaga=str(uuid.uuid4().hex)
        filename=id_vaga+cargo_vaga +'.png'
        img_vaga.save("static/img/imagens/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO vagas (tipo_vaga, cargo_vaga, requisitos_vaga, salario_vaga, local_vaga,email_vaga, desc_vaga, img_vaga) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (tipo_vaga, cargo_vaga, requisitos_vaga, salario_vaga, local_vaga,email_vaga, desc_vaga, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:
        return redirect("/login")


# Excluir produtos 
@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM vagas WHERE id_vaga = ?', (id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")

# Editar produtos
@app.route('/editvaga/<id_vaga>')
def editar(id_vaga):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?', (id_vaga,)).fetchall()
        conexao.close()
        title = 'Edição de cargos'
        return render_template('editvaga.html', vagas=vagas, title=title)
    else:
        return redirect('/login')
    
# ROTA PARA TRATAR DA EDIÇÃO ↧
@app.route('/editarvagas', methods=['POST'])
def editvaga():
    id_vaga = request.form['id_vaga']
    cargo_vaga = request.form['cargo_vaga']
    tipo_vaga = request.form['tipo_vaga']
    requisitos_vaga = request.form['requisitos_vaga']
    desc_vaga = request.form['desc_vaga']
    local_vaga = request.form['local_vaga']
    email_vaga = request.form['email_vaga']
    salario_vaga = request.form['salario_vaga']
    img_vaga = request.files['img_vaga']
    conexao = conecta_database()
    if img_vaga:
        vaga = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?', (id_vaga)).fetchall()
        filename = vaga[0]['img_vaga']
        img_vaga.save("static/img/imagens" + filename)
        conexao.execute('UPDATE vagas SET tipo_vaga = ?, cargo_vaga = ?, requisitos_vaga = ?, salario_vaga = ?, local_vaga = ?, email_vaga = ?, desc_vaga = ?, img_vaga = ? WHERE id_vaga = ?', (tipo_vaga, cargo_vaga,requisitos_vaga, salario_vaga, local_vaga, email_vaga, desc_vaga, filename, id_vaga))
    else:
        conexao.execute('UPDATE vagas SET tipo_vaga = ?, cargo_vaga = ?, requisitos_vaga = ?, salario_vaga = ?, local_vaga = ?, email_vaga = ?, desc_vaga = ? WHERE id_vaga = ?', (tipo_vaga, cargo_vaga, requisitos_vaga, salario_vaga, local_vaga, email_vaga, desc_vaga, id_vaga))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

@app.route("/sobre")
def sobre():
    iniciar_db()
    conexao = conecta_database()
    # Verifica se há um parâmetro vaga_id na solicitação
    vaga_id = request.args.get('vaga_id')
    # Se vaga_id estiver presente, exibe os detalhes específicos da vaga
    vaga = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?', (vaga_id,)).fetchone()
    conexao.close()
    # Verifica se a consulta encontrou uma vaga antes de acessar seus atributos
    if vaga is not None:
        title = vaga['cargo_vaga']  # Ou algum outro campo relevante para o título
        return render_template("sobre.html", vaga=vaga, title=title)
    else:
        # Trate o caso em que não foi encontrada nenhuma vaga com o id_vaga fornecido
        return render_template("home.html")



@app.route("/sobrevaga", methods=['POST'])
def sobrevaga():
    if verifica_sessao():
        curriculo_vaga = request.files['curriculo_vaga']
        id_vaga = str(uuid.uuid4().hex)
        filename = id_vaga + '.pdf'
        curriculo_vaga.save("static/img/curriculo/" + filename)
        return redirect("/")
    else:
        return redirect("/sobre")



# Rota da página para quando não há páginas
@app.route("/construcao")
def construcao():
    title="Construção"
    return render_template("construcao.html", title=title)

# Rota da página sobre a empresa
@app.route("/empresa")
def empresa():
    title="Sobre a empresa"
    return render_template("empresa.html", title=title)


# Rota de busca
@app.route("/busca",methods=["post"])
def busca():
    busca=request.form['buscar']
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE cargo_vaga LIKE "%" || ? || "%"',(busca,)).fetchall()
    title = "Home"
    return render_template("home.html", vagas=vagas, title = title)

# Para finalizar a rota 
app.run(debug=True, host='0.0.0.0')
