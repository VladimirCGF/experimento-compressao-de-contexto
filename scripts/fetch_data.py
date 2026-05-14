import wikipediaapi
import os

def get_salmos_text():
    """
    Retorna o texto de Salmos 91:1-16 (Almeida Revista e Atualizada).
    """
    texto = """
    1 Aquele que habita no esconderijo do Altíssimo, à sombra do Onipotente descansará.
    2 Direi do Senhor: Ele é o meu Deus, o meu refúgio, a minha fortaleza, e nele confiarei.
    3 Porque ele te livrará do laço do passarinho, e da peste perniciosa.
    4 Ele te cobrirá com as suas penas, e debaixo das suas asas te confiarás; a sua verdade será o teu escudo e broquel.
    5 Não terás medo do terror de noite nem da seta que voa de dia,
    6 Nem da peste que anda na escuridão, nem da mortandade que assola ao meio-dia.
    7 Mil cairão ao teu lado, e dez mil à tua direita, mas não chegará a ti.
    8 Somente com os teus olhos contemplarás, e verás a recompensa dos ímpios.
    9 Porque tu, ó Senhor, és o meu refúgio. No Altíssimo fizeste a tua habitação.
    10 Nenhum mal te sucederá, nem praga alguma chegará à tua tenda.
    11 Porque aos seus anjos dará ordem a teu respeito, para te guardarem em todos os teus caminhos.
    12 Eles te sustentarão nas suas mãos, para que não tropeces com o teu pé em pedra.
    13 Pisarás o leão e a cobra; calcarás aos pés o filho do leão e a serpente.
    14 Porquanto tão encarecidamente me amou, também eu o livrarei; pô-lo-ei em retiro alto, porque conheceu o meu nome.
    15 Ele me invocará, e eu lhe responderei; estarei com ele na angústia; dela o retirarei, e o glorificarei.
    16 Fartá-lo-ei com longura de dias, e lhe mostrarei a minha salvação.
    """
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, "Salmos_91.txt")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(texto.strip())
        
    return texto.strip()

if __name__ == "__main__":
    get_salmos_text()
