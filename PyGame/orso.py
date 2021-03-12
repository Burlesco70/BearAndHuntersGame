import pygame
import time
import sys
import functools

# Palette - RGB colors
BLACK = (0, 0, 0)

# Metodo per ottimizzare il caricamento degli assets
# "lru_cache" decorator saves recent images into memory for fast retrieval.
@functools.lru_cache()
def get_img(path):
    return pygame.image.load(path)

@functools.lru_cache()
def get_img_alpha(path):
    return pygame.image.load(path).convert_alpha()

class BearGame:
    '''
    PyGame independent game class
    Class for logical board and game model
    20 positions:
    _ means empty;
    1-8-9 means hunters; 
    2 means bear;
    '''
    def __init__(self, max_bear_moves: int, hunter_starts: bool):
        # Start settings
        self.reset(max_bear_moves, hunter_starts)
        
    def reset(self, max_bear_moves: int, hunter_starts: bool) -> None:
        # Start and reset settings
        self._board = ['1', '8', '9', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '2']
        self._bear_position = 20
        self._bear_moves = 0
        self._hunter_starting_pos = -1
        # From external configuration
        self._is_hunter_turn = hunter_starts        
        self._max_bear_moves = max_bear_moves 

    def get_bear_moves(self) -> int:
        '''
        Counter of bear moves
        '''
        return self._bear_moves


    def get_max_bear_moves(self) -> int:
        '''
        Max bear moves
        '''
        return self._max_bear_moves

    def get_board_position(self, position:int) -> str:
        return self._board[position]

    def get_board_length(self) -> int:
        '''
        Return the length of the board
        '''
        return len(self._board)

    def get_hunter_starting_pos(self) -> int:
        return self._hunter_starting_pos
    
    def is_bear_winner(self) -> bool:
        '''Returns the winner in a string type for display purposes'''
        if not(self.get_possible_moves(self._bear_position)):
            return False
        if (self._bear_moves >= self._max_bear_moves):
            return True

    def get_winner(self) -> str:
        '''Returns the winner in a string type for display purposes'''
        if not(self.get_possible_moves(self._bear_position)):
            return 'Hanno vinto i cacciatori!'
        if (self._bear_moves >= self._max_bear_moves):
            return "Ha vinto l'orso, congratulazioni"

    def game_over(self) -> bool:
        if ( ( not(self.get_possible_moves(self._bear_position)) ) or (self._bear_moves >= self._max_bear_moves) ):
            return True
        else:
            return False

    def is_hunter(self, selection:str) -> bool:
        return selection in ['1','8','9']

    def is_hunter_turn(self) -> bool:
        return self._is_hunter_turn

    def manage_hunter_selection(self, sel:int) -> tuple:
        '''Input selection from user; return 2 outputs: 1) message, 2) bool if board must be redrawn (not useful in PyGame)'''
        selected_hunter = ''
        # Pick up pawn (starting pos -1)
        if self._hunter_starting_pos == -1:
            if (not(self.is_hunter(self._board[sel]))):
                return ("Seleziona un cacciatore!", True)
            else:
                self._hunter_starting_pos = sel
                return ("Cacciatore, fa' la tua mossa!", True)
        else: # Finding final position for hunter
            if sel in self.get_possible_moves(self._hunter_starting_pos):
                selected_hunter = self._board[self._hunter_starting_pos]
                self._board[self._hunter_starting_pos] = '_'
                self._board[sel] = selected_hunter
                self._hunter_starting_pos = -1
                self._is_hunter_turn = not(self._is_hunter_turn)
                return ("Orso, scegli la tua mossa!", True)
            else: # Go back to picking stage
                self._hunter_starting_pos = -1
                return ("Posizione non valida!", True)
    
    def manage_bear_selection(self,sel: int) -> tuple:
        '''Input selection from user; return 2 outputs: 1) message, 2) bool if board must be redrawn (not useful in PyGame)'''
        if sel in self.get_possible_moves(self._bear_position):
            # Bear makes the move
            self._board[self._bear_position] = '_'
            self._board[sel] = '2'
            self._bear_moves += 1
            self._bear_position = sel
            self._is_hunter_turn = not(self._is_hunter_turn)
            return ("Seleziona uno dei cacciatori!", True)
        else:
            return ("Posizione non valida...", False)
    
    def is_footprint_and_type(self, sel:int) -> tuple:
        '''
        Return a tuple:
        - if is a footprint
        - footprint type (HUNTER|BEAR)
        '''
        if self._is_hunter_turn:
            if self._hunter_starting_pos == -1:
                return (False, None)
            else:
                if sel in self.get_possible_moves(self._hunter_starting_pos):
                    return (True, "HUNTER")
                else:
                    return (False, None)
        else:
            if sel in self.get_possible_moves(self._bear_position):
                return (True, "BEAR")
            else:
                return (False, None)

    def get_possible_moves(self, position: int) -> list:
        '''Adjacent locations, index is position'''
        adjacent = [[1,2,3], #0
                [0,3,4],
                [0,3,6], #2
                [0,1,2,5],
                [1,7,8], #4
                [3,9,10,11],
                [2,12,13], #6
                [4,8,14],
                [7,4,14,9], #8
                [8, 10,5,15],
                [5,9,11,15],#10
                [5,10,15,12],
                [11,6,16,13],#12
                [6,12,16],
                [7,8,18],#14
                [9,10,11,17],
                [12,13,19], #16
                [15,18,19,20],
                [14,17,20], #18
                [16, 17, 20],
                [18, 17, 19]]
        moves = []
        #Check free positions
        for x in adjacent[position]:
            if self._board[x] == '_':
                moves.append(x)
        return moves


