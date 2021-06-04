#################################################
# Scripte réalisé dans le cadre du projet Pont par
# Charles AZAM
# Python 3.8
#################################################


#################################################
# Ce scripte permet de tracer des courbes 
# de contraintes et d'effort tranchant
# Penser à adapter le script
# Il utilise en entrée la sortie de RM (save to file)
#################################################


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def save_graph(file_name, title ="test",liste_piles = [2146,2216,2286,2356,2736,2806,2876],liste_piles_centrales = [2453,2469,2623,2639]):
    """[summary]
        Fonction permettant de tracer le diagramme des moments/efforts tranchant/ contraintes à partir d'une
    sortie RM-Bridge

    Args:
        file_name ([string]): [nom du fichier de sortie ex : fichier_sortie_moment.xls]
        title (str, optional): [titre du graph, sera utilisé comme nom pour l'image de sortie]. Defaults to "test".
        liste_piles (list, optional): [Liste des piles à tracer en vert]. Defaults to [2146,2216,2286,2356,2736,2806,2876].
        liste_piles_centrales (list, optional): [Liste des piles à tracer en violet]. Defaults to [2453,2469,2623,2639].
    """

    # lire le fichier RM
    try:
        lines_numpy = pd.read_excel(file_name).to_numpy()
    except:
        print("Error : Impossible d'ouvrir le fichier, vérifier le nom ou le répertoire")
        return

    # détermine le type du cas de charge (Moment, effort tranchant, contrainte)
    if lines_numpy[9][2] == 'Mz' :
        # cas un seul diagramme de moment
        type_chargement = 'Moment'
        name= lines_numpy[8][2]
        fibres = ['Moment']
    elif lines_numpy[9][2] == 'MinMz:Mz' :
        # cas 2 diagrammes min et max du moment
        type_chargement = 'Moment'
        name= lines_numpy[8][2]
        fibres = lines_numpy[9][2:4].tolist()
    elif lines_numpy[9][2].find("Qy")>-1:
        # cas diagramme effort tranchant
        type_chargement = 'Tranchant'
        name= lines_numpy[8][2]
        fibres = lines_numpy[9][2:4].tolist()
    elif lines_numpy[9][2].find("Vy")>-1:
        # cas déplacement
        type_chargement = 'Déplacement'
        name= lines_numpy[8][2]
        fibres = lines_numpy[9][2:4].tolist()
    else :
        # cas chargement de type contrainte
        type_chargement = 'Stress'
        names = lines_numpy[8][2:4].tolist()
        assert(names[0]==names[1])
        name = names[0]
        fibres = lines_numpy[10][2:4].tolist()

    # vérification
    print("Le graphique :",file_name," est détecté comme un diagramme de : ",type_chargement)

    # récupère les données
    lines_numpy[15]
    valeurs_numpy = lines_numpy[15:]
    numero_elem_first = int(valeurs_numpy[0][0])
    print(numero_elem_first)

    # ici seront sauvegarder les résultats
    new_valeurs = dict() # new_value['name'] = [num_elem,value]

    # récupération des résultats : initialisation 
    for i,fibre in enumerate(fibres):
        # correction des noms
        fibre = fibre.replace('RefStress:SupFibre','Fibre supérieure').replace('RefStress:InfFibre','Fibre inférieure')
        fibre = fibre.replace("MinQy:Qy","Min Effort Tranchant").replace("MaxQy:Qy","Max Effort Tranchant")
        fibre = fibre.replace("MinVy:Vy","Min Déplacement").replace("MaxVy:Vy","Max Déplacement")
        fibre = fibre.replace('MinMz:Mz',"Min Moment").replace('MaxMz:Mz',"Max Moment")
        fibres[i] = fibre
        new_valeurs[fibre] = []

    # récupération des résultats : lecture 
    for i,valeurs in enumerate(valeurs_numpy):

        # on saute cas pair
        if i%2 != 0:
            continue

        num_elem = valeurs[0]

        for i_fibre,fibre in enumerate(fibres):
            new_valeurs[fibre].append([int(num_elem),valeurs[2+i_fibre]])

    # transformation en objet numpy (pour pouvoir tracer)
    for fibre in fibres:
        new_valeurs[fibre] = np.array(new_valeurs[fibre])

    # Trace les piles
    #liste_piles = [2146,2216,2286,2356,2736,2806,2876]
    #liste_piles_centrales = [2453,2469,2623,2639]
    liste_pile_tot = liste_piles+liste_piles_centrales
    liste_pile_tot_str = [str(pile) for pile in liste_pile_tot]

    # liste des barres verticales que l'on va tracer
    liste_barres = [numero_elem_first + i*100 for i in range(9)]
    liste_barres_str = [str(i) for i in liste_barres]

    # Tracage des courbes
    plt.figure(figsize=(30,10))
    for i,fibre in enumerate(fibres):
        color = 'tab:blue'
        if i==1:
            color = 'tab:orange'

        if type_chargement == 'Stress':
            if fibre == 'Fibre supérieure':
                color = 'tab:blue'
            else :
                color = 'tab:orange'

        if type_chargement == 'Déplacement':
            plt.plot(new_valeurs[fibre][:,0],new_valeurs[fibre][:,1],label =fibre,color = color)
        else :
            plt.plot(new_valeurs[fibre][:,0],-new_valeurs[fibre][:,1],label =fibre,color = color)

    # nom des courbes et maillage
    plt.legend()
    plt.grid()

    # nom des axes
    if type_chargement == 'Moment':
        plt.ylabel("Moment (MN.m)")
    elif type_chargement == 'Tranchant':
        plt.ylabel("Effort tranchant (MN)")
    elif type_chargement == 'Déplacement':
        plt.ylabel("Déplacement différentiel (mm)")
    else:
        plt.ylabel("Stress (MPa)")

    # axe horizontal
    axes = plt.gca()
    axes.set_xticks(liste_barres+liste_pile_tot)
    axes.xaxis.set_ticklabels(liste_barres_str+liste_pile_tot_str,fontsize = 8,rotation = 90)

    # sauvegarde la zone de tracé initiale
    limites_x = axes.xaxis.get_view_interval()
    limites_y = axes.yaxis.get_view_interval()

    # axe vertical
    if type_chargement == "Moment":
        new_y_axis = list(range(int(limites_y[0]/10000)*10,int(limites_y[1]/1000)+1,10))
        new_y_axis_str = [str(-i) for i in new_y_axis]
        new_y_axis = [i*1000 for i in new_y_axis]

    elif type_chargement == "Effort tranchant (MN)":
        new_y_axis = list(range(int(limites_y[0]/1000),int(limites_y[1]/1000)+1,10))
        new_y_axis_str = [str(-i) for i in new_y_axis]
        new_y_axis = [i*1000 for i in new_y_axis]

    elif type_chargement == 'Déplacement':
        new_y_axis = list(range(int(limites_y[0]),int(limites_y[1])+1,10))
        new_y_axis_str = [str(i) for i in new_y_axis]
        new_y_axis = [i for i in new_y_axis]
        

    else:
        new_y_axis = list(range(int(limites_y[0]/1000),int(limites_y[1]/1000)+1))
        new_y_axis_str = [str(-i) for i in new_y_axis]
        new_y_axis = [i*1000 for i in new_y_axis]

    axes.set_yticks(new_y_axis)
    axes.yaxis.set_ticklabels(new_y_axis_str,fontsize = 8)


    # trace les piles
    for pile in liste_piles:
        plt.plot([pile,pile],[limites_y[0],0],'go--',linewidth =2,markersize = 5,color = "green")

    for pile in liste_piles_centrales:
        plt.plot([pile,pile],[limites_y[0],0],'go--',linewidth =2,markersize = 5,color = "purple")

    plt.plot(limites_x,[0,0],linewidth = 1, color = "black")

    # les opération de traçage modifient la zone de tracé initiale, elle est remise ici
    axes.set_xlim(limites_x[0],limites_x[1])
    axes.set_ylim(bottom = limites_y[0],top = limites_y[1])
    plt.title(title)

    plt.savefig(title.replace(" ","_"),dpi = 150)


