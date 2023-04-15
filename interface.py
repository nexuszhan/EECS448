from tkinter import *
from tkinter import ttk
from functools import partial
import os

from SVM_Predictor.SVM_Predictor import tokenize
from SVM_Predictor.SVM_Predictor import SVMpredict
from Model_Final.RNN_Predictor import *

SHOW_POST_NUM = 5
roll_num = 0

text_size = {"width":550, "height":75}
text_pos = {"x":150, "y":120, "gap":80}
delete_pos = {"x":835, "y":120, "gap":80}
edit_pos = {"x":750, "y":120, "gap":80}
msg_pos= {"x":400, "y":550}
try_again_pos = {"x":420, "y":580}
exit_pos = {"x":430, "y":610}
post_entry_pos = {"x":165, "y":85}
add_post_btn_pos = {"x":750, "y":85}
submit_post_btn_pos = {"x":425, "y":550}
roll_up_post_btn_pos = {"x":700, "y":200}
roll_down_post_btn_pos = {"x":700, "y":360}
comboxlist_pos = {"x":60, "y":85}

highlight_words = []
attributions = []
sentences = []
model_name = "SVM"
submitted = False

# Frame
window = Tk()
window.title("MindReader")
window.geometry("950x650")
defaultbg = window.cget('bg')

posts = []
post_text_vars = [Text(window,bg=defaultbg,font=14) for i in range(SHOW_POST_NUM)]
# Text entry
post_entry = Entry(window, width=60)
post_entry.place(x=post_entry_pos["x"], y=post_entry_pos["y"])

# Label for prompt message
msg = Label(window, text="Please wait for the result.")

def helper(i):
    global roll_num
    global model_name
    global submitted
    global attributions
    global sentences
    global highlight_words

    post_index = max(0,len(posts)-SHOW_POST_NUM - roll_num)+i
    target_post = posts[post_index]
    show = "Post"+str(post_index+1)+": "+target_post
    post_text_vars[i].delete("1.0",END)
    post_text_vars[i].insert(END,show)
    post_text_vars[i].place(x=text_pos["x"],y=i*text_pos["gap"]+text_pos["y"],
                            width=text_size["width"],height=text_size["height"])
    
    if submitted:
        if model_name == "SVM":
            for highlight_word in highlight_words:
                start_index = 0
                while True:
                    index = target_post.find(highlight_word, start_index)
                    if index == -1:
                        break
                    
                    start = "1."+str(index+6+len(str(post_index+1)))
                    end = "1."+str(index+len(highlight_word)+6+len(str(post_index+1)))
                    post_text_vars[i].tag_add(highlight_word+str(start_index), start, end)
                    post_text_vars[i].tag_config(highlight_word+str(start_index), foreground="red")

                    start_index = index + 1
        elif model_name == "RNN":
            sentence = sentences[post_index]
            attribution = attributions[post_index]
            start_index = 6 + len(str(post_index+1)) 
            end_index = -1
            for j in range(1, len(sentence)-1):
                word = sentence[j]
                end_index = start_index + len(word)
                start = "1."+str(start_index)
                end = "1."+str(end_index)

                bg_color = defaultbg
                if attribution[j] >= 0.6:
                    bg_color = "red"
                elif attribution[j] >= 0.4:
                    bg_color = "yellow"
                elif attribution[j] >= 0.2:
                    bg_color = "light yellow"
                elif attribution[j] <= -0.6:
                    bg_color = "blue"
                elif attribution[j] <= -0.4:
                    bg_color = "teal"
                elif attribution[j] <= -0.2:
                    bg_color = "light blue"

                post_text_vars[i].tag_add(word+str(j), start, end)
                post_text_vars[i].tag_config(word+str(j), background = bg_color)

                start_index = end_index
            
    post_text_vars[i].config(state="disabled")

