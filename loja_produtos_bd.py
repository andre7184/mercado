import sqlite3
from datetime import datetime, timedelta

senhaAdmin=142536 # senha administrador
tempo_finalizar_carrinho=5 # tempo em minutos para finalizar carrinho inativo
arquivo_banco_dados='database.db' # url do arquivo do banco de dados SQL

def connect_db():
    return sqlite3.connect(arquivo_banco_dados)

def create(conn, table, dic_value): # conn:variavel conexao banco,table:string nome da tabela, dic_value: Dicionario com colunas e valor para cadastrar na tabela
    columns = ', '.join(dic_value.keys())
    placeholders = ', '.join('?' * len(dic_value))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    cursor = conn.cursor()
    cursor.execute(sql, tuple(dic_value.values()))
    conn.commit()
    return cursor.lastrowid  # Retorna o ID do último registro inserido

def read(conn, table, dic_value=None): # conn:variavel conexao banco,table:string nome da tabela, dic_value: Dicionario com colunas e valor para buscar na tabela(pode ser None)
    if dic_value:
        conditions = ' AND '.join(f"{k} = ?" for k in dic_value.keys())
        sql = f'SELECT * FROM {table} WHERE {conditions}'
        cursor = conn.execute(sql, tuple(dic_value.values()))
    else:
        sql = f'SELECT * FROM {table}'
        cursor = conn.execute(sql)
    rows = cursor.fetchall()
    if rows:
        # Converta cada linha em um dicionário
        # Obtenha os nomes das colunas da descrição do cursor
        column_names = [column[0] for column in cursor.description]
        # Converta cada linha em um dicionário
        dict_rows = [{column: value for column, value in zip(column_names, row)} for row in rows]
        return dict_rows
    else:
        return []

def update(conn, table, dic_values, dic_update): # conn:variavel conexao banco,table:string nome da tabela, dic_value: Dicionario com nome de colunas e valores para buscar na tabela, dic_update: Dicionario com dados (nome coluna e valor) para atualizar a tabela
    set_values = ', '.join(f"{k} = ?" for k in dic_values.keys())
    conditions = ' AND '.join(f"{k} = ?" for k in dic_update.keys())
    sql = f'UPDATE {table} SET {set_values} WHERE {conditions}'
    conn.execute(sql, tuple(list(dic_values.values()) + list(dic_update.values())))
    conn.commit()

def delete(conn, table, dic_value): # conn:variavel conexao banco,table:string nome da tabela, dic_value: Dicionario com nome de colunas e valores para buscar na tabela
    conditions = ' AND '.join(f"{k} = ?" for k in dic_value.keys())
    sql = f'DELETE FROM {table} WHERE {conditions}'
    conn.execute(sql, tuple(dic_value.values()))
    conn.commit()

def verificaTempoCarrinho(conn,id_user): # faz a remoção do carrinho caso passe muito tempo sem finalizar a compra
    resultado = conn.execute("SELECT datetime('now')").fetchone() #pega a data e hora do banco, para não haver diferença de horario
    if resultado is not None:
        data_atual=datetime.strptime(resultado[0], '%Y-%m-%d %H:%M:%S')
        ten_minutes_ago = data_atual - timedelta(minutes=tempo_finalizar_carrinho)
        lista_carrinho=read(conn, 'carrinho', {'id_usuario': id_user,'finalizado':0})
        if len(lista_carrinho)==1:
            id_carrinho=lista_carrinho[0]['id']
            data_update=datetime.strptime(lista_carrinho[0]['data_update'], '%Y-%m-%d %H:%M:%S') # pega ultima data atualizada do carrinho
            if data_update < ten_minutes_ago: 
                delete(conn, 'itens_carrinho', {'id_carrinho': id_carrinho}) # caso nao foi feito nenhuma alteração no carrinho remove ele

def formataReal(valor): #formata os valores em real
    return 'R$ {:,.2f}'.format(float(valor)).replace('.', '#').replace(',', '.').replace('#', ',')

