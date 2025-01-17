import os
import glob
import random
#import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from PIL import ImageTk, Image
from pathlib import Path

#dossier_exam = "./QuestionChiens/"
dossier_exam = "./QuestionMamiferePrio/"
#dossier_exam = "./QuestionMamifere/"
#dossier_exam = "./QuestionOiseauxPrio/"
#dossier_exam = "./QuestionOiseaux/"
nombre_props = 5
largeur_props = 25
dimention_image = [500, 400]

class CQuestion:
    def __init__(self, filename, question, proposition):
        self.FileName = filename
        self.Question = question
        self.Proposition = proposition
        self.undone = 0
        self.success = 0
        self.fail = 0

    def get_pourcentage_of_success(self):
        total = self.success + self.fail
        if total == 0:
            pourc = 0
        else:
            pourc = round((100 * self.success) / total)
        return pourc

def random_list(list):
    if list != None:
        for i in range(len(list)):
            n_aleat = random.randint(0, len(list)-1)
            swap = list[n_aleat]
            list[n_aleat] = list[i]
            list[i] = swap

current_question = -1
nb_question_left = 0
nb_question_proba_left = 0
nb_question_correct = 0
nb_question_incorrect = 0
label_stat = ''
choix = None
canvas = None
current_photo = None
idImageQuestion = None
question_textbox = None
load_button = None
save_button = None
choix = list()
choixProps = {}
choixPropsGlob = {}
details = {}
repquest_champ_list = None
lb_values = None
lbl_cor = None
lbl_cors = None
repquest_var = None

def reset_list():
    global choix, choixProps, choixPropsGlob, repquest_champ_list, lb_values, repquest_var
    random_list(choix)
    repquest_champ_list.selection_clear(0, tk.END)
    repquest_champ_list.delete(0, tk.END)
    for c in choix:
        repquest_champ_list.insert(tk.END, c)
    repquest_champ_list.selection_clear(0, tk.END)
    for lb in lb_values:
        lb.selection_clear(0, tk.END)
        lb.delete(0, tk.END)
        lb.selection_clear(0, tk.END)
    repquest_var.set("")

def restore_score():
    global Questions, load_button
    file = "score.csv"
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as fichier:
            lignes = fichier.readlines()
        if len(lignes) > 1 and lignes[0].strip() == "file_name|success|fail|pourcentage":
            lignes = lignes[1:]
            for ln in lignes:
                sln = ln.split('|')
                if len(sln) == 4:
                    quest = next((q for q in Questions if q.FileName == sln[0]), None)
                    if quest != None:
                        quest.success = int(sln[1].strip())
                        quest.fail = int(sln[2].strip())
    load_button.config(state="disabled")


def store_score():
    global Questions, save_button
    file = "score.csv"
    lignes: list[str] = list()
    lignes.append("file_name|success|fail|pourcentage\n")
    for quest in Questions:
        lignes.append(quest.FileName + "|"
                      + str(quest.success) + "|"
                      + str(quest.fail) + "|"
                      + str(quest.get_pourcentage_of_success()) + "%\n")
    with open(file, 'w', encoding='utf-8') as fichier:
        fichier.writelines(lignes)
    save_button.config(state="disabled")
    load_button.config(state="disabled")

def load_question(file):
    if os.path.exists(file):
        nom = os.path.basename(file)
        index_nom = 0
        try:
            # Recherche de l'index du caractère
            index_nom = nom.index('[')
        except ValueError:
            try:
                # Recherche de l'index du caractère
                index_nom = nom.index('.')
            except ValueError:
                index_nom = len(nom)

        index_props_deb = index_nom + 1
        index_props_fin = len(nom) - len('.jpg') - 1

        while(index_nom > 0 and nom[index_nom-1].isdigit()):
            index_nom = index_nom-1

        strprop = nom[index_props_deb:index_props_fin]
        if len(strprop) > 0 and strprop[0] != '':
            props = strprop.split('][')
        else:
            props = []
        return CQuestion(file, nom[0:index_nom], props)
    else:
        return None

def load_questions():
    quest_files = glob.glob("**/*.jpg", recursive=True)
    questions = list()
    for file_name in quest_files:
        quest = load_question(file_name)
        if quest != None :
            questions.append(quest)
    return questions

