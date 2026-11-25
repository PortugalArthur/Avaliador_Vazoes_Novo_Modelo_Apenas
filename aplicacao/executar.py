"""Janela de entradas e geração independente por linha de comando."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import queue
import tempfile
import threading
import webbrowser
from zoneinfo import ZoneInfo

from infraestrutura.preparar_ambiente import garantir_dependencias,PASTA_PROJETO
garantir_dependencias({'duckdb':'duckdb>=0.10','pandas':'pandas>=2.0','numpy':'numpy>=1.24',
                      'scipy':'scipy>=1.11','pyarrow':'pyarrow>=14','plotly':'plotly>=5.18',
                      'xlsxwriter':'XlsxWriter>=3.2','tzdata':'tzdata>=2024.1'})
from aplicacao.fontes import inspecionar,assinatura,sha256,periodo_proposto
from relatorio.blocos import ArquivoHTML
from relatorio.motor import calcular_modelo
from dados.validacao_dados_cobre import localizar_fontes_deck,validar_historico
from dados.cadastro_bacias import ler_cadastro_bacias
import pandas as pd

VERSAO='1.2.2'

def agora():
    return datetime.now(ZoneInfo('America/Sao_Paulo'))


def entradas_janela_novo_modelo(anteriores):
    """Recupera as entradas sem reaproveitar uma antiga fonte B do NEWAVE."""
    entradas=dict(anteriores) if isinstance(anteriores,dict) else {}
    if entradas.get('tipo_comparacao')!='novo_novo':
        for campo in ['newave','deck_referencia','newave_inicio','newave_fim']:
            entradas[campo]=''
        entradas['rotulo_referencia']='Novo modelo B'
    entradas['modelo']='Novo modelo'
    entradas['tipo_comparacao']='novo_novo'
    if entradas.get('modo') not in ('Análise','Comparação'):
        entradas['modo']='Análise'
    if not entradas.get('rotulo_referencia','').strip() or entradas['rotulo_referencia'].strip().casefold()=='newave':
        entradas['rotulo_referencia']='Novo modelo B'
    return entradas

def gerar(deck,novo=None,newave=None,periodos=None,saida=None,progresso=print, *,
          tipo_comparacao='novo_newave',deck_referencia=None,rotulo_novo=None,rotulo_referencia=None):
    if not novo or (newave and tipo_comparacao != 'novo_novo'):
        raise ValueError('Esta edição avalia apenas Parquets do Novo Modelo.')
    caminhos,nomes,fontes,limites=inspecionar(deck,novo,newave,periodos,progresso,
        tipo_comparacao=tipo_comparacao,deck_referencia=deck_referencia,
        rotulo_novo=rotulo_novo,rotulo_referencia=rotulo_referencia)
    origens=[Path(v) for v in caminhos.values()]+[Path(f.caminho) for f in fontes]
    antes=[assinatura(p) for p in origens]
    comparacao=len(fontes)==2
    modo='comparacao_novo_modelo_novo_modelo' if comparacao else 'analise_novo_modelo'
    if saida:
        destino=Path(saida).resolve()
        if destino.exists(): raise ValueError('A saída já existe. Escolha outro nome; relatórios anteriores são preservados.')
    else:
        destino=PASTA_PROJETO/'relatorios'/f'{modo}_{agora():%Y%m%d_%H%M%S}.html'
        i=1
        while destino.exists():
            destino=PASTA_PROJETO/'relatorios'/f'{modo}_{agora():%Y%m%d_%H%M%S}_{i}.html';i+=1
    if destino.suffix.lower()!='.html' or destino in [p.resolve() for p in origens]:
        raise ValueError('Selecione uma saída .html diferente das fontes.')
    arquivo=ArquivoHTML(destino)
    try:
        models=[]
        with tempfile.TemporaryDirectory(prefix='avaliador_html_') as tmp:
            for f in fontes: models.append(calcular_modelo(f,caminhos['historico'],tmp,arquivo,progresso))
        uhes=sorted(set(fontes[0].ids_deck.values()),key=lambda u:nomes[u])
        etapas=sorted(fontes[0].calendario.values(),key=lambda e:e['inicio'])
        manifesto={'versao':VERSAO,'modo':'Comparação' if comparacao else 'Análise','alfa':.05,
                   'tipo_comparacao':tipo_comparacao if comparacao else None,
                   'gerado_em':agora().isoformat(),'historico_disponivel':limites,
                   'usinas':[{'id':u,'nome':nomes[u]} for u in uhes],
                   'estagios':[{'i':i,'inicio':str(e['inicio']),'fim':str(e['fim']),'mes':e['mes'],'ano':e['ano'],
                                'rotulo':f"{e['mes']:02d}/{e['ano']}"} for i,e in enumerate(etapas)],
                   'modelos':models,'cadastro_versao':ler_cadastro_bacias().attrs.get('versao'),
                   'fontes':antes,'metodos':{'medias':'Welch bilateral','variancias':'Levene original — centro na média',
                                            'distribuicao':'KS bilateral — distribuição limite de Kolmogorov'}}
        manifesto['rotulos']=json.loads((PASTA_PROJETO/'recursos/rotulos.json').read_text(encoding='utf-8'))
        progresso('Conferindo integridade das fontes e gravando o HTML…')
        for a in antes:
            atual=assinatura(a['caminho'])
            if atual!=a: raise ValueError(f"A fonte mudou durante a geração: {a['caminho']}")
            a['sha256']=sha256(a['caminho'])
        caminho=arquivo.concluir(manifesto)
        progresso(f'Relatório concluído: {caminho}')
        return caminho,manifesto
    except BaseException:
        arquivo.cancelar();raise

def janela():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    raiz=tk.Tk();raiz.title('Avaliador de vazões — Novo Modelo');raiz.geometry('990x900');raiz.minsize(850,740)
    estilo=ttk.Style(raiz);estilo.theme_use('clam')
    for n in ['TFrame','TLabel']:estilo.configure(n,background='#f3f6fa',foreground='#102a43')
    estilo.configure('TLabel',font=('Segoe UI',10));estilo.configure('TButton',padding=8,font=('Segoe UI',10))
    estilo.configure('Titulo.TLabel',font=('Segoe UI',20,'bold'),foreground='#154765')
    raiz.configure(background='#f3f6fa')
    canvas=tk.Canvas(raiz,highlightthickness=0,background='#f3f6fa');scroll=ttk.Scrollbar(raiz,orient='vertical',command=canvas.yview)
    scroll.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True);canvas.configure(yscrollcommand=scroll.set)
    painel=ttk.Frame(canvas,padding=24);janela_painel=canvas.create_window((0,0),window=painel,anchor='nw')
    painel.bind('<Configure>',lambda _:canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure(janela_painel,width=e.width))
    raiz.bind_all('<MouseWheel>',lambda e:canvas.yview_scroll(int(-e.delta/120),'units'))
    painel.columnconfigure(1,weight=1)
    ttk.Label(painel,text='Avaliador de vazões em HTML',style='Titulo.TLabel').grid(row=0,column=0,columnspan=3,sticky='w')
    ttk.Label(painel,text='Novo Modelo · Cada versão avaliada contra seu histórico · Significância fixa: 5%').grid(row=1,column=0,columnspan=3,sticky='w',pady=(5,16))
    config=PASTA_PROJETO/'.ultimas_entradas.json'
    try: anteriores=json.loads(config.read_text(encoding='utf-8'))
    except (OSError,ValueError): anteriores={}
    anteriores=entradas_janela_novo_modelo(anteriores)
    vars={k:tk.StringVar(value=anteriores.get(k,v)) for k,v in [('modo','Análise'),('modelo','Novo modelo'),('deck',''),('novo',''),('newave',''),('novo_inicio',''),('novo_fim',''),('newave_inicio',''),('newave_fim',''),('tipo_comparacao','novo_novo'),('deck_referencia',''),('rotulo_novo','Novo modelo'),('rotulo_referencia','Novo modelo B')]}
    ttk.Label(painel,text='Geração').grid(row=2,column=0,sticky='w')
    cb=ttk.Combobox(painel,textvariable=vars['modo'],values=['Análise','Comparação'],state='readonly',width=20);cb.grid(row=2,column=1,sticky='w',pady=5)
    ttk.Label(painel,text='Novo modelo').grid(row=2,column=2,sticky='e')
    ttk.Label(painel,text='Tipo de comparação').grid(row=3,column=0,sticky='w',pady=8)
    comparador=ttk.Label(painel,text='Novo modelo × Novo modelo');comparador.grid(row=3,column=1,columnspan=2,sticky='w')
    botoes=[];botoes_fontes={};entradas={};etiquetas={};ocupado=False
    def atualizar_periodos():
        try:
            notas=[]
            chaves=['novo','newave'] if vars['modo'].get()=='Comparação' else ['novo']
            for chave in chaves:
                d=vars['deck_referencia' if chave=='newave' else 'deck'].get()
                if not d or not Path(vars[chave].get()).is_file():continue
                h=validar_historico(localizar_fontes_deck(d)['historico'])
                limites=[str(pd.Period(h['inicio'],freq='M')),str(pd.Period(h['fim'],freq='M'))]
                a,b,origem=periodo_proposto(vars[chave].get(),limites,'novo')
                vars[chave+'_inicio'].set(a);vars[chave+'_fim'].set(b)
                notas.append(f"{vars['rotulo_'+('novo' if chave=='novo' else 'referencia')].get()}: {a} a {b}. {origem}.")
            nota.set('\n'.join(notas) or 'Selecione os decks e Parquets para propor os períodos.')
        except (ValueError,OSError) as e:nota.set(str(e))
    for linha,chave,texto in [(4,'deck','Deck A — novo modelo'),(5,'novo','Parquet A — novo modelo'),(6,'newave','Parquet B — novo modelo'),(7,'deck_referencia','Deck B — novo modelo')]:
        lab=ttk.Label(painel,text=texto);lab.grid(row=linha,column=0,sticky='w',pady=7,padx=(0,10));etiquetas[chave]=lab
        en=ttk.Entry(painel,textvariable=vars[chave],state='readonly');en.grid(row=linha,column=1,sticky='ew',padx=(0,10));entradas[chave]=en
        def escolher(c=chave):
            base=Path(vars[c].get()).parent if vars[c].get() else PASTA_PROJETO.parent
            v=(filedialog.askdirectory(parent=raiz,title='Raiz do deck: system, scenarios e stages.json',initialdir=base) if c.startswith('deck') else
               filedialog.askopenfilename(parent=raiz,title='Selecionar Parquet',filetypes=[('Parquet','*.parquet')],initialdir=base))
            if v:vars[c].set(v);atualizar_periodos()
        bt=ttk.Button(painel,text='Selecionar…',command=escolher);bt.grid(row=linha,column=2);botoes.append(bt);botoes_fontes[chave]=bt
    for row,key,label in [(8,'rotulo_novo','Nome/versão A'),(9,'rotulo_referencia','Nome/versão B')]:
        ttk.Label(painel,text=label).grid(row=row,column=0,sticky='w',pady=6)
        en=ttk.Entry(painel,textvariable=vars[key]);en.grid(row=row,column=1,columnspan=2,sticky='ew');entradas[key]=en
    ttk.Label(painel,text='Histórico usado na avaliação — início e fim inclusivos (AAAA-MM)',font=('Segoe UI',11,'bold')).grid(row=10,column=0,columnspan=3,sticky='w',pady=(20,8))
    for row,chave in [(11,'novo'),(12,'newave')]:
        lab=ttk.Label(painel,text='Histórico A' if chave=='novo' else 'Histórico B');lab.grid(row=row,column=0,sticky='w');etiquetas[chave+'_hist']=lab
        fr=ttk.Frame(painel);fr.grid(row=row,column=1,columnspan=2,sticky='w',pady=5)
        for k,label in [('inicio','De'),('fim','Até')]:
            ttk.Label(fr,text=label).pack(side='left',padx=(0,8))
            en=ttk.Entry(fr,textvariable=vars[chave+'_'+k],width=13);en.pack(side='left',padx=(0,18));entradas[chave+'_'+k]=en
    nota=tk.StringVar(value='Selecione o deck e o Parquet do Novo Modelo. Para comparar versões, informe também o deck e o Parquet B.')
    ttk.Label(painel,textvariable=nota,wraplength=850,justify='left').grid(row=13,column=0,columnspan=3,sticky='w',pady=12)
    recalcular=ttk.Button(painel,text='Recarregar períodos propostos',command=atualizar_periodos);recalcular.grid(row=14,column=0,columnspan=3,sticky='w');botoes.append(recalcular)
    ttk.Label(painel,text='Comparação entre versões do Novo Modelo: mesmo horizonte e mesmas usinas. Cada versão usa o histórico do seu deck.\nSaída: um HTML independente em relatorios. Os arquivos originais são somente lidos.',wraplength=850).grid(row=15,column=0,columnspan=3,sticky='w',pady=(16,12))
    status=tk.StringVar(value='Pronto para conferir e gerar.');ttk.Label(painel,textvariable=status,wraplength=850).grid(row=16,column=0,columnspan=3,sticky='w',pady=8)
    barra=ttk.Progressbar(painel,mode='indeterminate');barra.grid(row=17,column=0,columnspan=3,sticky='ew',pady=8)
    fila=queue.Queue()
    def trabalhar():
        nonlocal ocupado
        if ocupado:return
        comparacao=vars['modo'].get()=='Comparação'
        chaves=['novo','newave'] if comparacao else ['novo']
        if not vars['deck'].get() or (comparacao and not vars['deck_referencia'].get()) or any(not vars[k].get() for k in chaves):
            messagebox.showerror('Entradas incompletas','Selecione o deck e o Parquet de cada versão do Novo Modelo escolhida.',parent=raiz);return
        if any(not vars[k+'_inicio'].get() or not vars[k+'_fim'].get() for k in chaves):
            messagebox.showerror('Período histórico','Informe início e fim para cada modelo selecionado.',parent=raiz);return
        args={'tipo_comparacao':'novo_novo' if comparacao else 'novo_newave',
              'deck_referencia':vars['deck_referencia'].get(),
              'rotulo_novo':vars['rotulo_novo'].get(),'rotulo_referencia':vars['rotulo_referencia'].get(),
              'deck':vars['deck'].get(),**{k:vars[k].get() for k in chaves},'periodos':{k:(vars[k+'_inicio'].get(),vars[k+'_fim'].get()) for k in chaves}}
        snapshot={k:v.get() for k,v in vars.items()};ocupado=True;barra.start(12)
        for b in botoes:b.configure(state='disabled')
        for w in [cb,comparador,*entradas.values()]:w.configure(state='disabled')
        def worker():
            try:fila.put(('ok',gerar(**args,progresso=lambda s:fila.put(('progresso',s))),snapshot))
            except Exception as e:fila.put(('erro',str(e),None))
        threading.Thread(target=worker,daemon=True).start()
    bt=ttk.Button(painel,text='Gerar relatório HTML',command=trabalhar);bt.grid(row=18,column=0,columnspan=3,sticky='e',pady=12);botoes.append(bt)
    def alternar(event=None):
        comparacao=vars['modo'].get()=='Comparação'
        comparador.configure(state='normal' if comparacao else 'disabled')
        for k in ['novo','newave']:
            ativo=k=='novo' or comparacao
            entradas[k].configure(state='readonly' if ativo else 'disabled')
            botoes_fontes[k].configure(state='normal' if ativo else 'disabled')
            for campo in ['inicio','fim']:entradas[k+'_'+campo].configure(state='normal' if ativo else 'disabled')
            nomekey='rotulo_'+('novo' if k=='novo' else 'referencia')
            entradas[nomekey].configure(state='normal' if ativo else 'disabled')
            etiquetas[k+'_hist'].configure(text='Histórico A' if k=='novo' else 'Histórico B')
        entradas['deck_referencia'].configure(state='readonly' if comparacao else 'disabled')
        botoes_fontes['deck_referencia'].configure(state='normal' if comparacao else 'disabled')
    cb.bind('<<ComboboxSelected>>',alternar);alternar()
    def acompanhar():
        nonlocal ocupado
        try:
            while True:
                e=fila.get_nowait()
                if e[0]=='progresso':status.set(e[1]);continue
                ocupado=False;barra.stop()
                for b in botoes:b.configure(state='normal')
                cb.configure(state='readonly');entradas['deck'].configure(state='readonly');alternar()
                if e[0]=='erro':status.set('Geração interrompida.');messagebox.showerror('Não foi gerado relatório',e[1],parent=raiz)
                else:
                    caminho,_=e[1];config.write_text(json.dumps(e[2],ensure_ascii=False,indent=2),encoding='utf-8')
                    status.set(f'Concluído: {caminho.name}');webbrowser.open(caminho.as_uri())
        except queue.Empty:pass
        raiz.after(150,acompanhar)
    def fechar():
        if ocupado:messagebox.showinfo('Geração em andamento','Aguarde a conclusão antes de fechar.',parent=raiz)
        else:raiz.destroy()
    raiz.protocol('WM_DELETE_WINDOW',fechar);raiz.after(150,acompanhar);raiz.mainloop()

def main():
    parser = argparse.ArgumentParser(description='Avaliador de vazões em HTML — Somente Novo Modelo.')
    parser.add_argument('--deck', help='Deck da versão A')
    parser.add_argument('--novo', help='Parquet da versão A')
    parser.add_argument('--deck-referencia', help='Deck da versão B, quando houver comparação')
    parser.add_argument('--novo-referencia', help='Parquet da versão B, quando houver comparação')
    parser.add_argument('--rotulo-novo', help='Nome da versão A')
    parser.add_argument('--rotulo-referencia', help='Nome da versão B')
    parser.add_argument('--saida', help='Caminho para um novo arquivo HTML')
    parser.add_argument('--sem-abrir', action='store_true', help='Gera o HTML sem abrir o navegador')
    for origem in ('novo', 'novo-referencia'):
        parser.add_argument(f'--{origem}-inicio', help='Início inclusivo do histórico (AAAA-MM)')
        parser.add_argument(f'--{origem}-fim', help='Fim inclusivo do histórico (AAAA-MM)')
    args = parser.parse_args()
    if not any(vars(args).values()):
        janela()
        return
    if not args.deck or not args.novo:
        parser.error('Informe --deck e --novo.')
    if bool(args.deck_referencia) != bool(args.novo_referencia):
        parser.error('Informe --deck-referencia e --novo-referencia juntos.')

    periodos = {}
    for campo, chave in (('novo', 'novo'), ('novo_referencia', 'newave')):
        inicio = getattr(args, campo + '_inicio')
        fim = getattr(args, campo + '_fim')
        if bool(inicio) != bool(fim):
            opcao = campo.replace('_', '-')
            parser.error(f'Informe --{opcao}-inicio e --{opcao}-fim juntos.')
        if inicio:
            periodos[chave] = (inicio, fim)
    if 'newave' in periodos and not args.novo_referencia:
        parser.error('Informe uma segunda versão para recortar o histórico B.')

    caminho, _ = gerar(
        args.deck, args.novo, args.novo_referencia, periodos, args.saida,
        progresso=lambda mensagem: print(mensagem, flush=True),
        tipo_comparacao='novo_novo' if args.novo_referencia else 'novo_newave',
        deck_referencia=args.deck_referencia, rotulo_novo=args.rotulo_novo,
        rotulo_referencia=args.rotulo_referencia,
    )
    if not args.sem_abrir:
        webbrowser.open(caminho.as_uri())


if __name__ == '__main__':
    main()