###########################################################
# Modifier les deux listes du dessous et lancer le script
###########################################################

liste_files = ["Rep-0FleauGauche.xls","Rep-1FleauDroit.xls","Rep-2ClavageFleau.xls","Rep-3PontPoussee.xls","Rep-Avant_Prest_Ext.xls","Rep-4_1ClavagePousse.xls","Rep-5_superstructure.xls","Rep-8_combinaison2.xls","Rep-8_combinaison3.xls","Rep-8_combinaison4.xls","Rep-8_combinaisonTOT.xls","Rep-8_combinaisTOT_C.xls","Rep-8_combinaisoTOTV.xls","Rep-8_combinaisoTOTd.xls","Rep-SW_Fleaux.xls","Rep-SW_Fleaux_M.xls","Rep-PREST_Fleaux.xls","Rep-PREST_Eclisse.xls","Rep-SW_PontPousse_M.xls","Rep-SW_PontPousse.xls","Rep-PREST_EclissePP.xls","Rep-PRESTM_CONTI.xls","Rep-PREST_CONTI.xls","Rep-Superstructure.xls","Rep-superstructure_M.xls","Rep-6_traffic_seul_M.xls","Rep-6_traffic_seul.xls","Rep-6_trafficseulmax.xls","Rep-dT_Grad.xls","Rep-dT_uni.xls"]
Title_file = ["0 Fléau gauche construction","1 Fléau droite construction","2 Clavage des deux ","3 Construction du pont poussé","4 Clavage des ponts poussés","5 Pose des cables de continuité","6 Pose des superstructures","7 Combinaison ELS UDL","8 Combinaison ELS TS","9 Combinaison ELS Thermique","10 Enveloppe ELS traction","11 Enveloppe ELS compression","12 Enveloppe effort tranchant","13 Enveloppe déplacement","LC1 Stress Poids propre des fléaux ","LC1 Moment Poids propre des fléaux ","LC2 Stress Precontrainte fleaux","LC3 Stress Precontrainte eclisse","LC4 Moment SW PontPousse","LC4 Stress SW PontPousse","LC4 Stress Precontrainte PontPousse","LC5 Moment Precontrainte continuité","LC5 Stress Precontrainte continuité","LC6 Stress Superstructure","LC6 Moment Superstructure","LC7 Moment du aux charges de traffic","LC7 Stress Traffic Traction","LC7 Stress Traffic Compression","LC8 Stress Gradient Thermique","LC9 Stress Thermique Uni"]

for i,file_name in enumerate(liste_files):
    print(file_name,Title_file[i])
    save_graph(file_name=file_name,title=Title_file[i])
