from banco_lanca import *
import subprocess
import cv2
import gi
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import numpy as np
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))

aux = 0
global aux2
aux2= 0
class Handler():

	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file(os.getcwd()+'/interface_model/n_interface.glade')
		self.builder.connect_signals(self)

		#List Store | combobox
		self.liststore = Gtk.ListStore(int,str)
		self.liststore_regiao = Gtk.ListStore(int,str)
		self.liststore_pais = Gtk.ListStore(int,str) 
		self.liststore_codigo = Gtk.ListStore(int,str)
		self.liststore_carro = Gtk.ListStore(int,str)
		self.liststore_site = Gtk.ListStore(int,str)
		self.liststore_tipo = Gtk.ListStore(int,str)
		
		# Stack
		self.stack = self.builder.get_object('stack')
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

		#Carrega imagens
		for i in range(1,7):
			self.logo(f'im_lumar{str(i)}', f'im_visiontech{str(i)}')

		for i in range(1,3):
			self.img_cad = self.builder.get_object(f'img_cad{str(i)}')
			self.img_cad.set_from_file("./db_images/cad"+".png")

		for i in range(1,4):
			self.img_c4d = self.builder.get_object(f'img_c4d{str(i)}')
			self.img_c4d.set_from_file("./db_images/c4d"+".png")
		
		self.av_img = self.builder.get_object('av_img')
		self.av_img.set_from_file('./db_images/av.png')
				
		self.vt_img = self.builder.get_object('vt_img')
		self.vt_img.set_from_file('./db_images/vt.png')

		self.vt_img = self.builder.get_object('inspec_img')
		self.vt_img.set_from_file('./db_images/inspec_img.png')

		# Load das janelas
		self.window = self.builder.get_object("main_window")
		self.mensagem_delete = self.builder.get_object("mensagem_delete")
		self.mensagem_save = self.builder.get_object("mensagem_save")
		self.mensagem_sobreescrever = self.builder.get_object("mensagem_sobreescrever")
		self.mensagem_null = self.builder.get_object("mensagem_null")
		self.mensagem_jc = self.builder.get_object("mensagem_jc")
		self.window.show()
		self.window.fullscreen()

		self.image = self.builder.get_object('image')
		self.image.set_from_file("./db_images/report.png")

	# Método que gera o relatório parcial
	def dados_parciais(self):
		self.BicoTreeView = self.builder.get_object('BicoTreeView')
		self.BicoListStore = Gtk.ListStore (str,str,str,str,str,str)
	
		for column in self.BicoTreeView.get_columns():
			self.BicoTreeView.remove_column(column)

		for i in range(len(extrair_dados('dados'))):
			if extrair_dados('dados')[i][0] == regiao3 and extrair_dados('dados')[i][1] == pais3 and extrair_dados('dados')[i][2] == guia2\
			and extrair_dados('dados')[i][3] == site4:
				self.BicoListStore.append(extrair_dados('dados')[i][8:14])	

		global a
		i=0
		j=1
		a=len(self.BicoListStore)
		
		while i < a:
			while j < a:
				if self.BicoListStore[i][0]==self.BicoListStore[j][0]:
					self.BicoListStore.remove(self.BicoListStore[i].iter)
					a=len(self.BicoListStore)
					i=0
					j=0
				if j < a:
					j+=1
			i+=1
			j=i+1
	
		
		for i, col_title in enumerate(['Código','Tipo','Vida Atual','Posição','Carro']):
			renderer = Gtk.CellRendererText()
			Column = Gtk.TreeViewColumn(col_title,cell_renderer = renderer,text= i)
			self.BicoTreeView.set_model(self.BicoListStore)
			self.BicoTreeView.append_column(Column)

	# Método que gera o relatório completo
	def relatorio(self):
		#self.pathListStore.clear()
		self.current_id = None
		self.pathTreeView = self.builder.get_object("pathTreeView")
		self.pathListStore = Gtk.ListStore(str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str)
		lista = ['Código','Tipo','Vida','Posição','Carro','Convertedor','Operador','Data','Ângulo','D1','D2',
		'D3','D4','D5','D6','D. Ext.']

		for column in self.pathTreeView.get_columns():
			self.pathTreeView.remove_column(column)
		
		for i in range(len(filtro('Dados',regiao4,pais4,nome_usina,site3))):
			self.pathListStore.append(filtro('Dados',regiao4,pais4,nome_usina,site3)[i][8:])
		
		self.id_filter = self.pathListStore.filter_new()
		self.id_filter.set_visible_func(self.id_filter_func)

		for i, col_title in enumerate(lista):
			renderer = Gtk.CellRendererText()
			Column = Gtk.TreeViewColumn(col_title,cell_renderer = renderer,text= i)
			self.pathTreeView.set_model(self.id_filter)
			self.pathTreeView.append_column(Column)

	# Troca a imagem do relatorio de acordo com a imagem
	def setSelected(self,selection):
		global model,row,life
		global path
		model, row = selection.get_selected()
		life = model[row][2]
		path = "./assets/"
		if row is not None:
			print("Name= "+ model[row][3])
			self.image = self.builder.get_object('image')
			print(path+site3+'-'+model[row][0]+'-'+model[row][2]+'-A'+".jpg")
			frame_original= cv2.imread(path+site3+'-'+model[row][0]+'-'+model[row][2]+'-A'+".jpg")
			frame_original = cv2.resize(frame_original, dsize=(600, 338), interpolation=cv2.INTER_CUBIC)
			loadingImg = GdkPixbuf.Pixbuf.new_from_data(frame_original.tobytes(),GdkPixbuf.Colorspace.RGB,False,8,frame_original.shape[1],frame_original.shape[0],frame_original.shape[2]*frame_original.shape[1])
			self.image.set_from_pixbuf(loadingImg.copy())
			self.builder.get_object("vida").set_text("Vida: "+model[row][2])

	#Carrega as logos
	def logo(self, logo_lumar_id, logo_visiontech_id):
		self.im_lumar = self.builder.get_object(logo_lumar_id)
		self.im_visiontech = self.builder.get_object(logo_visiontech_id)
		self.im_lumar.set_from_file("./db_images/logo_lumar"+".png")
		self.im_visiontech.set_from_file("./db_images/logo_visiontech"+".png")

	# Tela inicial 
	def on_button_cdu_clicked(self, widget):
		self.stack.set_visible_child_name("page1")

	def on_button_bico_cad_clicked(self, widget):
		self.combobox_regiao("combobox_regiao")
		self.stack.set_visible_child_name("page2")

	def on_button_dados_clicked(self, widget):
		self.combobox_regiao('combobox_regiao3')
		self.stack.set_visible_child_name("page3")

	def on_button_inserir2_clicked(self,widget):
		global aux
		self.combobox_regiao("combobox_regiao4")
		self.stack.set_visible_child_name("page5")

	def on_button_inspec_clicked (self, widget):
		self.combobox_regiao("combobox_regiao2")
		self.stack.set_visible_child_name("page6")

	# Tela de Cadastro de usina 
	def on_button_ti_clicked(self,widget):
		self.stack.set_visible_child_name("page0")
		self.reset_cad_entry()

	def on_button_cb_clicked(self,widget):
		self.combobox_regiao("combobox_regiao")
		self.stack.set_visible_child_name("page2")
		self.reset_cad_entry()

	def on_button_ver_clicked(self,widget):
		self.stack.set_visible_child_name("page3")
		self.reset_cad_entry()

	def on_button_sav_clicked (self,widget):
		global guia2

		self.reg = self.builder.get_object('entry1')
		self.reg_text = self.reg.get_text().upper()

		self.pais = self.builder.get_object('entry2')
		self.pais_text = self.pais.get_text().upper()

		self.grupos = self.builder.get_object('entry3')
		self.grupos_text = self.grupos.get_text()
		self.grupos_text = verifica_espacos(self.grupos_text).capitalize()

		self.site = self.builder.get_object('entry4')
		self.site_text = self.site.get_text().capitalize()

		self.bof = self.builder.get_object('entry5')
		self.bof_text = self.bof.get_text().lower()

		self.capacity = self.builder.get_object('entry6')
		self.capacity_text = self.capacity.get_text().lower()

		self.lancas = self.builder.get_object('entry7')
		self.lancas_text = self.lancas.get_text().lower()

		self.carros = self.builder.get_object('entry8')
		self.carros_text = self.carros.get_text().upper()

		
		if check_caixa_vazia(self.reg_text) or check_caixa_vazia(self.pais_text) \
			or check_caixa_vazia(self.grupos_text) or check_caixa_vazia(self.site_text)\
			or check_caixa_vazia(self.bof_text) or check_caixa_vazia(self.capacity_text)\
			or check_caixa_vazia(self.lancas_text) or check_caixa_vazia(self.carros_text):
			self.mensagem_null.run()

		elif len(check_table()) == 0 or contar_linhas('Usinas') == 0:
			criar_tabela_usinas()
			criar_tabela_dados()

			insert_usina('0',self.reg_text,self.pais_text,self.grupos_text,self.site_text,self.bof_text,self.capacity_text,self.lancas_text,self.carros_text)
			usinas = dados_coluna('Grupo')
			c=len(usinas)
			usina=usinas[-1]
			self.liststore.append([c,usina])
			guia2 = self.grupos_text
			self.mensagem_save.run()
			self.reset_cad_entry()

		else:
			for i in range(len(dados_coluna('Grupo'))):
				if dados_coluna('Grupo')[i] == self.grupos_text and dados_coluna('Site')[i] == self.site_text and dados_coluna('REGIAO')[i] == self.reg_text and dados_coluna('País')[i] == self.pais_text:
					name = self.grupos_text
					self.mensagem_sobreescrever.run()
					self.reset_cad_entry()

					if yes == True:
						atualizar('Usinas','BOF', self.bof_text, str(i))
						atualizar('Usinas','Capacity', self.capacity_text, str(i))
						atualizar('Usinas','Lanças', self.lancas_text, str(i))
						atualizar('Usinas','Carros', self.carros_text, str(i))

						self.liststore.append([i,name])
						guia2 = self.grupos_text
						self.mensagem_save.run()
						self.reset_cad_entry()
					return

			criar_tabela_usinas()
			criar_tabela_dados()

			insert_usina(contar_linhas('Usinas'),self.reg_text,self.pais_text,self.grupos_text,
				self.site_text,self.bof_text,self.capacity_text,self.lancas_text,self.carros_text)
					
			usinas = dados_coluna('Grupo')

			c=len(usinas)
			usina=usinas[-1]
			self.liststore.append([c,usina])
			guia2 = self.grupos_text
			self.mensagem_save.run()
			self.reset_cad_entry()


	def reset_cad_entry(self):
		for i in range(1,9):
			self.builder.get_object(f'entry{i}').set_text('')
	
	# Tela cadastro de bicos 
	def on_button_ti2_clicked(self, widget):
		self.stack.set_visible_child_name("page0")
		self.reset_cad_bico()

	def on_ok2_clicked (self,widget):
		self.mensagem_jc.hide()

	def on_button_sav2_clicked(self,widget):
		self.codigo_text = self.builder.get_object('entryb1').get_text().upper()
		#self.tipo_text = self.builder.get_object('entryb2').get_text()
		self.tipo_text = tipo
		self.posicao_text = self.builder.get_object('entryb3').get_text().capitalize()
		self.carro_text = self.builder.get_object('entryb4').get_text().capitalize()
		self.conv_text = self.builder.get_object('entryb5').get_text().capitalize()
		carro = acessar_dados('carro','dados','Bico_id',self.codigo_text, tipo=self.tipo_text,convertedor=self.conv_text,Posição=self.posicao_text)
		
		
		if check_caixa_vazia(self.codigo_text) or check_caixa_vazia(self.tipo_text) or check_caixa_vazia(self.posicao_text) \
		or check_caixa_vazia(self.carro_text) or check_caixa_vazia(self.conv_text):
			self.mensagem_null.run()

		elif verifica_existencia('dados','Bico_id',self.codigo_text,grupo = guia,site = site,país = pais,regiao = regiao,carro = self.carro_text)== 1:
			self.mensagem_jc.run()
			self.reset_cad_bico()
		else:
			bof = selecionar_linhas('BOF','Usinas','Site',site,'Grupo', guia,'país',pais)
			capacity = selecionar_linhas('Capacity','Usinas','Site',site,'Grupo', guia,'país',pais)
			lancas = selecionar_linhas('Lanças','Usinas','Site',site,'Grupo', guia,'país',pais)
			carros = selecionar_linhas('Carros','Usinas','Site',site,'Grupo', guia,'país',pais)
			insert_dados(regiao,pais,guia,site,bof,capacity,lancas,carros,self.codigo_text,self.tipo_text,
			self.posicao_text,self.carro_text,self.conv_text)
			self.mensagem_save.run()
			self.reset_cad_bico()
	
	def combobox_regiao(self,nome_combobox):
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.liststore_regiao.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore_regiao)

		regioes = dados_coluna('regiao')
		regioes = sorted(set(regioes))
		for c,regiao in enumerate(regioes):
			self.liststore_regiao.append([c,regiao])

		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)

	def combobox_pais(self,nome_combobox,nome_regiao):
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.liststore_pais.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore_pais)

		paises = acessar_dado_pontual("País","Usinas","REGIAO",nome_regiao)
		paises = sorted(set(paises))

		c=0
		for i in range(len(paises)):
			self.liststore_pais.append([c,paises[i][0]])
			c=c+1

		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)
	
	def combobox_site(self,nome_usina,nome_combobox):
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.liststore_site.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore_site)
		sites = acessar_dado_pontual("Site","Usinas","Grupo",nome_usina)

		c=0
		for i in range(len(sites)):
			self.liststore_site.append([c,sites[i][0]])
			c=c+1

		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)
		
	def combobox_tipo(self,nome_combobox):
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.liststore_tipo.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore_tipo)

		if len(dados_coluna('regiao')) == 0:
			tipos = ['']
		else:
			tipos = ['Slagless 6 Furos - Usiminas','GGOB - 6 Furos','GGOB - 5 Furos','Slagless 4 Furos - Usiminas']

		for c,tipo in enumerate(tipos):
			self.liststore_tipo.append([c,tipo])

		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)

	def on_combobox_regiao_changed(self,widget,data=None):
		global regiao

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		regiao = self.item
		self.combobox_pais("combobox_pais",regiao)
	
	def on_combobox_pais_changed(self,widget,data=None):
		global pais

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		pais = self.item
		self.combobox_usina("us",regiao,pais)
		self.combobox_tipo('combobox_tipo')
	
	def on_combobox_site_changed(self,widget,data=None):
		global site
		global site4

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		site = self.item
		self.combobox_tipo('combobox_tipo')
		try:
			site4 = site
		except Exception:
			pass
		self.combobox_tipo('combobox_tipo')

	def on_combobox_tipo_changed(self,widget,data=None):
		global tipo

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		tipo = self.item

	def on_button_gr_clicked(self,widget):
		self.combobox_regiao("combobox_regiao2")
		self.reset_cad_bico()
		self.stack.set_visible_child_name("page6")

	def on_button_see_clicked(self,widget):
		self.reset_cad_bico()
		self.combobox_regiao("combobox_regiao3")
		self.stack.set_visible_child_name("page3")

	def on_us_changed(self, widget, data=None):
		global guia
		global guia2
		global index

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		guia = self.item
		try:
			guia2 = guia
		except Exception:
			pass
		index = self.index
		self.combobox_site(guia,"combobox_site")

	def reset_cad_bico(self):
		self.builder.get_object("entryb1").set_text('')
		#self.builder.get_object("entryb2").set_text('')
		self.builder.get_object("entryb3").set_text('')
		self.builder.get_object("entryb4").set_text('')
		self.builder.get_object("entryb5").set_text('')

	# Tela de dados usinas 
	def on_button_ti3_clicked(self,widget):
		self.stack.set_visible_child_name("page0")
	
	def on_combobox_regiao3_changed(self, widget, data=None):
		global regiao3
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		regiao3 = self.item	
		self.combobox_pais("combobox_pais3",regiao3)
	
	def on_combobox_pais3_changed(self, widget, data=None):
		global pais3
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		pais3 = self.item
		self.combobox_usina("us1",regiao3,pais3)
	
	def on_us1_changed(self, widget):
		global guia2
		global index
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		guia2 = self.item
		index = self.index
		self.combobox_site(guia2,"combobox_site4")
	
	def on_combobox_site4_changed (self,widget):
		global site4

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		site4 = self.item
		self.dados_parciais()

	def on_button_vr_clicked (self,widget):
		self.combobox_regiao("combobox_regiao2")
		self.stack.set_visible_child_name("page5")

	def on_main_window_destroy(self, widget, data=None):
		print ("quit with cancel")
		Gtk.main_quit()

	#Tela de relatorio
	def on_button_ti5_clicked (self,widget):
		self.stack.set_visible_child_name("page0")

	def on_combobox_regiao4_changed(self, widget, data=None):
		global regiao4
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		regiao4 = self.item
		self.combobox_pais("combobox_pais4",regiao4)
	
	def on_combobox_pais4_changed(self, widget, data=None):
		global pais4
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		pais4 = self.item
		self.combobox_usina("u",regiao4,pais4)

	def on_u_changed (self,widget):
		global nome_usina
		self.index = widget.get_active()
		self.model = widget.get_model()
		
		self.item = self.model[self.index][1]
		nome_usina = self.item
		self.combobox_site(nome_usina,"combobox_site3")
	
	def on_combobox_site3_changed(self,widget,data=None):
		global site3
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		site3 = self.item
		self.combobox_codigo(nome_usina,site3,"id")

	def on_id_changed (self,widget):
		global id
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.current_id = 'Nan'
		self.relatorio()
		self.item = self.model[self.index][1]
		id = self.item
		self.current_id = id
		self.id_filter.refilter()

	def combobox_codigo(self,x,y,nome_combobox):
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.liststore_codigo.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore_codigo)

		codigos = ler_colunas('Bico_id','dados','Grupo',x,'Site',y)
		codigos = sorted(set(codigos))
		
		c=0
		for i in range(len(codigos)):
			self.liststore_codigo.append([i,codigos[i][0]])
			c=c+1
		
		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)

	def combobox_usina(self,nome_combobox,x,y):
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.liststore.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore)

		usinas = ler_colunas('Grupo','usinas','regiao',x,'país',y)
		usinas = sorted(set(usinas))

		c=0
		for i in range(len(usinas)):
			self.liststore.append([c,usinas[i][0]])
			c=c+1

		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)
	

	# Deleta todos os dados relacionados ao grupo
	def on_button_del1_clicked(self,widget):
		self.mensagem_delete.run()
		if sim == True:
			delete_dados('usinas','Grupo',nome_usina,'País',pais4)
			delete_dados('dados','Grupo',nome_usina,'País',pais4)
			self.combobox_regiao("combobox_regiao4")
		if len(dados_coluna('regiao')) == 0:
			self.combobox_pais("combobox_pais4",'')
			self.combobox_usina("u",'','')
			self.combobox_site('',"combobox_site3")
			self.combobox_codigo('','',"")	

	# Deleta uma linha da tabela do databse
	def on_button_del2_clicked(self,widget):
		if check_null('dados',"vida",'país',pais4,'grupo',nome_usina,'site',site3,'bico_id',id) == 0:
			delete_dados('dados','REGIAO',regiao4,'País',pais4,'Grupo',nome_usina,'site',site3,'bico_id',id,'vida',life)
		else:
			delete_dados('dados','REGIAO',regiao4,'País',pais4,'Grupo',nome_usina,'site',site3,'bico_id',id,mode=True)
		self.combobox_regiao("combobox_regiao4")
		self.combobox_codigo(nome_usina,site3,"id")

	def on_button_sim_clicked(self,widget):
		global sim

		self.mensagem_delete.hide()
		sim = True

	def on_button_nao_clicked(self,widget):
		global sim
		self.mensagem_delete.hide()
		sim = False

	# Mensagens de dialogo 
	def on_button_cd1_clicked (self,widget):
		self.stack.set_visible_child_name("page2")

		try:
			self.combobox.set_active(0)
		except Exception:
			pass

	def on_button_ok_clicked (self,widget):
		self.mensagem_save.hide()
		self.reset_cad_bico()

	def on_button_ti6_clicked (self,widget):
		self.stack.set_visible_child_name("page0")

	def	on_button_vb1_clicked (self,widget):
		self.stack.set_visible_child_name("page3")

	# Fecha a tela de dialogo
	def on_ok_clicked (self,widget):
		self.mensagem_null.hide()


	# Sobreescreve os dada de acordo com a requisição
	def on_button_yes_clicked (self,widget):
		global yes

		self.mensagem_sobreescrever.hide()
		yes = True


	def on_button_no_clicked (self,widget):
		global yes
		self.mensagem_sobreescrever.hide()
		yes = False

	# Função que filtra a tabela do relatório de acordo com o id
	def id_filter_func(self, model, iter, data):
        #Tests if the id in the row is the one in the filter
		if (self.current_id is None or self.current_id == "None"):
			return True
		else:
			return model[iter][0] == self.current_id		

	# Geração da combobox carro	
	def combobox_carro(self,grupo,site,nome_combobox):
		self.liststore_carro.clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}").clear()
		self.combobox = self.builder.get_object(f"{nome_combobox}")
		self.combobox.set_model(self.liststore_carro)

		carros = ler_colunas2('Carro','dados','Grupo',grupo,'Site',site,'bico_id',cod)
		carros = sorted(set(carros))	

		c=0
		for i in range(len(carros)):
			self.liststore_carro.append([c,carros[i][0]])
			c+=1
		
		self.cell = Gtk.CellRendererText()
		self.combobox.pack_start(self.cell, True)
		self.combobox.add_attribute(self.cell, 'text', 1)
		self.combobox.set_active(0)


	# Mostra a imagem posterior no relatório
	def on_button_next_img_clicked(self,widget):
		global aux2
		global model,row
		
		if aux2==0:
			frame_original= cv2.imread(path+site3+'-'+model[row][0]+'-'+model[row][2]+'-B'+".jpg")
			frame_original = cv2.resize(frame_original, dsize=(600, 338), interpolation=cv2.INTER_CUBIC)
			aux2=1
		elif aux2==1:
			frame_original= cv2.imread(path+site3+'-'+model[row][0]+'-'+model[row][2]+'-A'+".jpg")
			frame_original = cv2.resize(frame_original, dsize=(600, 338), interpolation=cv2.INTER_CUBIC)
			aux2=0
		loadingImg = GdkPixbuf.Pixbuf.new_from_data(frame_original.tobytes(),GdkPixbuf.Colorspace.RGB,False,8,frame_original.shape[1],frame_original.shape[0],frame_original.shape[2]*frame_original.shape[1])
		self.image.set_from_pixbuf(loadingImg.copy())

	# Mostra a imagem anterior no relatório
	def  on_button_back_img_clicked(self,widget):
		global aux2
		global model,row
		if aux2==0:
			frame_original= cv2.imread(path+site3+'-'+model[row][0]+'-'+model[row][2]+'-B'+".jpg")
			frame_original = cv2.resize(frame_original, dsize=(600, 338), interpolation=cv2.INTER_CUBIC)
			aux2=1
		elif aux2==1:
			frame_original= cv2.imread(path+site3+'-'+model[row][0]+'-'+model[row][2]+'-A'+".jpg")
			frame_original = cv2.resize(frame_original, dsize=(600, 338), interpolation=cv2.INTER_CUBIC)
			aux2=0
		loadingImg = GdkPixbuf.Pixbuf.new_from_data(frame_original.tobytes(),GdkPixbuf.Colorspace.RGB,False,8,frame_original.shape[1],frame_original.shape[0],frame_original.shape[2]*frame_original.shape[1])
		self.image.set_from_pixbuf(loadingImg.copy())

	# Tela de inspeção
	# Sinal gerado ao selecionar a combobox regiao
	def on_combobox_regiao2_changed(self, widget, data=None):
		global regiao2
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		regiao2 = self.item	
		self.combobox_pais("combobox_pais2",regiao2)

	# Sinal gerado ao selecionar a combobox rpaís
	def on_combobox_pais2_changed(self, widget, data=None):
		global pais2
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		pais2 = self.item
		self.combobox_usina("us2",regiao2,pais2)

	# Sinal gerado ao selecionar a combobox usina
	def on_us2_changed(self, widget, data=None):
		global usin
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		usin = self.item
		self.combobox_site(usin,"combobox_site2")

	# Sinal gerado ao selecionar a combobox site
	def on_combobox_site2_changed(self,widget,data=None):
		global site2

		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		site2 = self.item
		self.combobox_codigo(usin,site2,"cd2")

	# Sinal gerado ao selecionar a combobox codigo
	def on_cd2_changed(self, widget, data=None):
		global cod
		self.index = widget.get_active()
		self.model = widget.get_model()

		self.item = self.model[self.index][1]
		cod = self.item
		self.combobox_carro(usin,site2,"combobox_carro")

	# Sinal gerado ao selecionar a combobox carr0
	def on_combobox_carro_changed (self, widget, data=None):
		global car
		self.index = widget.get_active()
		self.model = widget.get_model()
		self.item = self.model[self.index][1]
		car = self.item

	# Verifica se as input boxs estão vazias e se os dados ja estão no database,então salva os dados caso tudo estiver correto
	def on_button_start_clicked(self,widget):
		vida = self.builder.get_object('entryc1').get_text()
		operador = self.builder.get_object('entryc2').get_text().title()
		data = self.builder.get_object('entryc3').get_text()

		if check_caixa_vazia(vida)  or check_caixa_vazia(operador) or check_caixa_vazia(data):
			self.mensagem_null.run()

		elif check_null('dados',"vida",'país',pais2,'grupo',usin,'site',site2) == 1:
				update("dados","Vida",vida,"Bico_id",cod,"Site",site2)
				update("dados","Operador",operador,"Bico_id",cod,"Site",site2)
				update("dados","Data",data,"Bico_id",cod,"Site",site2)
				tipo = acessar_dados('tipo','dados','Grupo', usin,Site=site2,bico_id=cod,carro=car)[0][0]

				self.mensagem_save.run()
				self.builder.get_object('entryc1').set_text('')
				self.builder.get_object('entryc2').set_text('')
				self.builder.get_object('entryc3').set_text('')
				process = subprocess.Popen(['python3', 'WRLSegmentationScreen.py', '--cod', str(cod), '--usi', str(usin), '--vida', str(vida),
				'--site', str(site2),'--pais',str(pais2),'--tipo',str(tipo)], stdout=None, stderr=None)
				#time.sleep(7)
				self.window.destroy()
				
		elif check_null('dados',"vida",'país',pais2,'grupo',usin,'site',site2) == 0:
			if check_values("dados","vida",vida,'país',pais2,'grupo',usin,'site',site2) == 1:
				self.mensagem_sobreescrever.run()
				if yes == True:
					self.mensagem_save.run()
					update("dados","Vida",vida,"Vida",vida,"Site",site2)
					update("dados","Operador",operador,"Vida",vida,"Site",site2)
					update("dados","Data",data,"Vida",vida,"Site",site2)
					
					self.builder.get_object('entryc1').set_text('')
					self.builder.get_object('entryc2').set_text('')
					self.builder.get_object('entryc3').set_text('')

					tipo = acessar_dados('tipo','dados','Grupo', usin,Site=site2,bico_id=cod,carro=car)[0][0]
					process = subprocess.Popen(['python3', 'WRLSegmentationScreen.py', '--cod', str(cod), '--usi',
					str(usin), '--vida', str(vida),'--site', str(site2),'--pais',str(pais2),'--tipo',str(tipo)], stdout=None, stderr=None)
					#time.sleep(7)
					self.window.destroy()

				else:
					self.builder.get_object('entryc1').set_text('')
					self.builder.get_object('entryc2').set_text('')
					self.builder.get_object('entryc3').set_text('')

			else:
					bof = selecionar_linhas('BOF','Usinas','Site',site2,'Grupo', usin,'país',pais2)
					capacity = selecionar_linhas('Capacity','Usinas','Site',site2,'Grupo', usin,'país',pais2)
					lancas = selecionar_linhas('Lanças','Usinas','Site',site2,'Grupo', usin,'país',pais2)
					carros = selecionar_linhas('Carros','Usinas','Site',site2,'Grupo', usin,'país',pais2)
					tipo = acessar_dados('tipo','dados','Grupo', usin,Site=site2,bico_id=cod,carro=car)[0][0]
					posicao = acessa_dado_4_cond('posição','dados','Grupo', usin,'Site',site2,'bico_id',cod,'carro',car)[0][0]
					convertedor = acessa_dado_4_cond('convertedor','dados','Grupo',usin,'Site',site2,'bico_id',cod,'carro',car)[0][0]
					#tipo = acessa_dado_4_cond('Tipo','dados','Grupo',usin,'Site',site2,'bico_id',cod,'carro',car)[0][0]

					insert_dados_inspec(regiao2,pais2,usin,site2,bof,capacity,lancas,carros,cod,tipo,posicao,car,vida,operador,data,convertedor)

					self.mensagem_save.run()
					self.builder.get_object('entryc1').set_text('')
					self.builder.get_object('entryc2').set_text('')
					self.builder.get_object('entryc3').set_text('')
					process = subprocess.Popen(['python3', 'WRLSegmentationScreen.py', '--cod', str(cod), '--usi', str(usin),
					'--vida', str(vida),'--site', str(site2),'--pais',str(pais2),'--tipo',str(tipo)], stdout=None, stderr=None)
					#time.sleep(7)
					self.window.destroy()


	# Troca para a tela de inspeção
	def on_button_start_seg_clicked(self,widget):
		self.stack.set_visible_child_name("page6")

	# Troca para a tela inicial
	def on_button_tela_clicked(self,widget):
		self.stack.set_visible_child_name("page0")
	

if __name__ == "__main__":
	main = Handler()
	Gtk.main()