class OrsoPyGame():

    # Create the window
    FINESTRA_X=1536
    FINESTRA_Y=864
    DIM_CASELLA = 80

    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((OrsoPyGame.FINESTRA_X, OrsoPyGame.FINESTRA_Y))
        pygame.display.set_caption("Gioco dell'orso")
        # set game clock
        self.clock = pygame.time.Clock()
        self._load_assets_common()
        self._load_assets_menu()
        self._load_assets_game()
        # Gestione caselle: posizione e gruppo sprite
        self._caselle = [(730,0), (565,5), (900,5), #0,1,2
                    (730,135), (350,225), (730,225), #3,4,5
                    (1115,225), (315,385), (465,385), #6,7,8
                    (565,385), (730,385), (900,385), #9,10,11
                    (995,385), (1155,385), (350,565), #12,13,14
                    (730,565), (1115,565), (730,655), #15,16,17
                    (565,775), (900,775), (730,800)] #18.19.20
        # Creazione gruppo caselle
        self._lista_caselle = pygame.sprite.Group()
        for i,p in enumerate(self._caselle):
            #print(i,p)
            pos = CasellaGiocoOrso(i, self)
            # Definisco rect ma non image
            pos.rect = pygame.Rect(p[0],p[1], OrsoPyGame.DIM_CASELLA, OrsoPyGame.DIM_CASELLA)
            self._lista_caselle.add(pos)


    def _load_assets_common(self):
        self.ORSO_IDLE_IMG = get_img('images/little-bear-idle.png')
        self.TRE_CACCIATORI_IMG = get_img('images/TreCacciatoriTurno.png')

    def _load_assets_game(self):
        # Caricamento assets

        # Pannelli, controlli e immagini "messaggio"
        self.PANNELLO_UNO_IMG = get_img('images/buttonLong.png') #panel
        self.PANNELLO_DUE_IMG = get_img('images/panel.png') #panel_due

        self.USCITA_IMG = get_img('images/back.png')
        self.USCITA_RECT = self.USCITA_IMG.get_rect()
        self.USCITA_RECT.center = (1355,675)

        self.ORSO_VINCE = get_img_alpha("images/Lorso-vince.png")
        self.CACCIATORI_VINCONO = get_img_alpha("images/Vincono-i-cacciatori.png")

        # Scacchiera
        self.BOARD_IMG = get_img('images/board.png')
        # Posizioni nella board dove posizionare le pedine
        # Per controllo click sulla scacchiera    

        # Fonts
        self.LOBSTER_30 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',30)
        self.LOBSTER_45 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',45)
        self.LOBSTER_90 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',90)

    def _load_assets_menu(self):
        # Assets per menu
        # grafica titolo creata con https://textcraft.net/
        self.TITOLO = get_img_alpha("images/Gioco-dellorso.png")
        self.MENU_BACKGROUND = get_img("images/3d_board.png")
        self.INIZIA = get_img('images/buttonLong.png')
        self.INIZIA_RECT = self.INIZIA.get_rect()
        self.INIZIA_RECT.center = (1290, 720)
        self.INIZIA_STR = get_img_alpha("images/Inizia-a-giocare.png")

        self.ESCI_GIOCO = get_img('images/buttonLong.png')
        self.ESCI_GIOCO_RECT = self.ESCI_GIOCO.get_rect()
        self.ESCI_GIOCO_RECT.center = (290, 720)
        self.ESCI_GIOCO_STR = get_img_alpha("images/Esci-dal-gioco.png")

    def menu(self):
        '''
        Display main menu with PyGame
        TODO: richiedere opzioni: numero mosse, chi parte
        '''
        pygame.mixer.music.load('sounds/intro.wav')
        pygame.mixer.music.play(-1)

        self.screen.blit(self.MENU_BACKGROUND, (0, 0))#
        self.screen.blit(self.TITOLO, (500,20))
        self.screen.blit(self.ORSO_IDLE_IMG, (250, 420))
        self.screen.blit(self.TRE_CACCIATORI_IMG, (1200, 420))
        
        self.screen.blit(self.INIZIA, (1100, 680))
        self.screen.blit(self.INIZIA_STR, (1140, 700))

        self.screen.blit(self.ESCI_GIOCO, (100, 680))
        self.screen.blit(self.ESCI_GIOCO_STR, (170, 690))

        self._pos_call = (0, 0)
        self._running = True
        while self._running:
            self._pos_call = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:                
                    self._pos_call = pygame.mouse.get_pos()
                    # print(pos_call)
                    # Per uscire
                    if self.ESCI_GIOCO_RECT.collidepoint(self._pos_call):
                        self._running = False
                        self.quit()

                    # Per iniziare il gioco
                    if self.INIZIA_RECT.collidepoint(self._pos_call):
                        self._running = False
                        pygame.time.delay(800)
                        # fade out menu music
                        pygame.mixer.music.fadeout(800)
                        self.game(30, True)

            pygame.display.update()

    def quit(self):
        pygame.time.delay(500)
        pygame.mixer.music.fadeout(500)
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()



    def game(self, numero_mosse: int, inizia_cacciatore: bool):
        '''
        Gioco implementato con PyGame
        '''
        pygame.mixer.music.load('sounds/orso_music.ogg')
        pygame.mixer.music.play(-1)

        # Inizializza la scacchiera e il gioco
        self.gioco_orso = BearGame(numero_mosse, inizia_cacciatore)
        msg = "L'orso vince facendo "+str(self.gioco_orso.get_max_bear_moves())+" mosse"
        
        # Inizializzazioni
        self._running = True
        self._pos_call = (0, 0)
        selezione = None   
        # show non usata, var per decidere se serve o no ridisegnare lo schermo
        show = True        

        while self._running:
            #self._pos_call = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    pygame.mixer.music.stop()
                    menu()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._pos_call = pygame.mouse.get_pos()
                    # print(self._pos_call)
                    # Verifica se click su freccia per uscita
                    if self.USCITA_RECT.collidepoint(self._pos_call):
                        self._running = False
                        pygame.mixer.music.stop()
                        self.menu()

                    for casella_cliccata in self._lista_caselle:
                        if casella_cliccata.rect.collidepoint(self._pos_call):
                            selezione = casella_cliccata.position
                            # Controlla e aggiorna gli spostamenti nella scacchiera
                            # Se click in posizione non corretta, ritorna solo un messaggio
                            if (self.gioco_orso.is_hunter_turn()):
                                msg, show = self.gioco_orso.manage_hunter_selection(selezione)
                            else:
                                msg, show = self.gioco_orso.manage_bear_selection(selezione)                        
        
            # Debug 
            #string = font.render("self._pos_call = " + str(self._pos_call), 1, BLACK)
            self.clock.tick(60)
            # Disegna la scacchiera
            self.screen.blit(self.BOARD_IMG, (0, 0))

            # Pannello mosse orso
            mosse_str = self.LOBSTER_45.render("Mosse orso", 1, BLACK)
            mosse = self.LOBSTER_90.render(str(self.gioco_orso.get_bear_moves()), 1, BLACK)    
            self.screen.blit(self.PANNELLO_DUE_IMG, (80, 80))  
            self.screen.blit(mosse_str, (90, 90))  
            self.screen.blit(mosse, (145, 140))    

            # Pannello turno
            self.screen.blit(self.PANNELLO_DUE_IMG, (1250, 80))
            turno_str = self.LOBSTER_45.render("Turno", 1, BLACK)
            self.screen.blit(turno_str, (1300, 90))
            if not self.gioco_orso.is_hunter_turn():
                self.screen.blit(self.ORSO_IDLE_IMG, (1320, 160))
            else:
                self.screen.blit(self.TRE_CACCIATORI_IMG, (1265, 160))

            # Pannello uscita
            self.screen.blit(self.USCITA_IMG, (1250, 580))

            # Aggiorna le caselle
            self._lista_caselle.update()
            self._lista_caselle.draw(self.screen)

            # Check fine del gioco
            if self.gioco_orso.game_over():
                msg = self.gioco_orso.get_winner()
                if self.gioco_orso.is_bear_winner():
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/orso_ride.wav'))
                    self.screen.blit(self.ORSO_VINCE, (580,380))            
                    
                else:
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/cacciatori_ridono.wav'))
                    self.screen.blit(self.CACCIATORI_VINCONO, (480,380))            

            # Pannello messaggi
            text = self.LOBSTER_30.render(msg, 1, BLACK)            
            self.screen.blit(self.PANNELLO_UNO_IMG, (40, 680))
            self.screen.blit(text, (50,705))

            # Aggiornamento screen
            pygame.display.update()

            # Reset del gioco
            if self.gioco_orso.game_over():
                time.sleep(5)
                # Si inverte chi inizia
                inizia_cacciatore = not(inizia_cacciatore)
                if inizia_cacciatore:
                    msg = "Ricominciano i cacciatori"
                else:
                    msg = "Ricomincia l'orso"
                self.gioco_orso.reset(numero_mosse, inizia_cacciatore)