def cadastrarProduto(conn): #cadastra produtos
    print("---- Cadastrar Produto ----")
    nome=input("Digite o nome do produto: ")
    lista_produtos=read(conn, 'produtos', {'nome': nome})
    if len(lista_produtos)==0:
        qtd=input("qtd em estoque do produto: ")
        valor=round(float(input(f"Digite o valor do produto: ").replace(',', '.')),2)
        create(conn, 'produtos', {'nome': nome, 'qtd': qtd,'valor':valor})
        print("Produto cadastrado com sucesso!")
    else:
        print(f"O produto com nome '{nome}' já esta cadastrado!")

def alterarProduto(conn): #atualiza produtos
    print("---- Alterar Produto ----")
    id_produto=int(input("Digite o Id do produto: "))
    lista_produtos=read(conn, 'produtos', {'id': id_produto})
    if len(lista_produtos)==1:
        rp=input(f"Deseja alterar o nome do produto {lista_produtos[0]['nome']}:(s/n) ").lower()
        if rp=='s':
            novo_nome=input("Digite o novo nome do produto: ")
            update(conn, 'produtos', {'nome': novo_nome}, {'id': id_produto})
            print("Nome do produto alterado com sucesso!")
        else:
            novo_nome=lista_produtos[0]['nome']
        rp=input(f"Deseja alterar a qtd do produto {novo_nome} de {lista_produtos[0]['qtd']}:(s/n) ").lower()
        if rp=='s':
            nova_qtd=int(input(f"Digite a nova qtd do produto: "))
            update(conn, 'produtos', {'qtd': nova_qtd}, {'id': id_produto})
            print("qtd do produto alterado com sucesso!")
        rp=input(f"Deseja alterar o valor do produto {novo_nome} de {formataReal(lista_produtos[0]['valor'])}:(s/n) ").lower()
        if rp=='s':
            novo_valor=round(float(input(f"Digite o novo valor do produto: ").replace(',', '.')),2)
            update(conn, 'produtos', {'valor': novo_valor}, {'id': id_produto})
            print("Valor do produto alterado com sucesso!")
    else:
        print(f"o produto com id:{id_produto} nao existe!")

def removerProduto(conn): #remove produtos
    print("---- Remover Produto ----")
    id_produto=int(input("Digite o Id do produto: "))
    lista_produtos=read(conn, 'produtos', {'id': id_produto})
    if len(lista_produtos)==1:
        nome=lista_produtos[0]['nome']
        rp=input(f"Tem certeza que deseja remover o produto {nome} com id:{id_produto}:(s/n) ").lower()
        if rp=='s':
            lista_itens_carrinho=read(conn, 'itens_carrinho',{'id_produto':id_produto})
            if len(lista_itens_carrinho)==0:
                delete(conn, 'produtos', {'id': id_produto})
                print("Produto removido com sucesso")
            else:
                print("Produto não pode ser removido")
                qtd_produtos=lista_produtos[0]['qtd']
                if qtd_produtos>0:
                    rp=input(f"Deseja alterar a qtd do produto {nome} de '{qtd_produtos}' para 0 :(s/n) ").lower()
                    if rp=='s':
                        update(conn, 'produtos', {'qtd': 0}, {'id': id_produto}) 
    else:
        print(f"O produto  com id:{id_produto} nao existe!")

def listarProduto(conn): #lista produtos
    print("---- Listar Produtos ----")
    lista_produtos=read(conn, 'produtos')
    if len(lista_produtos)>0:
        for linha in lista_produtos:
            print(f"Id:{linha['id']} - {linha['nome']} - qtd: {linha['qtd']} - {formataReal(linha['valor'])}")
    else:
        print(f"Nenhum produto encontrado!")

def cadastrarUsuario(conn): # cadatra usuario
    print("---- CADASTRAR USUÁRIO ----")
    nome=input("Digite o nome: ")
    email=input("Digite o login (e-mail): ").lower()
    senha=int(input(f"Digite a senha ({email}): "))
    adm=False
    rp=input(f"Este: {email} é admin:(s/n) ").lower()
    if rp=='s':
        senha_admin=int(input(f"Digite a senha do Administrador: "))
        if senha_admin==senhaAdmin:
            adm=True
    id=create(conn, 'usuario', {'nome': nome, 'email': email,'senha':senha,'admin':adm})
    if id: # retorna em lista os dados do usuario e a autenticação se caso sucesso
        return [True,id,adm] 
    else:
        return [False,0,adm]

