class Dataset:
  def __init__(self):
    raise NotImplementedError("Subclasses must implement this method.")
  
  def __getitem__(self, index):
    raise NotImplementedError("Subclasses must implement this method.")
    
  def __len__(self):
    raise NotImplementedError("Subclasses must implement this method.")
  

"""
Tópicos:
  curto-prazo:
    encontros semanais para produzir mais no pipeflow (in progress);
    Publico alvo: Pessoa que faz muito experimento diariamente!  

    TASKS:
      Branchs (reproduzir igual o do mtsa, pedir acesso para Diego);
      Criar os Readmes (25/01/2025);
      Implementar o ransyconders no atelierflow (25/01/2025) - Partial;
      ir implementando em conjunto algumas features core (25/01/2025);
      Validar o modelo com curva roc (25/01/2025) - Partial;


  longo-prazo:
    usar o framework não so para treinar modelo;
    feature de analise comparativa de modelo;
    feature step core (appendResult, latex);
    comentar do rumo do framework;
    marcar uma "sprint" de refatoração (próximo ano)
"""