# Post button
def add_post_clicked():
    global roll_num
    res = post_entry.get()
    if len(res) != 0:
        posts.append(res)
        post_entry.delete(0,len(res))
        
        for i in range(min(len(posts),SHOW_POST_NUM)):
            post_text_vars[i].config(state="normal")

        for i in range(min(len(posts),SHOW_POST_NUM)):
            helper(i)
            
            edit_post_btns[i].place(x=edit_pos["x"],y=edit_pos["y"]+i*edit_pos["gap"])
            delete_post_btns[i].place(x=delete_pos["x"],y=delete_pos["y"]+i*delete_pos["gap"])
        
        roll_num = 0
        submit_post_btn.place(x=submit_post_btn_pos["x"], y=submit_post_btn_pos["y"])
        roll_up_post_btn.place(x=roll_up_post_btn_pos["x"], y=roll_up_post_btn_pos["y"])
        roll_down_post_btn.place(x=roll_down_post_btn_pos["x"], y=roll_down_post_btn_pos["y"])

def delete_post_clicked(btn_index):
    global roll_num
    for i in range(min(len(posts),SHOW_POST_NUM)):
        post_text_vars[i].config(state="normal")

    del posts[max(0, len(posts)-SHOW_POST_NUM- roll_num) + btn_index] #!!!
    if len(posts) < SHOW_POST_NUM:
        for i in range(len(posts)):
            helper(i)
        post_text_vars[len(posts)].delete("1.0",END)
        post_text_vars[len(posts)].place_forget()
        post_text_vars[len(posts)].config(state="disabled")
        delete_post_btns[len(posts)].place_forget()
        edit_post_btns[len(posts)].place_forget()

    elif btn_index > len(posts)-SHOW_POST_NUM-roll_num:
        if roll_num > 0:
            roll_num -= 1
        for i in range(min(len(posts),SHOW_POST_NUM)):
            helper(i)
    else:
        for i in range(min(len(posts),SHOW_POST_NUM)):
            helper(i)
  
    # mute submit button if all posts are deleted
    if len(posts) == 0:
        submit_post_btn.place_forget()
        roll_up_post_btn.place_forget()
        roll_down_post_btn.place_forget()
        
def submit_post_clicked():
    global roll_num
    global highlight_words
    global attributions
    global sentences
    global model_name
    global submitted
    # make some buttons invisible
    post_entry.place_forget()
    submit_post_btn.place_forget()
    add_post_btn.place_forget()
    comboxlist.place_forget()
    for i in range(SHOW_POST_NUM):
        delete_post_btns[i].place_forget()
        edit_post_btns[i].place_forget()
    # generate output
    msg.config(text = "Please wait for the result.")
    msg.place(x=msg_pos["x"],y=msg_pos["y"])
    
    if model_name == "SVM":
        antiwork, words = SVMpredict(posts)
        if antiwork:
            msg.config(text = "The user is likely to be antiwork!") 
        else:
            msg.config(text = "The user seems not to be antiwork!")
        highlight_words = list(set(words))
    elif model_name == "RNN":
        attributions, sentences, pred_class = RNNpredict().run_model(posts)
        if pred_class:
            msg.config(text = "The user seems not to be antiwork!")
        else:
            msg.config(text = "The user is likely to be antiwork!") 
    
    submitted = True
    for i in range(min(len(posts),SHOW_POST_NUM)):
        post_text_vars[i].config(state="normal")
    for i in range(min(len(posts),SHOW_POST_NUM)):
        helper(i)

    try_again_btn.place(x=try_again_pos["x"], y=try_again_pos["y"])
    exit_btn.place(x=exit_pos["x"], y=exit_pos["y"])

def roll_up_clicked():
    global roll_num
    if len(posts) > SHOW_POST_NUM and roll_num < (len(posts)-SHOW_POST_NUM):
        roll_num += 1
        for i in range(min(len(posts),SHOW_POST_NUM)):
            post_text_vars[i].config(state="normal")
        for i in range(min(len(posts),SHOW_POST_NUM)):
            helper(i)

def roll_down_clicked():
    global roll_num
    if len(posts) > SHOW_POST_NUM and roll_num > 0:
        roll_num -= 1
        for i in range(min(len(posts),SHOW_POST_NUM)):
            post_text_vars[i].config(state="normal")
        for i in range(min(len(posts),SHOW_POST_NUM)):
            helper(i)