def listarUsuario(conn,id_usuario=None): # lista usuarios
    print("---- Listar Usuários ----")
    if id_usuario:
        lista_usuarios=read(conn, 'usuario',{'id': id_usuario})
    else:
        lista_usuarios=read(conn, 'usuario')
    if len(lista_usuarios)>0:
        for linha in lista_usuarios:
            if linha['admin']:
                admin='SIM'
            else:
                admin='NÃO'
            print(f"Id: {linha['id']} - Nome: {linha['nome']} - email: {linha['email']} - Admin: {admin}")
    else:
        print(f"Nenhum usuário encontrado!")

def adicionarAoCarrinho(conn,id_user): #adiciona produtos ao carrinho
    verificaTempoCarrinho(conn,id_user)
    print("---- Adicionar Produto ao Carrinho ----")
    id_produto=int(input("Digite o Id do produto: "))
    lista_produtos=read(conn, 'produtos', {'id': id_produto})
    if len(lista_produtos)==1:
        nome=lista_produtos[0]['nome']
        qtd=int(input(f"qtd de produto(s) {nome}: "))
        if qtd<=lista_produtos[0]['qtd']:
            valor_unitario=lista_produtos[0]['valor']
            valor_total=round(lista_produtos[0]['valor']*qtd,2)
            lista_carrinho=read(conn, 'carrinho', {'id_usuario': id_user,'finalizado':0})
            if len(lista_carrinho)==1:
                id_carrinho=lista_carrinho[0]['id']
                lista_itensCarrinho=read(conn, 'itens_carrinho', {'id_produto': id_produto,'id_carrinho':id_carrinho})
                if len(lista_itensCarrinho)==1:
                    produto=False
                else:
                    produto=True  
            else:
                id_carrinho=create(conn, 'carrinho', {'id_usuario': id_user, 'preco': 0,'qtd': 0,'data': None,'data_update': None,'finalizado':False})
                produto=True
            if produto:
                id_itensCarrinho=create(conn, 'itens_carrinho', {'id_carrinho': id_carrinho, 'id_produto': id_produto,'qtd':qtd,'valor_unitario':valor_unitario,'valor_total':valor_total})
                print(f"Produto adicionado com sucesso ao carrinho ({id_itensCarrinho})!")  
            else:
                print("este produto ja está no carrinho")    
        else:
            print(f"Qtd de produtos com id:{id_produto} nao existe no estoque!")
    else:
        print(f"o produto com id:{id_produto} nao existe!")

def removerDoCarrinho(conn,id_user):  #remove produtos do carrinho
    print("---- Remover Produto do Carrinho ----")
    lista_carrinho=visualizarCarrinho(conn,id_user,True)
    if len(lista_carrinho)!=0:
        itens=lista_carrinho['itens']
        for i in itens:
            print(f"Id:{itens[i]['id']} - {itens[i]['produto']} - qtd: {itens[i]['qtd']} - {formataReal(itens[i]['valor_unitario'])} - {formataReal(itens[i]['valor_total'])}")

        id_item=int(input("Id do item a remover: "))
        if id_item in itens:
            rp=input(f"Tem certeza que deseja remover o produto {lista_carrinho['itens'][id_item]['produto']} do carrinho:(s/n) ").lower()
            if rp=='s':
                delete(conn, 'itens_carrinho', {'id': id_item})
                print("Carrinho alterado com sucesso!")
        else:
            print(f"O id Digitado é inválido!")
    else:
        print(f"Carrinho vazio!")

