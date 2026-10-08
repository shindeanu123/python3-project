import tkinter as tk
from tkinter import messagebox
import random
import database
class QuizVerse:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizVerse")
        self.root.geometry("1280x760")
        self.root.minsize(1000, 650)
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass
        self.bg = "#EAF1FF"
        self.navy = "#102B66"
        self.purple = "#615BFF"
        self.text = "#18346D"
        self.muted = "#7788B5"
        self.green = "#16A34A"
        self.red = "#EF4444"
        self.name = ""
        self.category = ""
        self.question_list = []
        self.current_question = 0
        self.user_answers = {}
        self.total_time = 600
        self.time_left = self.total_time
        self.timer_id = None
        self.selected_answer = tk.StringVar()

        # Create tables (and load questions.py into the DB the first time)
        database.init_db()
        self.show_home()

    def clear_screen(self, keep_timer=False):
        if self.timer_id and not keep_timer:
            try:
                self.root.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def round_rect(self, c, x1, y1, x2, y2, r=22, **kw):
        r = min(r, (x2-x1)/2, (y2-y1)/2)
        p = [x1+r,y1,x1+r,y1,x2-r,y1,x2-r,y1,x2,y1,
             x2,y1+r,x2,y1+r,x2,y2-r,x2,y2-r,x2,y2,
             x2-r,y2,x2-r,y2,x1+r,y2,x1+r,y2,x1,y2,
             x1,y2-r,x1,y2-r,x1,y1+r,x1,y1+r,x1,y1]
        return c.create_polygon(p, smooth=True, splinesteps=24, **kw)

    def decorations(self, c, w, h):
        c.configure(bg=self.bg)
        c.create_oval(-120,-140,300,250,fill="#DCE8FF",outline="")
        c.create_oval(w-250,-120,w+160,300,fill="#D9D7FF",outline="")
        c.create_oval(-120,h-190,290,h+150,fill="#D9E6FF",outline="")
        c.create_oval(w-200,h-190,w+150,h+150,fill="#D5D3FF",outline="")
        for x,y,r,col in [(90,140,5,"#8EBBFF"),(155,205,7,"#B8B8FF"),
                          (w-120,110,6,"#9DDFFF"),(w-75,330,9,"#9BAEFF"),
                          (w-220,h-100,6,"#B7A5FF"),(190,h-90,7,"#B5A6FF")]:
            c.create_oval(x-r,y-r,x+r,y+r,fill=col,outline="")
        c.create_line(0,260,70,220,120,228,180,180,220,130,
                      fill="#A8C9FF",width=3,smooth=True,dash=(5,4))
        c.create_line(w-180,260,w-120,300,w-60,275,w,300,
                      fill="#A8C9FF",width=3,smooth=True,dash=(5,4))

    # ------------------------------------------------------------------ HOME
    def show_home(self):
        self.clear_screen()
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill="both", expand=True)
        left = tk.Frame(main, bg=self.navy, width=390)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left,text="Q",font=("Arial",48,"bold"),bg=self.purple,
                 fg="white",width=2).pack(pady=(100,22))
        tk.Label(left,text="QUIZVERSE",font=("Arial",30,"bold"),
                 bg=self.navy,fg="white").pack()
        tk.Label(left,text="Learn  ·  Practice  ·  Improve",font=("Arial",13),
                 bg=self.navy,fg="#C8D8FF").pack(pady=15)
        tk.Label(left,text="🧠  Multiple Categories\n\n⏱  10 Minute Challenge\n\n🏆  Track Your Score",
                 font=("Segoe UI Emoji",14),bg=self.navy,fg="#E4ECFF",
                 justify="left").pack(pady=45)
        right=tk.Frame(main,bg=self.bg)
        right.pack(side="left",fill="both",expand=True)
        tk.Label(right,text="Welcome to QuizVerse 👋",font=("Arial",30,"bold"),
                 bg=self.bg,fg=self.text).pack(pady=(115,10))
        tk.Label(right,text="Enter your name to start your quiz",font=("Arial",14),
                 bg=self.bg,fg=self.muted).pack(pady=5)
        card=tk.Frame(right,bg="white",padx=42,pady=32,
                      highlightbackground="#D7E2F5",highlightthickness=1)
        card.pack(pady=28)
        tk.Label(card,text="Your Name",font=("Arial",13,"bold"),
                 bg="white",fg=self.text).pack(anchor="w")
        self.name_entry=tk.Entry(card,font=("Arial",15),width=29,bd=0,
                                 bg="#F1F5FC",fg=self.text)
        self.name_entry.pack(pady=12,ipady=10)
        self.name_entry.focus()
        self.name_entry.bind("<Return>", lambda e: self.start_quiz())
        tk.Button(card,text="START QUIZ  →",font=("Arial",13,"bold"),
                  bg=self.purple,fg="white",bd=0,width=24,pady=12,
                  cursor="hand2",command=self.start_quiz).pack(pady=(12,4))
        tk.Button(right,text="Exit",font=("Arial",11),bg=self.bg,fg=self.muted,
                  bd=0,cursor="hand2",command=self.root.destroy).pack()

    def start_quiz(self):
        self.name=self.name_entry.get().strip()
        if not self.name:
            messagebox.showwarning("Name Required","Please enter your name.")
            return
        try:
            database.get_or_create_user(self.name)   # register / recognise the player
        except Exception as error:
            print("Could not register user:", error)
        self.show_categories()

    # ------------------------------------------------------------ CATEGORIES
    def get_ordered_categories(self):
        defaults=["Python","Java","C","DSA","Aptitude"]
        all_cats=database.get_categories()
        return [x for x in defaults if x in all_cats]+[x for x in all_cats if x not in defaults]

    def show_categories(self):
        self.clear_screen()
        page=tk.Frame(self.root,bg=self.bg)
        page.pack(fill="both",expand=True)
        header=tk.Frame(page,bg=self.navy,height=66)
        header.pack(fill="x")
        header.pack_propagate(False)
        brand=tk.Frame(header,bg=self.navy)
        brand.pack(side="left",padx=28)
        tk.Label(brand,text="◉",font=("Arial",28,"bold"),fg="#8C8BFF",
                 bg=self.navy).pack(side="left")
        tk.Label(brand,text="QUIZVERSE",font=("Arial",21,"bold"),
                 fg="white",bg=self.navy).pack(side="left",padx=(8,18))
        tk.Frame(brand,bg="#6379AA",width=2,height=30).pack(side="left",padx=5)
        tk.Label(brand,text="Learn  ·  Practice  ·  Improve",font=("Arial",12),
                 fg="#D5E2FF",bg=self.navy).pack(side="left",padx=14)
        tk.Label(header,text=f"👤  {self.name}",font=("Arial",12,"bold"),
                 fg="white",bg=self.navy).pack(side="right",padx=32)
        tk.Button(header,text="🏆 Leaderboard",font=("Arial",11,"bold"),bg=self.purple,
                  fg="white",bd=0,padx=14,pady=6,cursor="hand2",
                  command=lambda: self.show_leaderboard(None)).pack(side="right",padx=6)

        body=tk.Frame(page,bg=self.bg)
        body.pack(fill="both",expand=True)
        c=tk.Canvas(body,bg=self.bg,highlightthickness=0)
        c.pack(fill="both",expand=True)
        c.update_idletasks()
        w=max(c.winfo_width(),1000); h=max(c.winfo_height(),580)
        self.decorations(c,w,h)

        # Decorative books and graduation cap
        self.round_rect(c,-25,h-205,185,h-150,13,fill="#4059E8",outline="")
        self.round_rect(c,-20,h-155,205,h-100,13,fill="#9D4DFF",outline="")
        self.round_rect(c,-10,h-105,220,h-48,13,fill="#FFB02E",outline="")
        for yy,col in [(h-188,"#B9D4FF"),(h-138,"#E5C8FF"),(h-88,"#FFE1A3")]:
            c.create_line(15,yy,125,yy,fill=col,width=3)
        c.create_polygon(20,h-245,100,h-275,180,h-245,100,h-218,
                         fill="#1C3D9A",outline="")
        c.create_line(100,h-244,100,h-208,fill="#FBBF24",width=3)
        c.create_oval(93,h-212,107,h-198,fill="#FBBF24",outline="")
        # Laptop illustration
        self.round_rect(c,w-185,h-190,w+35,h-65,18,fill="#5A4BE8",
                        outline="#4036B8",width=3)
        self.round_rect(c,w-168,h-174,w+16,h-84,10,fill="#2147B8",outline="")
        c.create_text(w-76,h-130,text="</>",font=("Arial",27,"bold"),fill="#D9F3FF")
        c.create_polygon(w-198,h-63,w+48,h-63,w+18,h-43,w-168,h-43,
                         fill="#8E9DFF",outline="")

        pw=min(820,w-300); pw=max(pw,690)
        ph=min(535,h-45); ph=max(ph,500)
        x1=(w-pw)/2; y1=max(18,(h-ph)/2); x2=x1+pw; y2=y1+ph
        self.round_rect(c,x1+4,y1+9,x2+4,y2+9,28,fill="#D5DEFF",outline="")
        self.round_rect(c,x1,y1,x2,y2,28,fill="#FFFFFF",outline="")
        c.create_text(w/2-200,y1+38,text="🚀",font=("Segoe UI Emoji",30),fill=self.text)
        c.create_text(w/2+20,y1+38,text="Select a Subject",
                      font=("Arial",29,"bold"),fill=self.text)
        c.create_text(w/2,y1+78,text="Choose a category and test your knowledge",
                      font=("Arial",12,"bold"),fill="#7D8DB7")
        c.create_line(w/2-255,y1+78,w/2-190,y1+78,fill="#D3D9FF",width=2)
        c.create_line(w/2+190,y1+78,w/2+255,y1+78,fill="#D3D9FF",width=2)

        categories=self.get_ordered_categories()
        styles={
            "Python":("#30B8F5","#0875F8","🐍","#0055B9"),
            "Java":("#FFC62E","#FF6245","☕","#D94700"),
            "C":("#9294FF","#4432E8","C","#3025C7"),
            "DSA":("#D43CF5","#7928F7","♧","#6515D8"),
            "Aptitude":("#6DE3AC","#00AFA0","🧠","#008A77")}
        cw,ch,gx,gy=195,178,18,18
        sx=w/2-(3*cw+2*gx)/2
        first_y=y1+122
        for i,cat in enumerate(categories):
            row,col=divmod(i,3)
            cx=(w/2-(2*cw+gx)/2+col*(cw+gx)) if row==1 else sx+col*(cw+gx)
            cy=first_y+row*(ch+gy)
            top,bottom,icon,bcol=styles.get(cat,("#5CB8FF","#4655E8","📚","#303FC8"))
            self.round_rect(c,cx+2,cy+7,cx+cw+2,cy+ch+7,22,fill="#DCE4FF",outline="")
            self.round_rect(c,cx,cy,cx+cw,cy+ch,22,fill=bottom,outline="#FFFFFF",width=2)
            self.round_rect(c,cx+2,cy+2,cx+cw-2,cy+ch-3,21,fill=top,outline="")
            c.create_oval(cx+cw-55,cy+72,cx+cw+15,cy+142,fill=bottom,outline="")
            c.create_text(cx+cw-34,cy+34,text="‹/›",font=("Arial",20,"bold"),fill="#FFFFFF")
            c.create_text(cx+cw/2,cy+46,text=icon,font=("Segoe UI Emoji",38,"bold"),fill="white")
            c.create_text(cx+cw/2,cy+91,text=cat,font=("Arial",17,"bold"),fill="white")
            self.round_rect(c,cx+42,cy+117,cx+cw-42,cy+151,18,fill=bcol,outline="")
            c.create_text(cx+cw/2,cy+134,text="START  →",font=("Arial",10,"bold"),fill="white")
            tag=f"category_{i}"
            for item in c.find_overlapping(cx,cy,cx+cw,cy+ch):
                c.addtag_withtag(tag,item)
            c.tag_bind(tag,"<Button-1>",lambda event,chosen=cat:self.start_category(chosen))
            c.tag_bind(tag,"<Enter>",lambda event:c.configure(cursor="hand2"))
            c.tag_bind(tag,"<Leave>",lambda event:c.configure(cursor=""))
        c.create_text(w-125,145,text="Small Steps\nBig Dreams",
                      font=("Segoe Script",21,"italic","bold"),fill="#173B80",justify="center")
        c.create_line(w-195,192,w-65,168,fill="#173B80",width=3)

    # ----------------------------------------------------------- LEADERBOARD
    def show_leaderboard(self, category=None):
        self.clear_screen()
        categories=self.get_ordered_categories()
        if not categories:
            messagebox.showinfo("Leaderboard","No categories found.")
            self.show_categories(); return
        if category not in categories:
            category=self.category if self.category in categories else categories[0]

        page=tk.Frame(self.root,bg=self.bg); page.pack(fill="both",expand=True)
        header=tk.Frame(page,bg=self.navy,height=66)
        header.pack(fill="x"); header.pack_propagate(False)
        tk.Label(header,text="◉  QUIZVERSE  ·  LEADERBOARD",font=("Arial",20,"bold"),
                 fg="white",bg=self.navy).pack(side="left",padx=28)
        tk.Button(header,text="←  Back",font=("Arial",11,"bold"),bg=self.purple,fg="white",
                  bd=0,padx=16,pady=6,cursor="hand2",
                  command=self.show_categories).pack(side="right",padx=28)

        # Category tabs
        tabs=tk.Frame(page,bg=self.bg); tabs.pack(pady=(24,10))
        for cat in categories:
            active=(cat==category)
            tk.Button(tabs,text=cat,font=("Arial",12,"bold"),
                      bg=self.purple if active else "white",
                      fg="white" if active else self.text,
                      bd=0,padx=22,pady=8,cursor="hand2",
                      command=lambda ct=cat:self.show_leaderboard(ct)).pack(side="left",padx=5)

        card=tk.Frame(page,bg="white",padx=30,pady=22,
                      highlightbackground="#D7E2F5",highlightthickness=1)
        card.pack(pady=10)
        tk.Label(card,text=f"🏆  Top Players — {category}",font=("Arial",18,"bold"),
                 bg="white",fg=self.text).grid(row=0,column=0,columnspan=5,pady=(0,14))

        heads=["Rank","Player","Score","Percent","Date"]
        widths=[7,24,10,10,18]
        for i,(hd,wd) in enumerate(zip(heads,widths)):
            tk.Label(card,text=hd,font=("Arial",11,"bold"),bg="#EEF2FF",fg=self.text,
                     width=wd,pady=6).grid(row=1,column=i,padx=1,pady=1)

        rows=database.get_leaderboard(category,10)
        if not rows:
            tk.Label(card,text="No scores yet — be the first to play!",font=("Arial",13),
                     bg="white",fg=self.muted,pady=30).grid(row=2,column=0,columnspan=5)
        medals={1:"🥇",2:"🥈",3:"🥉"}
        for r,(pname,best,total,when) in enumerate(rows,start=1):
            pct=(best/total*100) if total else 0
            is_me=(pname==self.name)
            bgc="#FFF8DB" if is_me else ("#F8FAFF" if r%2 else "white")
            vals=[medals.get(r,str(r)),pname,f"{best} / {total}",f"{pct:.0f}%",(when or "")[:16]]
            for i,(v,wd) in enumerate(zip(vals,widths)):
                tk.Label(card,text=v,font=("Arial",11,"bold" if is_me else "normal"),
                         bg=bgc,fg=self.text,width=wd,pady=6).grid(row=r+1,column=i,padx=1,pady=1)

        # Player's recent history
        history=database.get_user_history(self.name,5) if self.name else []
        if history:
            tk.Label(page,text=f"Your recent attempts, {self.name}",font=("Arial",12,"bold"),
                     bg=self.bg,fg=self.text).pack(pady=(14,4))
            for cat,score,total,when in history:
                tk.Label(page,text=f"{cat}:  {score}/{total}    ({(when or '')[:16]})",
                         font=("Arial",11),bg=self.bg,fg=self.muted).pack()

    # ------------------------------------------------------------------ QUIZ
    def start_category(self, category):
        self.category=category
        self.question_list=database.get_questions(category)
        if not self.question_list:
            messagebox.showwarning("No Questions",f"No questions found for {category} in the database.")
            return
        random.shuffle(self.question_list)
        self.current_question=0
        self.user_answers={}
        self.time_left=self.total_time
        if self.timer_id:
            try:
                self.root.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id=None
        self.show_question()
        self.update_timer()

    def show_question(self):
        self.clear_screen(keep_timer=True)
        if self.current_question>=len(self.question_list):
            self.show_result(); return
        main=tk.Frame(self.root,bg="#F0F4FF")
        main.pack(fill="both",expand=True)
        side=tk.Frame(main,bg=self.navy,width=225)
        side.pack(side="left",fill="y"); side.pack_propagate(False)
        tk.Label(side,text="◉ QUIZVERSE",font=("Arial",19,"bold"),fg="white",bg=self.navy).pack(pady=(25,12))
        tk.Label(side,text=self.category,font=("Arial",14,"bold"),fg="#AFC2FF",bg=self.navy).pack(pady=5)
        tk.Label(side,text="QUESTION PANEL",font=("Arial",10,"bold"),fg="#9FB1D9",bg=self.navy).pack(pady=(24,10))
        nums=tk.Frame(side,bg=self.navy); nums.pack(padx=12)
        for i in range(len(self.question_list)):
            col=self.purple if i==self.current_question else (self.green if i in self.user_answers else "#52648A")
            tk.Button(nums,text=str(i+1),font=("Arial",9,"bold"),bg=col,fg="white",bd=0,width=4,
                      cursor="hand2",command=lambda q=i:self.go_to_question(q)).grid(row=i//4,column=i%4,padx=3,pady=4)
        legend=tk.Frame(side,bg=self.navy); legend.pack(side="bottom",pady=24)
        for col,label in [(self.purple,"Current"),(self.green,"Attempted"),("#52648A","Not Attempted")]:
            row=tk.Frame(legend,bg=self.navy); row.pack(anchor="w",pady=3)
            tk.Label(row,text="  ",bg=col).pack(side="left",padx=6)
            tk.Label(row,text=label,font=("Arial",9),fg="#D8E2FA",bg=self.navy).pack(side="left")
        content=tk.Frame(main,bg="#F0F4FF"); content.pack(side="left",fill="both",expand=True)
        top=tk.Frame(content,bg="white",height=72); top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top,text=f"Question {self.current_question+1} of {len(self.question_list)}",
                 font=("Arial",15,"bold"),fg=self.text,bg="white").pack(side="left",padx=30)
        m,s=divmod(self.time_left,60)
        self.timer_label=tk.Label(top,text=f"{m:02d}:{s:02d}",font=("Arial",16,"bold"),
                                  fg=self.red,bg="#FFF0F0",padx=18,pady=7)
        self.timer_label.pack(side="right",padx=28)
        area=tk.Frame(content,bg="#F0F4FF",padx=45,pady=30); area.pack(fill="both",expand=True)
        card=tk.Frame(area,bg="white",padx=38,pady=30,highlightbackground="#DCE5F5",highlightthickness=1)
        card.pack(fill="both",expand=True)
        q=self.question_list[self.current_question]
        tk.Label(card,text=q["question"],font=("Arial",20,"bold"),fg=self.text,bg="white",
                 wraplength=850,justify="left").pack(anchor="w",pady=(8,22))
        self.selected_answer=tk.StringVar(value=self.user_answers.get(self.current_question,""))
        for option in q["options"]:
            f=tk.Frame(card,bg="#F5F8FF",padx=12,pady=7); f.pack(fill="x",pady=5)
            tk.Radiobutton(f,text=option,variable=self.selected_answer,value=option,font=("Arial",13),
                           fg="#263B68",bg="#F5F8FF",activebackground="#F5F8FF",
                           selectcolor="#DDE5FF",anchor="w",cursor="hand2").pack(fill="x")
        buttons=tk.Frame(card,bg="white"); buttons.pack(side="bottom",fill="x",pady=(20,0))
        tk.Button(buttons,text="←  Previous",font=("Arial",11,"bold"),bg="#E3EAF8",fg=self.text,bd=0,
                  width=14,pady=10,command=self.previous_question).pack(side="left")
        label="Submit Quiz  ✓" if self.current_question==len(self.question_list)-1 else "Next  →"
        tk.Button(buttons,text=label,font=("Arial",11,"bold"),bg=self.purple,fg="white",bd=0,
                  width=17,pady=10,command=self.next_question).pack(side="right")

    def save_current_answer(self):
        if self.selected_answer.get():
            self.user_answers[self.current_question]=self.selected_answer.get()

    def go_to_question(self, number):
        self.save_current_answer(); self.current_question=number; self.show_question()

    def previous_question(self):
        self.save_current_answer()
        if self.current_question>0:
            self.current_question-=1; self.show_question()

    def next_question(self):
        self.save_current_answer()
        if self.current_question==len(self.question_list)-1:
            if messagebox.askyesno("Submit Quiz","Are you sure you want to submit the quiz?"):
                self.show_result()
        else:
            self.current_question+=1; self.show_question()

    def update_timer(self):
        if not self.root.winfo_exists() or not hasattr(self,"timer_label") or not self.timer_label.winfo_exists():
            return
        m,s=divmod(self.time_left,60)
        self.timer_label.config(text=f"{m:02d}:{s:02d}",fg="#DC2626" if self.time_left<=60 else self.red,
                                bg="#FEE2E2" if self.time_left<=60 else "#FFF0F0")
        if self.time_left<=0:
            self.timer_id=None
            messagebox.showinfo("Time Over","Your 10 minute quiz time is over.")
            self.show_result(); return
        self.time_left-=1
        self.timer_id=self.root.after(1000,self.update_timer)

    # ---------------------------------------------------------------- RESULT
    def show_result(self):
        if self.timer_id:
            try: self.root.after_cancel(self.timer_id)
            except tk.TclError: pass
            self.timer_id=None
        if hasattr(self,"selected_answer") and self.selected_answer.get():
            self.user_answers[self.current_question]=self.selected_answer.get()
        self.clear_screen()
        total=len(self.question_list)
        score=sum(1 for i,q in enumerate(self.question_list) if self.user_answers.get(i)==q.get("answer"))
        attempted=len(self.user_answers); missed=total-attempted
        pct=score/total*100 if total else 0
        page=tk.Frame(self.root,bg=self.bg); page.pack(fill="both",expand=True)
        c=tk.Canvas(page,bg=self.bg,highlightthickness=0); c.pack(fill="both",expand=True)
        c.update_idletasks(); w=max(c.winfo_width(),1000); h=max(c.winfo_height(),600)
        self.decorations(c,w,h)
        c.create_rectangle(0,0,w,70,fill=self.navy,outline="")
        c.create_text(35,35,text="◉  QUIZVERSE",anchor="w",font=("Arial",22,"bold"),fill="white")
        c.create_text(w-35,35,text="RESULT",anchor="e",font=("Arial",12,"bold"),fill="#D5E0FF")
        self.round_rect(c,w/2-255,h/2-245,w/2+255,h/2+290,28,fill="white",outline="#DCE5F5",width=2)
        c.create_text(w/2,h/2-198,text="🎉  Quiz Completed!",font=("Arial",25,"bold"),fill=self.purple)
        c.create_text(w/2,h/2-158,text=f"Well done, {self.name}!",font=("Arial",16),fill=self.muted)
        c.create_text(w/2,h/2-126,text=f"Category: {self.category}",font=("Arial",12,"bold"),fill="#8585E8")
        c.create_text(w/2,h/2-62,text=f"{score} / {total}",font=("Arial",45,"bold"),fill=self.purple)
        c.create_text(w/2,h/2-20,text=f"{pct:.1f}% Score",font=("Arial",16,"bold"),fill=self.text)
        self.round_rect(c,w/2-190,h/2+12,w/2-10,h/2+82,12,fill="#F0FDF4",outline="#DCE5F5")
        c.create_text(w/2-100,h/2+34,text=str(attempted),font=("Arial",22,"bold"),fill=self.green)
        c.create_text(w/2-100,h/2+61,text="Attempted",font=("Arial",10),fill=self.muted)
        self.round_rect(c,w/2+10,h/2+12,w/2+190,h/2+82,12,fill="#FFF1F2",outline="#DCE5F5")
        c.create_text(w/2+100,h/2+34,text=str(missed),font=("Arial",22,"bold"),fill=self.red)
        c.create_text(w/2+100,h/2+61,text="Not Attempted",font=("Arial",10),fill=self.muted)
        again=tk.Button(page,text="PLAY AGAIN  ↻",font=("Arial",12,"bold"),bg=self.purple,fg="white",
                        bd=0,cursor="hand2",command=self.show_categories)
        c.create_window(w/2,h/2+128,window=again,width=205,height=42)
        board=tk.Button(page,text="🏆  LEADERBOARD",font=("Arial",11,"bold"),bg=self.navy,fg="white",
                        bd=0,cursor="hand2",command=lambda:self.show_leaderboard(self.category))
        c.create_window(w/2,h/2+182,window=board,width=205,height=38)
        exit_btn=tk.Button(page,text="EXIT",font=("Arial",10),bg="white",fg=self.muted,
                           bd=0,cursor="hand2",command=self.root.destroy)
        c.create_window(w/2,h/2+235,window=exit_btn,width=100,height=28)
        self.save_score(score)

    def save_score(self, score):
        try:
            database.save_result(self.name, self.category, score,
                                 len(self.question_list), len(self.user_answers))
        except Exception as error:
            print("Could not save score:", error)


if __name__=="__main__":
    root=tk.Tk()
    app=QuizVerse(root)
    root.mainloop()