# Create a validation button
def validate():
    update_question_with_answer(True)
    next_question()

# Create a validation button
def invalidate():
    update_question_with_answer(False)
    next_question()

def reset():
    global current_question, nb_question_left, nb_question_proba_left, nb_question_correct, nb_question_incorrect
    current_question = -1
    nb_question_left = 0
    nb_question_proba_left = 0
    nb_question_correct = 0
    nb_question_incorrect = 0
    label_stat.config(text = "")
    update_stat()

# Create a resetAllMode button
def reset_all_mode():
    global nb_question_left, nb_question_proba_left
    reset()
    for q in Questions:
        q.undone = 1
    nb_question_left = sum(1 for q in Questions if q.undone != 0)
    nb_question_proba_left = nb_question_left
    next_question()


# Create a resetOnlyFalseMode button
def reset_only_false_mode():
    global nb_question_left, nb_question_proba_left
    reset()
    for q in Questions:
        if q.success == 0:
            q.undone = 1
        else:
            q.undone = 0
    nb_question_left = sum(1 for q in Questions if q.undone != 0)
    nb_question_proba_left = nb_question_left
    next_question()

def reset_pc_false_mode():
    global nb_question_left, nb_question_proba_left
    reset()
    for q in Questions:
        if q.get_pourcentage_of_success() <= 70:
            q.undone = 1
        else:
            q.undone = 0
    nb_question_left = sum(1 for q in Questions if q.undone != 0)
    nb_question_proba_left = nb_question_left
    next_question()

def draw_question():
    global nb_question_left, nb_question_proba_left
    if nb_question_proba_left > 0:
        n_aleat = random.randint(1, nb_question_proba_left)
        qnumb = 0
        for q in Questions:
            n_aleat -= q.undone
            if n_aleat <= 0:
                return qnumb
            qnumb += 1
    else:
        return -1


def show_answer():
    global Questions, current_question, repquest_champ_list, lbl_cor, lbl_cors, lb_values
    if current_question >= 0:
        quest = Questions[current_question]
        question_textbox.config(state='normal')
        question_textbox.delete("0.0", "end")
        if quest.Question in details:
            det = details[quest.Question]
            for dl in det:
                question_textbox.insert("end", dl)
        question_textbox.config(state='disabled')

        lbl_cor.config(text=quest.Question)
        cursel = repquest_champ_list.curselection()
        if cursel and repquest_champ_list.get(cursel) == quest.Question:
            lbl_cor.config(fg="green")
        else:
            lbl_cor.config(fg="red")

        for i in range(0, min(len(lbl_cors), len(quest.Proposition))):
            lbl_cors[i].config(text=quest.Proposition[i])
            cursel = lb_values[i].curselection()
            if cursel and  lb_values[i].get(cursel) == quest.Proposition[i]:
                lbl_cors[i].config(fg="green")
            else:
                lbl_cors[i].config(fg="red")

        #update_question_with_answer()
        pass
        #i_cb = 0
        #for prop in Questions[current_question].Proposition:
        #    if prop[0:1] == '>':
        #        check_buttons[i_cb].config(fg="green")
        #    else:
        #        check_buttons[i_cb].config(fg="red")
        #    i_cb += 1