def visualizarCarrinho(conn,id_user,retornar=False): # visualiza carrinho, para retornar dados para outra função ou imprimir direto
    verificaTempoCarrinho(conn,id_user)
    if retornar:
        carrinho={}
    else:
        print("---- Visualizar Carrinho ----")
    lista_carrinho=read(conn, 'carrinho', {'id_usuario': id_user,'finalizado':0})
    if len(lista_carrinho)==1:
        id_carrinho=lista_carrinho[0]['id']
        preco=lista_carrinho[0]['preco']
        qtd=lista_carrinho[0]['qtd']
        if retornar:
            carrinho['id_carrinho']=id_carrinho
            carrinho['preco']=preco
            carrinho['qtd_itens']=qtd
            itens={}
        else:
            print(f"Carrinho Id:{id_carrinho} - Valor Total: {formataReal(preco)} com {qtd} itens:")

        lista_itensCarrinho=read(conn, 'itens_carrinho',{'id_carrinho':id_carrinho})
        for linha in lista_itensCarrinho:
            lista_produtos=read(conn, 'produtos',{'id':linha['id_produto']})
            if len(lista_produtos)==1:
                nome_produto=lista_produtos[0]['nome']
            else:
                nome_produto=None
            if retornar:
                linha_itens={'id':linha['id'],'id_carrinho':linha['id_carrinho'],'id_produto':linha['id_produto'],'produto':nome_produto,'qtd':linha['qtd'],'valor_unitario':linha['valor_unitario'],'valor_total':linha['valor_total']}
                itens[linha['id']]=linha_itens
            else:
                print(f"Id:{linha['id']} - {nome_produto} - qtd: {linha['qtd']} - {formataReal(linha['valor_unitario'])} - {formataReal(linha['valor_total'])}")
        if retornar:
            carrinho['itens']=itens
            return carrinho
    else:
        if retornar:
            return carrinho
        else:
            print(f"Carrinho vazio!")

def finalizarCompra(conn,id_user): # finaliza a compra dos itens que esta no carrinho
    print("---- Finalizar Compra ----")
    lista_carrinho=visualizarCarrinho(conn,id_user,True)
    if len(lista_carrinho)!=0:
        print(f"Carrinho Id:{lista_carrinho['id_carrinho']} - Valor Total {formataReal(lista_carrinho['preco'])} com ({lista_carrinho['qtd_itens']} produtos:)")
        itens=lista_carrinho['itens']
        for i in itens:
            print(f" - Produto: {itens[i]['produto']} - qtd: {itens[i]['qtd']} - {formataReal(itens[i]['valor_unitario'])} - {formataReal(itens[i]['valor_total'])}")

        rp=input(f"Tem certeza que deseja finalizar a compra dos itens do carrinho:(s/n) ").lower()
        if rp=='s':
            dataTime = conn.execute("SELECT datetime('now')").fetchone()[0]
            update(conn, 'carrinho', {'finalizado': True,'data':dataTime}, {'id': lista_carrinho['id_carrinho']})
            print("Compra Finalizada com sucesso!")
        else:
            print(f"O id Digitado é inválido!")
    else:
        print(f"Carrinho vazio!")

def historicoTransacoes(conn,id_user=None): # mostra historico de transações, HISTORICO DE COMPRAS para o cliente normal e HISTORICO DE VENDAS para o usuario admin
    if id_user:
        print("---- Histórico de Compras ----")
        lista_transacoes=read(conn, 'transacoes', {'id_usuario': id_user})
    else:
        print("---- Histórico de Vendas ----")
        lista_transacoes=read(conn, 'transacoes')
    if lista_transacoes:
        print("__________________________________________________________________")
        for linha in lista_transacoes:
            print(f"Data: {linha['data_transacao']} - usuario:{linha['nome_usuario']} - Valor Total {formataReal(linha['valor_total_carrinho'])} - qtd itens: {linha['quantidade_total_carrinho']}")
            produtos=linha['produtos'].split(',')
            qtd_produtos=linha['qtd_produtos'].split(',')
            valor_produtos=linha['valor_unitario_produtos'].split(',')
            valor_total_produtos=linha['valor_total_produtos'].split(',')
            for i in range(linha['quantidade_total_carrinho']):
                print(f" * {produtos[i]} - qtd:{qtd_produtos[i]} - {formataReal(valor_produtos[i])} - {formataReal(valor_total_produtos[i])}")
            print("__________________________________________________________________")

    else:
        print(f"Não existem transações!")