def edit_clicked(btn_index):
    post_text_vars[btn_index].config(state="normal")
    edit_post_btns[btn_index].place_forget()
    confirm_edit_btns[btn_index].place(x=edit_pos["x"], y=edit_pos["y"]+btn_index*edit_pos["gap"])
    
def confirm_clicked(btn_index):
    global roll_num
    post_index = max(0,len(posts)-SHOW_POST_NUM - roll_num) + btn_index
    tmp = "1." + str(6+len(str(post_index+1)))
    posts[post_index] = post_text_vars[btn_index].get(tmp,"end")
    
    confirm_edit_btns[btn_index].place_forget()
    edit_post_btns[btn_index].place(x=edit_pos["x"], y=edit_pos["y"]+btn_index*edit_pos["gap"])

    post_text_vars[btn_index].config(state="disabled")

def try_again_clicked():
    global roll_num
    global attributions
    global sentences
    global highlight_words
    global submitted
    global model_name
    msg.place_forget()
    try_again_btn.place_forget()
    exit_btn.place_forget()
    #roll_up_post_btn.place(x=roll_up_post_btn_pos["x"], y=roll_up_post_btn_pos["y"])
    #roll_down_post_btn.place(x=roll_down_post_btn_pos["x"], y=roll_down_post_btn_pos["y"])
    roll_up_post_btn.place_forget()
    roll_down_post_btn.place_forget()

    add_post_btn.place(x=add_post_btn_pos["x"], y=add_post_btn_pos["y"])
    post_entry.place(x=post_entry_pos["x"], y=post_entry_pos["y"])
    comboxlist.place(x=comboxlist_pos["x"], y=comboxlist_pos["y"])
    comboxlist.current(0)
    model_name = "SVM"
        
    for i in range(min(len(posts),SHOW_POST_NUM)):
        post_text_vars[i].config(state="normal")
        post_text_vars[i].delete("1.0","end")
        post_text_vars[i].place_forget()
        post_text_vars[i].config(state="disabled")
    posts.clear()
    highlight_words.clear()
    attributions.clear()
    sentences.clear()
    submitted = False
    roll_num = 0

def exit_clicked():
    window.destroy()

def select_model(*args):
    global model_name
    model_name = comboxlist.get()

add_post_btn = Button(window, text = "Add", command=add_post_clicked)
add_post_btn.place(x=add_post_btn_pos["x"], y=add_post_btn_pos["y"])

delete_post_btns = []
for i in range(SHOW_POST_NUM):
    delete_post_btns.append(Button(window, text = "Delete", command=partial(delete_post_clicked,i)))

submit_post_btn = Button(window, text = "Submit",
                 fg="red", command=submit_post_clicked)

# roll up
roll_up_post_btn = Button(window, text = "⬆️", command=roll_up_clicked)
#roll_up_post_btn.place(x=roll_up_post_btn_pos["x"], y=roll_up_post_btn_pos["y"])

# roll down
roll_down_post_btn = Button(window, text = "⬇️", command=roll_down_clicked)
#roll_down_post_btn.place(x=roll_down_post_btn_pos["x"], y=roll_down_post_btn_pos["y"])

# edit post
edit_post_btns = []
for i in range(SHOW_POST_NUM):
    edit_post_btns.append(Button(window, text = "Edit", command=partial(edit_clicked,i)))
confirm_edit_btns = []
for i in range(SHOW_POST_NUM):
    confirm_edit_btns.append(Button(window, text = "Confirm", command=partial(confirm_clicked,i)))

try_again_btn = Button(window, text = "Try again", command=try_again_clicked)

# exit
exit_btn = Button(window, text="Exit", fg="red", command=exit_clicked)

# cobobox
comvalue = StringVar()
comboxlist = ttk.Combobox(window,textvariable=comvalue, width=7) #初始化
comboxlist["values"]=("SVM","RNN")
comboxlist.current(0)
comboxlist.bind("<<ComboboxSelected>>", select_model)
comboxlist.place(x=comboxlist_pos["x"], y=comboxlist_pos["y"])

window.mainloop()
