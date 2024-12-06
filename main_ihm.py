import matplotlib.pyplot as plt
import pandas
import tkinter as tk
from tkinter import ttk, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from bd import obtenir_df_projection, obtenir_df_coapparition, obtenir_dict_pers
import networkx as nx
import seaborn


class IHM:

    # **************************************************************************
    def __init__(self) -> None:

        # modèle --------------------------------------------------------------

        self.df_comp_prin_star_wars = obtenir_df_projection()


        # vue -----------------------------------------------------------------
        root = tk.Tk()
        root.title('ACP Projet Visage')

        # widget --------------------------------------------------------------
        frame_principale = ttk.Frame(root, padding="3 3 3 3")

        self.string_var_onglet = StringVar(value="ACP")
        radio_button_acp = ttk.Radiobutton(frame_principale, text="Analyse en Composantes Principales",
                                                variable=self.string_var_onglet, value="ACP",
                                                command=self.mettre_a_jour_graphique)
        radio_button_graphe = ttk.Radiobutton(frame_principale, text="Graphe des liaisons",
                                                variable=self.string_var_onglet, value="Graphe",
                                                command=self.mettre_a_jour_graphique)

        # initialisation du df_coapparition
        self.df_coapparition = obtenir_df_coapparition()

        # creation de la combobox
        self.dico_pers = obtenir_dict_pers()
        liste_pers = list(self.dico_pers.keys())
        liste_pers.insert(0, 'Tous')

        self.listCombo_graph = ttk.Combobox(frame_principale, values=liste_pers)
        self.listCombo_graph.current(0)


        figure = plt.figure()
        self.ax = figure.add_subplot()

        self.canvas = FigureCanvasTkAgg(figure, master=frame_principale)

        self.mettre_a_jour_graphique()

        # mise en page  -------------------------------------------------------
        frame_principale.grid(row=0, column=0, sticky="nsew")

        radio_button_acp.grid(row=0, column=0, sticky="nsw", padx=2, pady=2)
        radio_button_graphe.grid(row=0, column=1, sticky="nsw", padx=2, pady=2)
        self.listCombo_graph.grid(row=0, column=2, sticky="nsw", padx=2, pady=2)

        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky="nswe", padx=2, pady=2)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        frame_principale.columnconfigure(0, weight=1)
        frame_principale.columnconfigure(1, weight=1)
        frame_principale.rowconfigure(0, weight=0)
        frame_principale.rowconfigure(1, weight=1)



        # binding -------------------------------------------------------------
        root.bind("<space>", self.changer_onglet)
        self.listCombo_graph.bind('<<ComboboxSelected>>', self.changer_personne)

        # sinon la main loop ne s'arrête pas ----------------------------------
        def quit():
            root.quit()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", quit)

        # boucle principale  --------------------------------------------------
        root.mainloop()

    # **************************************************************************
    def mettre_a_jour_graphique(self) -> None:

        if self.string_var_onglet.get() == 'ACP' :

            self.ax.clear()
            seaborn.scatterplot(data=self.df_comp_prin_star_wars, x='x_projection', y='y_projection', hue='pseudonyme' , ax=self.ax)
            seaborn.move_legend(self.ax, loc=2,bbox_to_anchor = (1,1))
            self.canvas.draw()

        else :
            self.ajouter_graphe(self.ax, self.df_coapparition)

            self.canvas.draw()


    # **************************************************************************
    def ajouter_graphe(self, axes, df_coapparition):


        graphe = nx.Graph()
        for ligne_df_coapparition in range(len(df_coapparition.iloc[:,0])):
            pseudo_1 =df_coapparition.iloc[ligne_df_coapparition,0]
            pseudo_2 =df_coapparition.iloc[ligne_df_coapparition,1]
            poids =1/df_coapparition.iloc[ligne_df_coapparition,2]

            # creation des arrêtes du graphe
            graphe.add_weighted_edges_from([(pseudo_1, pseudo_2, poids)])

        axes.clear()
        position = nx.kamada_kawai_layout(graphe)

        nx.draw_networkx(graphe, pos=position, node_color = '0.9', edge_color = '0.5', ax=axes )


    # **************************************************************************
    def changer_onglet(self, *args) -> None:
        if self.string_var_onglet.get() == 'ACP':
            self.string_var_onglet.set('Graphe')
        else:
            self.string_var_onglet.set('ACP')

        self.mettre_a_jour_graphique()

    def changer_personne(self, *args):
        selection = self.listCombo_graph.get()

        if selection == 'Tous' :
            self.df_coapparition = obtenir_df_coapparition()
        else :
            self.df_coapparition = obtenir_df_coapparition(self.dico_pers[selection])

        self.mettre_a_jour_graphique()



ihm = IHM()