def menuCadastro(): # menu de cadastro de usuario
    text="""
    ---- MENU LOJA - cadastro de usuários----
    Informe a operação desejada:
    1 PARA PARA CADASTRAR
    2 PARA PARA LISTAR USUÁRIO
    0 PARA SAIR
    """
    print(text)

def menuAdmin(): # menu do usuario admin
    text="""
    ---- MENU LOJA - admin----
    Informe a operação desejada:
    1 PARA LISTAR PRODUTOS
    2 PARA CADASTRAR PRODUTO
    3 PARA ALTERAR PRODUTO
    4 PARA REMOVER PRODUTO
    5 HISTORICO DE VENDAS
    6 PARA LISTAR USUARIOS
    0 PARA SAIR
    """
    print(text)

def menuCliente(login):  # menu do usuario cliente
    text=f"""
    ---- MENU LOJA user:{login}----
    1 PARA LISTA DE PRODUTOS
    2 PARA ADICIONAR AO CARRINHO
    3 PARA REMOVER DO CARRINHO
    4 PARA VISUALIZAR CARRINHO
    5 PARA FINALIZAR COMPRA
    6 HISTORICO DE COMPRAS
    7 PARA LISTAR USUARIO
    0 PARA SAIR
    """
    print(text)

new=False
auth=False
admin=False
while True:
    print("---- LOGIN LOJA ----")
    print("Entre com o login ou 'novo' para cadastrar")
    login=input("Entre com o email(login): ").lower()
    if login=='novo':
        new=True
    else:
        senha=int(input("Entre com a senha: "))
        conn = connect_db()
        lista_login=read(conn, 'usuario', {'email': login,'senha':senha})
        if len(lista_login)==1:
            id_usuario=lista_login[0]['id']
            if lista_login[0]['admin']:
                admin=True
            else:
                auth=True
        else:
            print("login ou senha inválido!")
            rp=input("Para tentar novamente digite (s): ").lower()
            if rp != 's':
                break
    while new:
        menuCadastro()
        entrada=int(input("ENTRE COM UMA OPÇÃO ACIMA: "))
        if entrada==1:
            conn = connect_db()
            lista=cadastrarUsuario(conn)
            if lista[2]:
                admin=lista[0]
            else:
                auth=lista[0]
            id_usuario=lista[1]
        elif entrada==2:
            print("---- LISTA DE USUÁRIOS ----")
            conn = connect_db()
            listarUsuario(conn,id_usuario)
        elif entrada==0:
            new=False
            auth=False
            admin=False
        else:
            print('entrada inválida!')
    while admin:
        menuAdmin()
        entrada=int(input("ENTRE COM UMA OPÇÃO ACIMA: "))
        if entrada==1:
            conn = connect_db()
            listarProduto(conn)
        elif entrada==2:
            conn = connect_db()
            cadastrarProduto(conn)
        elif entrada==3:
            conn = connect_db()
            alterarProduto(conn)
        elif entrada==4:
            conn = connect_db()
            removerProduto(conn)
        elif entrada==5:
            conn = connect_db()
            historicoTransacoes(conn)
        elif entrada==6:
            conn = connect_db()
            listarUsuario(conn)
        elif entrada==0:
            admin=False
        else:
            print('entrada inválida!')
    while auth:
        menuCliente(login)
        entrada=int(input("ENTRE COM UMA OPÇÃO ACIMA: "))
        if entrada==1:
            conn = connect_db()
            listarProduto(conn)
        elif entrada==2:
            conn = connect_db()
            adicionarAoCarrinho(conn,id_usuario)
        elif entrada==3:
            conn = connect_db()
            removerDoCarrinho(conn,id_usuario)
        elif entrada==4:
            conn = connect_db()
            visualizarCarrinho(conn,id_usuario)
        elif entrada==5:
            conn = connect_db()
            finalizarCompra(conn,id_usuario)
        elif entrada==6:
             conn = connect_db()
             historicoTransacoes(conn,id_usuario)
        elif entrada==7:
             conn = connect_db()
             listarUsuario(conn,id_usuario)
        elif entrada==0:
            auth=False
        else:
            print("opção inválida, tente novamente!")