class CasellaGiocoOrso(pygame.sprite.Sprite):
    # Static resources
    TRASPARENTE = pygame.Surface((80,80), pygame.SRCALPHA)

    ORSO_IMG = get_img('images/little-bear.png')
    ORSO_IDLE_IMG = get_img('images/little-bear-idle.png')
    ORSO_SEL_IMG = get_img('images/little-bear-sel.png')

    CACCIATORE_UNO_IMG = get_img('images/little-hunter1.png')
    CACCIATORE_UNO_IDLE_IMG = get_img('images/little-hunter1-idle.png')
    CACCIATORE_UNO_SEL_IMG = get_img('images/little-hunter1-sel.png')

    CACCIATORE_DUE_IMG = get_img('images/little-hunter2.png')
    CACCIATORE_DUE_IDLE_IMG = get_img('images/little-hunter2-idle.png')
    CACCIATORE_DUE_SEL_IMG = get_img('images/little-hunter2-sel.png')

    CACCIATORE_TRE_IMG = get_img('images/little-hunter3.png')
    CACCIATORE_TRE_IDLE_IMG = get_img('images/little-hunter3-idle.png')
    CACCIATORE_TRE_SEL_IMG = get_img('images/little-hunter3-sel.png')
        
    # Orme
    ORMA_ORSO_IMG = get_img('images/impronta_orso.png')
    ORMA_CACCIATORE_IMG = get_img('images/impronta_cacciatore.png')

    def __init__(self, position: int, game: OrsoPyGame):
        super().__init__()
        self.position = position
        self.game = game

    def update(self):
        # Disegna la pedine ottenendo la board dall'oggetto gioco
        bb = self.game.gioco_orso
        #print("aggiorno la casella ", self.position)
        if bb.get_board_position(self.position) == '_':
            # Controllo se è orma
            is_orma, tipo_orma  = bb.is_footprint_and_type(self.position)            
            if is_orma:
                #print(self.position, is_orma, tipo_orma)
                if tipo_orma == 'HUNTER':
                    self.image = CasellaGiocoOrso.ORMA_CACCIATORE_IMG
                else:
                    self.image = CasellaGiocoOrso.ORMA_ORSO_IMG                    
            else:
                self.image = CasellaGiocoOrso.TRASPARENTE
        # Verifica se è orso
        if bb.get_board_position(self.position) == '2':            
            if not bb.is_hunter_turn():
                self.image = CasellaGiocoOrso.ORSO_SEL_IMG
            else:
                self.image = CasellaGiocoOrso.ORSO_IMG
        # Verifica se è uno dei cacciatori
        if bb.get_board_position(self.position) == '1':
            if (bb.get_hunter_starting_pos() == self.position):
                self.image = CasellaGiocoOrso.CACCIATORE_UNO_SEL_IMG
            else:
                if bb.is_hunter_turn():
                    self.image = CasellaGiocoOrso.CACCIATORE_UNO_IMG
                else:
                    self.image = CasellaGiocoOrso.CACCIATORE_UNO_IDLE_IMG
        if bb.get_board_position(self.position) == '8':
            if (bb.get_hunter_starting_pos() == self.position):
                self.image = CasellaGiocoOrso.CACCIATORE_DUE_SEL_IMG
            else:
                if bb.is_hunter_turn():
                    self.image = CasellaGiocoOrso.CACCIATORE_DUE_IMG
                else:
                    self.image = CasellaGiocoOrso.CACCIATORE_DUE_IDLE_IMG
        if bb.get_board_position(self.position) == '9':
            if (bb.get_hunter_starting_pos() == self.position):
                self.image = CasellaGiocoOrso.CACCIATORE_TRE_SEL_IMG
            else:
                if bb.is_hunter_turn():
                    self.image = CasellaGiocoOrso.CACCIATORE_TRE_IMG
                else:
                    self.image = CasellaGiocoOrso.CACCIATORE_TRE_IDLE_IMG


# Main
if __name__ == "__main__":
    # Il gioco è richiamato da menu
    opg = OrsoPyGame()
    opg.menu()