def show_question(_current_question):
    global canvas, current_photo, current_question, repquest_var, repquest_champ_list, lb_values, question_textbox
    current_question = _current_question
    question_textbox.config(state='normal')
    question_textbox.delete("0.0", "end")

    #Questions[current_question].random_propositions()

    lbl_cor.config(text="")
    for lb in lbl_cors:
        lb.config(text="")

    reset_list()

    if current_question < 0:
        question_textbox.insert("0.0", "Examen terminé !")
        canvas.itemconfig(idImageQuestion, image=None)
    else:
        quest = Questions[_current_question]
        if quest.Question in details:
            det = details[quest.Question]
            for dl in det:
                try:
                    idx = dl.index(':')
                    question_textbox.insert("end", dl[0:idx+1] + "\n")
                except:
                    question_textbox.insert("end", dl)

        current_image = Image.open(quest.FileName)
        dw = dimention_image[0] / current_image.size[0]
        dh = dimention_image[1] / current_image.size[1]
        d = min(dw, dh)
        nw = int(current_image.size[0] * d)
        nh = int(current_image.size[1] * d)
        current_image = current_image.resize((nw, nh),
                                             Image.NEAREST)
        current_photo = ImageTk.PhotoImage(current_image)
        canvas.itemconfig(idImageQuestion, image=current_photo)
        canvas.moveto(idImageQuestion, (dimention_image[0] - nw) / 2, (dimention_image[1] - nh) / 2)
        #repquest_champ_combo['values'] =
        #cut_q = Questions[current_question].FileName + "\n" + cut_question_text(Questions[current_question].Question)
        #chemin_image2 = Questions[current_question].FileName
        #image2 = PhotoImage(Image.open(chemin_image2))
        #question_textbox.configure(image=image2)
        #question_textbox.image = image2
        # question_textbox.image = image2
        #i_cb = 0
        #for prop in Questions[current_question].Proposition:
        #    check_buttons[i_cb].config(state='normal')
        #    if prop[0:1] == '>':
        #        check_buttons[i_cb].config(text=cut_proposition_text(prop[1:]))
        #    else:
        #        check_buttons[i_cb].config(text=cut_proposition_text(prop))
        #    i_cb += 1
    question_textbox.config(state='disabled')

def check_is_correct_Answer():
    global current_question, Questions, repquest_champ_list, lb_values
    if current_question >= 0:
        quest = Questions[current_question]
        if repquest_champ_list.curselection():
            if repquest_champ_list.get(repquest_champ_list.curselection()) != quest.Question:
                return False
        else:
            return False

        for i in range(min(len(quest.Proposition), len(lb_values))):
            if lb_values[i].size() > 0:
                cursel = lb_values[i].curselection()
                if not cursel or lb_values[i].get(cursel) != quest.Proposition[i]:
                    return False
        #i_cb = 0
        #for prop in :
        #    if prop[0:1] == '>':
        #        if cb_values[i_cb].get() == 0:
        #            return False
        #    else:
        #        if cb_values[i_cb].get() == 1:
        #            return False
        #    i_cb += 1
        return True
    else:
        return None

def update_stat():
    total = (nb_question_correct + nb_question_incorrect)
    if total == 0:
        total = 1
    pourc = round((100 * (nb_question_correct)) / total)
    label_stat.config(text=str(nb_question_correct) + " réponse correcte et " + str(
        nb_question_incorrect) + " réponse incorrecte soit " + str(pourc) + "%")

def update_question_with_answer(vld):
    global current_question, nb_question_correct, nb_question_incorrect, nb_question_left, nb_question_proba_left, save_button, load_button
    if current_question >= 0 and Questions[current_question].undone > 0:
        check = check_is_correct_Answer() and vld
        if check != None:
            nb_question_left -= 1
            nb_question_proba_left -= Questions[current_question].undone
            Questions[current_question].undone = 0
            if check == True:
                nb_question_correct += 1
                Questions[current_question].success += 1
            else:
                nb_question_incorrect += 1
                Questions[current_question].fail += 1
            update_stat()
            save_button.config(state="normal")
            load_button.config(state="disabled")


def next_question():
    show_question(draw_question())

def repquest_texte_modifie(*args):
    global repquest_var, repquest_champ_list
    valeur = repquest_var.get().upper()
    repquest_champ_list.delete(0, tk.END)
    if len(valeur) > 0:
        for v in choix:
            if valeur in v.upper():
                repquest_champ_list.insert(tk.END, v)
    else:
        for v in choix:
            repquest_champ_list.insert(tk.END, v)

def repquest_champ_listbox_on_select(event):
    global repquest_champ_list, repquest_var, lb_values, choixProps
    selected_value = repquest_champ_list.curselection()
    for lb in lb_values:
        lb.delete(0, tk.END)
    if selected_value:
    #    repquest_var.set(repquest_champ_list.get(selected_value))
        cp = choixProps[repquest_champ_list.get(selected_value)]
        if cp:
            for i in range(min(len(cp), len(lb_values))):
                random_list(cp[i])
                for p in cp[i]:
                    lb_values[i].insert(tk.END, p)

