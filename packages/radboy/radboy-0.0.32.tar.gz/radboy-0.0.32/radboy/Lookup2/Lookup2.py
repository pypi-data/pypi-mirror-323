from radboy.DB.db import *
from radboy.DB.Prompt import *
from radboy.DB.Prompt import Prompt
from radboy.EntryExtras.Extras import *
from colored import Style,Fore,Back

class Lookup:
	def __init__(self,init_only=False):
		self.cmds={
		'1':{
			'cmds':['q','quit'],
			'exec':lambda self=self:exit("user quit!"),
			'desc':f'{Fore.light_red}Quit the program!{Style.reset}'
		},
		'2':{
			'cmds':['b','back'],
			'exec':None,
			'desc':f'{Fore.light_red}Go Back a Menu!{Style.reset}'
		},
		'3':{
			'cmds':['3','sbc','search_bc',],
			'exec':self.search,
			'desc':f'{Fore.light_blue}Lookup Codes by Barcode|Code{Style.reset}',
		},
		'4l':{
			'cmds':['4l','search_auto_long','sal'],
			'exec':self.SearchAuto,
			'desc':f'{Fore.light_blue}Search For Product by Name,Barcode,Code,Note,Size {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'4s':{
			'cmds':['4s','search_auto_short','sas'],
			'exec':lambda self=self:self.SearchAuto(short=True),
			'desc':f'{Fore.light_blue}Search For Product by Name,Barcode,Code,Note,Size {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'5':{
			'cmds':['5','sm','search_manual'],
			'exec':self.SearchManual,
			'desc':f'{Fore.light_blue}Search For Product by Field {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'6':{
			'cmds':['6','sch entry data extras short','sedes'],
			'exec':lambda self=self:self.entryDataExtrasSearch(longText=False),
			'desc':f'{Fore.light_blue}Search For Product by EntryDataExtras {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		},
		'7':{
			'cmds':['7','sch entry data extras long','sedel'],
			'exec':lambda self=self:self.entryDataExtrasSearch(longText=True),
			'desc':f'{Fore.light_blue}Search For Product by EntryDataExtras {Fore.cyan}*Note: these are text only searches, for numeric use Task Mode with the "s" command{Style.reset}'
		}

		}
		def mehelp(self):
				for k in self.cmds:
					#print(f"{Fore.medium_violet_red}{self.cmds[k]['cmds']}{Style.reset} -{self.cmds[k]['desc']}")
					yield f"{Fore.medium_violet_red}{self.cmds[k]['cmds']}{Style.reset} -{self.cmds[k]['desc']}"
		if init_only:
			return
		while True:
			def mkT(text,self):
				return text

			mode='LU'
			fieldname='ROOT'
			h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
			cmd=Prompt.__init2__(None,func=mkT,ptext=f"{h}Do What?",helpText='\n'.join([i for i in mehelp(self)]),data=self)
			if cmd in [None,]:
				return
			#cmd=input("Do What: ")
			for i in self.cmds:
				if cmd.lower() in self.cmds[i]['cmds']:
					if cmd.lower() in self.cmds['2']['cmds']:
						return
					else:
						self.cmds[i]['exec']()
						break

	def entryDataExtrasSearch(self,longText=False):
		while True:
			with Session(ENGINE) as session:
				search=Prompt.__init2__(None,func=FormBuilderMkText,ptext=f"Lookup@Search[EntryDataExtras[Field_Name is:*,Field_Value=]]:",helpText="Search All(*) fields",data="string")
				if search in [None,]:
					return
				fieldnames=[]
				fields=[]
				ttl=session.query(EntryDataExtras).group_by(EntryDataExtras.field_name).all()
				for i in ttl:
					if i not in fieldnames:
						fieldnames.append(i.field_name)
				ct=len(fieldnames)
				fieldnamestr=[f"{num}/{num+1} of {ct} -> {i}" for num,i in enumerate(fieldnames)]
				fieldnamestr='\n'.join(fieldnamestr)
				print(fieldnamestr)
				select=Prompt.__init2__(None,func=FormBuilderMkText,ptext="what fieldnames would you like to search?",helpText=fieldnamestr,data="list")
				if select in [None,]:
					return

				query=session.query(EntryDataExtras)
				q=[]
				try:
					for i in select:
						try:
							i=int(i)
							q.extend([EntryDataExtras.field_name==fieldnames[i],EntryDataExtras.field_value.icontains(search)])
						except Exception as e:
							print(e)
				except Exception as e:
					print(e)
				results=session.query(EntryDataExtras).filter(*q).all()
				xct=len(results)
				disp=[]
				there=[]
				for num,i in enumerate(results):
					entry=session.query(Entry).filter(Entry.EntryId==i.EntryId).first()
					if entry:
						if entry.EntryId not in there:
							there.append(entry.EntryId)
							if longText:
								msg=f"""{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{xct} -> {entry} """
							else:
								msg=f"""{Fore.cyan}{num}/{Fore.light_yellow}{num+1} of {Fore.light_red}{xct} -> {entry.seeShort()}"""
								extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==entry.EntryId).all()
								extras_ct=len(extras)
								if extras_ct == 0:
									print("no extras found")
								mtext=[]
								for n,e in enumerate(extras):
									mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
								mtext='\n'.join(mtext)
								msg+="\n"+mtext
							if msg not in disp:
								disp.append(msg)
				print('\n'.join(disp))



	def SearchAuto(self,short=False,returnable=False):
		while True:
			try:
				with Session(ENGINE) as session:
					def mkT(text,self):
						return text
					fields=[i.name for i in Entry.__table__.columns if str(i.type) == "VARCHAR"]
					if not short:
						mode='SEARCH_ALL_INFO'
					else:
						mode='SEARCH_BASIC_INFO'
					fieldname='LU_ROOT'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					stext=Prompt.__init2__(None,func=mkT,ptext=f"{h}Search[*]:",helpText="Search All(*) fields",data=self)
					if stext in [None,]:
						return
					query=session.query(Entry)
					if not stext:
						break
					
					q=[]
					for f in fields:
						q.append(getattr(Entry,f).icontains(stext.lower()))

					eid=None
					try:
						eid=int(stext)
						q.append(getattr(Entry,'EntryId')==eid)
					except Exception as e:
						print(e)

					query=query.filter(or_(*q))
					results=query.all()
					
					fields2=[i.name for i in EntryDataExtras.__table__.columns if str(i.type) == "VARCHAR"]
					q2=[]
					for f in fields2:
						q2.append(getattr(EntryDataExtras,f).icontains(stext.lower()))
					results2=session.query(EntryDataExtras).filter(or_(*q2)).all()

					entry_ids_from_extras=[]
					for i in results2:
						entry_ids_from_extras.append(i.EntryId)
					finalList=[]
					for i in entry_ids_from_extras:
						entry=session.query(Entry).filter(Entry.EntryId==i).first()
						if entry not in results:
							finalList.append(entry)
					for i in results:
						finalList.append(i)
					results=finalList
					ct=len(results)
					for num,r in enumerate(results):
						if num < round(0.25*ct,0):
							color_progress=Fore.green
						elif num < round(0.50*ct,0):
							color_progress=Fore.light_green
						elif num < round(0.75*ct,0):
							color_progress=Fore.light_yellow
						else:
							color_progress=Fore.light_red
						if num == ct - 1:
							color_progress=Fore.red
						if num == 0:
							color_progress=Fore.cyan	
						if not short:
							msg=f"{color_progress}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{r}\n"
							'''
							extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==r.EntryId).all()
							extras_ct=len(extras)
							if extras_ct == 0:
								print("no extras found")
							mtext=[]
							for n,e in enumerate(extras):
								mtext.append(f"\t -{Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
							mtext='\n'.join(mtext)
							msg+=mtext
							'''
						else:
							msg=f"{color_progress}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{r.seeShort()}\n"
							extras=session.query(EntryDataExtras).filter(EntryDataExtras.EntryId==r.EntryId).all()
							extras_ct=len(extras)
							if extras_ct == 0:
								print("no extras found")
							mtext=[]
							for n,e in enumerate(extras):
								mtext.append(f"\t- {Fore.orange_red_1}{e.field_name}:{Fore.light_steel_blue}{e.field_type}={Fore.light_yellow}{e.field_value} {Fore.cyan}ede_id={e.ede_id} {Fore.light_magenta}doe={e.doe}{Style.reset}")
							mtext='\n'.join(mtext)
							msg+=mtext
						print(msg)
					print(f"{Fore.light_yellow}There are {Fore.light_red}{ct}{Fore.light_yellow} Total Results for search {Fore.medium_violet_red}'{stext}'{Style.reset}{Fore.light_yellow}.{Style.reset}")
					print(f"{Fore.light_red}Fields Searched in {Fore.cyan}{fields}{Style.reset}")
					if returnable:
						return results
			except Exception as e:
				print(e)

	def SearchManual(self):
		while True:
			try:
				with Session(ENGINE) as session:
					def mkT(text,self):
						return text
					fields=[i.name for i in Entry.__table__.columns if str(i.type) == "VARCHAR"]
					fields=[i.name for i in Entry.__table__.columns if str(i.type) == "VARCHAR"]
					mode='SEARCH_MNL_SRCH_TXT'
					fieldname='LU_ROOT'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					stext=Prompt.__init2__(None,func=mkT,ptext=f"{h}Search[Field(s)]:",helpText="Search for Entry by field(s)",data=self)
					if stext in [None,]:
						return
					query=session.query(Entry)
					if not stext:
						break
					
					def mkTList(text,self):
						try:
							total=[]
							f=text.split(",")
							for i in f:
								if i in self:
									if i not in total:
										total.append(i)
							return total
						except Exception as e:
							return None
					mode='SEARCH_MNL_SRCH_FLD_NMS'
					fieldname='LU_ROOT'
					h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
					to_search=f"{Fore.light_red}Fields available to Search in {Fore.cyan}{fields}{Style.reset}"
					sfields=Prompt.__init2__(None,func=mkTList,helpText=f"fields separated by a comma, or just a field from fields [Case-Sensitive]{to_search}",ptext=f"{h}fields? ",data=fields)
					if sfields in [None,]:
						return
					if not sfields:
						break


					q=[]
					
					for f in sfields:
						q.append(getattr(Entry,f).icontains(stext.lower()))

					query=query.filter(or_(*q))
					results=query.all()
					ct=len(results)
					for num,r in enumerate(results):
						if num < round(0.25*ct,0):
							color_progress=Fore.green
						elif num < round(0.50*ct,0):
							color_progress=Fore.light_green
						elif num < round(0.75*ct,0):
							color_progress=Fore.light_yellow
						else:
							color_progress=Fore.light_red
						if num == ct - 1:
							color_progress=Fore.red
						if num == 0:
							color_progress=Fore.cyan	
						msg=f"{color_progress}{num}{Style.reset}/{Fore.light_red}{ct-1}{Style.reset} ->{r}"
						print(msg)
					print(f"{Fore.light_yellow}There are {Fore.light_red}{ct}{Fore.light_yellow} Total Results for search {Fore.medium_violet_red}'{stext}'{Style.reset}{Fore.light_yellow}.{Style.reset}")
					print(f"{Fore.light_red}Fields Searched in {Fore.cyan}{sfields}{Style.reset}")
			except Exception as e:
				print(e)

	def search(self):
		while True:
			try:
				mode='SEARCH_BY_BCD_OR_SHF'
				fieldname='LU_ROOT'
				h=f'{Prompt.header.format(Fore=Fore,mode=mode,fieldname=fieldname,Style=Style)}'
				def mkT(text,self):
					return text
				code=Prompt.__init2__(None,func=mkT,ptext=f"{h}Code/Barcode To Search For?",helpText="b/q/code/barcode",data=self)
				if code in [None,]:
					return
				print(f"{Fore.green}{Style.underline}Lookup Initialized...{Style.reset}")
				if code.lower() in self.cmds['1']['cmds']:
					self.cmds['1']['exec']()
				elif code.lower() in self.cmds['2']['cmds']:
					break
				else:
					with Session(ENGINE) as session:	
						query=session.query(Entry).filter(or_(Entry.Barcode==code,Entry.Code==code,Entry.ALT_Barcode==code))
						results=query.all()
						for num,r in enumerate(results):
							print(f'{Fore.red}{num}{Style.reset}/{Fore.green}{len(results)}{Style.reset} -> {r}')
						print(f"{Fore.cyan}There were {Fore.green}{Style.bold}{len(results)}{Style.reset} {Fore.cyan}results.{Style.reset}")
			except Exception as e:
				print(e)