def _init_app():
    global canvas, current_photo, idImageQuestion, choix, repquest_champ_texte, repquest_champ_list, repquest_var, lb_values, question_textbox, label_stat, save_button, load_button, lbl_cor, lbl_cors
    app = tk.Tk()
    app.title("QCMExam")
    app.attributes('-fullscreen', False)

    width = app.winfo_screenwidth()
    height = app.winfo_screenheight()
    width = 1024
    height = 768
    app.geometry("%dx%d" % (width, height))
    app.resizable(width=False, height=False)

    # Create the up panel (frame)
    top_panel = tk.Frame(app)
    top_panel.pack(side='top', fill='x')
    resette_allmode_button = tk.Button(top_panel, text='Repasser tout', font=("Helvetica", 12), command=reset_all_mode)
    resette_allmode_button.pack(side='left', pady=10)
    resette_onlyfalsemode_button = tk.Button(top_panel, text='Repasser erreur', font=("Helvetica", 12), command=reset_only_false_mode)
    resette_onlyfalsemode_button.pack(side='left', pady=10)
    resette_pcfalsemode_button = tk.Button(top_panel, text='Repasser moins de 70%', font=("Helvetica", 12), command=reset_pc_false_mode)
    resette_pcfalsemode_button.pack(side='left', pady=10)
    save_button = tk.Button(top_panel, text='Sauvegarder', font=("Helvetica", 12), command=store_score)
    save_button.pack(side='right', pady=10)
    save_button.config(state="disabled")
    load_button = tk.Button(top_panel, text='Charger', font=("Helvetica", 12), command=restore_score)
    load_button.pack(side='right', pady=10)
    label_stat = tk.Label(top_panel, text="", font=("Helvetica", 12))
    label_stat.pack(side='right', pady=10)

    # Create a text box for the question
    #chmimg = 'C:\\Users\\gauthier.sornet\\PycharmProjects\\pythonProject\\QuestionsImages\\Faisane[femelle].jpg'
    #chmimg = "C:\\Users\\gauthier.sornet\\PycharmProjects\\pythonProject\\QuestionsImages\\pngegg.png"
    #chmimg = 'QuestionsImages\\Faisane[femelle].jpg'
    #image2 = PhotoImage(file = Image.open(chmimg))
    #question_textbox = tk.Label(app, height=12, image=image2)
    #question_textbox.pack(pady=10)
    #question_textbox.config(state='disabled')
    # chemin_image2 = 'chemin/vers/ton_image2.png'
    # image2 = PhotoImage(Image.open(chemin_image2))
    #question_textbox.configure(image=image2)
    #question_textbox.image = image2

    frameQuest = tk.Frame(app)
    frameQuest.pack(pady=10)
    # Créer un canvas pour afficher l'image
    canvas = tk.Canvas(frameQuest, width=dimention_image[0], height=dimention_image[1], bg='white')
    #canvas.pack(fill="both", expand=True, pady=10)
    canvas.grid(row=0, column=0)
    idImageQuestion = canvas.create_image(0, 0, image=None, anchor="nw", state='normal')

    question_textbox = tk.Text(frameQuest, width=70, height=25, background='white', font=("Helvetica", 10))
    question_textbox.grid(row=0, column=1)
    question_textbox.config(state='disabled')

    frameRep = tk.Frame(app)
    frameRep.pack(pady=20)

    lbl_cor = tk.Label(frameRep, text="")
    lbl_cor.grid(row=0, column=0)

    i = 2
    lbl_cors = [tk.Label(frameRep, text="") for _ in range(nombre_props)]
    for c in lbl_cors:
        c.grid(row=0, column=i)
        i = i+2

    # Créer la liste déroulante
    repquest_champ_list = tk.Listbox(frameRep, width=largeur_props, selectmode=tk.SINGLE, exportselection=False)
    for c in choix:
        repquest_champ_list.insert(tk.END, c)
    #repquest_champ_list.pack(pady=20)
    repquest_champ_list.grid(row=1, column=0)

    # Création d'une variable StringVar pour suivre le texte
    repquest_var = tk.StringVar()
    repquest_var.trace_add("write", repquest_texte_modifie)
    # Création du champ de texte Entry
    repquest_champ_texte = tk.Entry(frameRep, width=largeur_props, textvariable=repquest_var)
    #repquest_champ_texte.pack()
    repquest_champ_texte.grid(row=2, column=0)
    # Associer une fonction à l'événement de sélection
    repquest_champ_list.bind("<<ListboxSelect>>", repquest_champ_listbox_on_select)

    # Créer un ascenseur vertical
    scrollbar = tk.Scrollbar(frameRep, orient=tk.VERTICAL)
    scrollbar.grid(row=1, column=1, sticky="ns")
    # Lier l'ascenseur à la Listbox
    repquest_champ_list.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=repquest_champ_list.yview)

    # Create 5 check boxes for propositions
    #cb_values = [tk.IntVar() for _ in range(5)]
    #check_buttons = [tk.Checkbutton(app, text='', variable=cb_values[i], justify='left', anchor='w', font=("Helvetica", 16)) for i in range(5)]
    #for cb in check_buttons:
    #    cb.pack(padx=10, anchor='w')
    #    cb.config(state='disabled')
    #    cb.config(text="")

    i = 2
    lb_values = [tk.Listbox(frameRep, width=largeur_props, selectmode=tk.SINGLE, exportselection=False) for _ in range(nombre_props)]
    for lb in lb_values:
        lb.grid(row=1, column=i)
        i = i+1
        scrollbar = tk.Scrollbar(frameRep, orient=tk.VERTICAL)
        scrollbar.grid(row=1, column=i, sticky="ns")
        # Lier l'ascenseur à la Listbox
        lb.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lb.yview)
        i = i + 1

    # Create the bottom panel (frame)
    bottom_panel = tk.Frame(app)
    bottom_panel.pack(side='bottom', fill='x')
    showanswer_button = tk.Button(bottom_panel, text='Corriger', font=("Helvetica", 12), command=show_answer)
    showanswer_button.pack(side='left', pady=10)
    validation_button = tk.Button(bottom_panel, text='Valider', font=("Helvetica", 12), command=validate)
    validation_button.pack(side='left', pady=10)
    validation_button = tk.Button(bottom_panel, text='InValider', font=("Helvetica", 12), command=invalidate)
    validation_button.pack(side='left', pady=10)
    bottom_panel.place(relx=0.5, rely=0.95, anchor='center')

    return app

os.chdir(dossier_exam)
Questions = load_questions()
for quest in Questions:
    subdos = str(Path(quest.FileName).parent)
    if not quest.Question in details and os.path.exists(subdos + '\\' + quest.Question + ".txt"):
        with open(subdos + '\\' + quest.Question + ".txt", 'r', encoding='utf-8') as fichier:
            details[quest.Question] = fichier.readlines()
    if quest.Question in choix:
        proplst = choixProps[quest.Question]
    else:
        proplst = list()
        choixProps[quest.Question] = proplst
        choix.append(quest.Question)
    while len(proplst) < len(quest.Proposition):
        proplst.append(list())
    for i in range(0, len(quest.Proposition)):
        prop = quest.Proposition[i]
        if prop.startswith('!'):
            prop = prop[1:]
            quest.Proposition[i] = prop
            if not prop in proplst[i]:
                proplst[i].append(prop)
            if prop in choixPropsGlob:
                probGlob = choixPropsGlob[prop]
                for vp in proplst[i]:
                    if vp.startswith('!'):
                        bvp = vp[1:]
                    else:
                        bvp = vp
                    if not bvp in probGlob:
                        probGlob.append(bvp)
            else:
                probGlob = proplst[i]
                choixPropsGlob[prop] = probGlob
            random_list(probGlob)
            proplst[i] = probGlob
        else:
            if not prop in proplst[i]:
                proplst[i].append(prop)
                random_list(proplst[i])
random_list(choix)

if os.path.exists('globalprops.cfg'):
    with open('globalprops.cfg', 'r', encoding='utf-8') as fichier:
        gprops_ln = fichier.readlines()
        for ln in gprops_ln:
            if ln.endswith('\n'):
                ln = ln[0:-1]
            if ln.endswith('\r'):
                ln = ln[0:-1]
            if ln.endswith('\n'):
                ln = ln[0:-1]
            gprops_ln_sp = ln.split('|')
            for spprop in gprops_ln_sp:
                if spprop in choixPropsGlob:
                    lst = choixPropsGlob[spprop]
                    for spprop2 in gprops_ln_sp:
                        if not spprop2 in lst:
                            lst.append(spprop2)
                    random_list(lst)

app = _init_app()
reset_all_mode()
app.mainloop()