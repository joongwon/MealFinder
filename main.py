from tkinter import *
import tkinter.font
import csv
import datetime
import menu2image
from PIL import ImageTk
import crawl_meal
from tkinter import messagebox


# 사전에 저장한 code.csv 파일에서 학교 코드를 불러온다
def load_school_list():
    with open('code.csv', 'r') as f:
        reader = csv.reader(f)
        return [list(row) for row in reader]


# 학교 코드 튜플(학교이름, 지역, 코드)를 읽기좋게 만들어준다(지역 학교이름).
def school2str(s):
    return s[1] + ' ' + s[0]


# 주어진 인수에 따라 급식 정보를 크롤링한다. 크롤링에는 crawl_meal.crawl 함수를 사용한다.
# return format: {'조식':[['메뉴'], ['메뉴','닭고기, 소고기']], '중식':[]}
def get_menu(school_id, school_region, year, month, day):
    meal = crawl_meal.crawl(school_region, school_id, str(year), str(month), str(day))
    if not meal:
        return {}
    result = {}
    current_menu_title = ''
    current_menu = []
    for row in meal.split('\n'):
        if row[0] == '[':
            if current_menu:
                result[current_menu_title] = current_menu
                current_menu = []
            #print('tag:',row)
            current_menu_title = row[1:-1]
        else:
            s = ''
            while row[-1] == '.':
                s = '.'+s
                row = row[:-1]
                while row[-1].isdigit():
                    s = row[-1] + s
                    row = row[:-1]
            current_menu.append([row, crawl_meal.get_allergy_text(s)])
    result[current_menu_title] = current_menu
    return result


# draw_menu에서 그리는 그림들이 가비지컬렉팅 되는 것을 막기 위함.
imgs = []


# 메뉴(menu)를 canvas의 (x,0) ~ (x+width, infinite) 영역에 출력한다
# returns height of canvas
def draw_menu(canvas, x, width, title, menu):
    # 제목(예: 조식, 중식, 석식 등) 출력
    canvas.create_text(x+width/2, 20, text=title, font=bigfont)
    h = 40

    # 식단을 구글에서 크롤링한 그림과 함께 출력
    for i in range(len(menu)):
        me = menu[i]
        mm = me[0]  # 음식
        al = me[1]  # 알러지 표기
        # print(al)

        # 크롤링
        img = menu2image.find_menu_image(mm, width-10)
        img = ImageTk.PhotoImage(img)

        # 가비지 컬렉팅 방지
        imgs.append(img)

        # 사각형 안에 급식메뉴, 알러지목록, 사진 출력
        canvas.create_rectangle(x+2,h+2,x+width-2,h+img.height()+65, fill='white')
        canvas.create_text(x+width/2, h+12, text=mm, width=width-4)
        canvas.create_text(x+width/2, h+42, text=al, width=width-4, font=smallfont, fill='gray')
        canvas.create_image(x+5, h+62, image=img, anchor=NW)
        h += img.height()+67

    # 함수 외부에서 사용될 출력한 길이
    return h


class TheApp:
    def __init__(self, master):
        self.master = master
        self.school_list = load_school_list()

        # 앱이 실행되면 가장 먼저 학교 선택 창을 보여준다.
        self.school_choice()
        self.frame1.pack()

    # 학교 선택 창
    def school_choice(self):
        self.frame1 = Frame(self.master)

        self.entry2 = Entry(self.frame1)
        self.entry2.grid(row=0,column=0,columnspan=2)

        self.btn3 = Button(self.frame1, text='검색', command=self.on_btn3)
        self.btn3.grid(row=1,column=0,columnspan=2)

        self.label1 = Label(self.frame1, text='학교를 선택하세요')
        self.label1.grid(row=2,column=0,columnspan=2)

        self.lb1 = Listbox(self.frame1)
        self.lb1_list = self.school_list[:]
        for s in self.lb1_list:
            self.lb1.insert(END, school2str(s))
        self.lb1.config(width=40)
        self.lb1.grid(row=3,column=0)

        self.yscroll2 = Scrollbar(self.frame1, orient='vertical', command=self.lb1.yview)
        self.yscroll2.grid(row=3, column=1,sticky=N+S)

        self.btn1 = Button(self.frame1, text='확인', command=self.on_btn1)
        self.btn1.grid(row=4,column=0,columnspan=2)

    # 학교 선택 창 확인 버튼
    def on_btn1(self):
        sel = self.lb1.curselection()
        # 학교를 선택하고 확인 버튼을 누르면
        if sel:
            # 날짜 선택 창으로 넘어간다.
            self.school = self.lb1_list[sel[0]]
            self.date_choice()
            self.frame1.pack_forget()
            self.frame2.pack()
        else:
            # 학교를 선택하지 않으면 오류가 발생한다.
            messagebox.showerror('오류', '학교를 선택하십시오')

    # 학교 선택 창 검색 버튼
    def on_btn3(self):
        s = self.entry2.get()
        self.lb1_list = []
        self.lb1.delete(0, END)

        # 검색 키워드를 포함하는 모든 학교명을 보여준다.
        for i in self.school_list:
            if s in i[0]:
                self.lb1_list.append(i)
                self.lb1.insert(END, school2str(i))

    # 날짜 선택 창
    def date_choice(self):
        self.frame2 = Frame(self.master)

        self.label3 = Label(self.frame2, text='선택된 학교: ' + school2str(self.school))
        self.label3.grid(column=0, row=0, columnspan=2)

        self.label2 = Label(self.frame2, text='날짜를 입력하세요')
        self.label2.grid(column=0, row=1, columnspan=2)

        self.entry1 = Entry(self.frame2)
        self.entry1.grid(column=0, row=2)

        self.label5 = Label(self.frame2, text='년')
        self.label5.grid(column=1, row=2)

        self.entry2 = Entry(self.frame2)
        self.entry2.grid(column=0, row=3)

        self.label6 = Label(self.frame2, text='월')
        self.label6.grid(column=1, row=3)

        self.entry3 = Entry(self.frame2)
        self.entry3.grid(column=0, row=4)

        self.label7 = Label(self.frame2, text='일')
        self.label7.grid(column=1, row=4)

        self.btn2 = Button(self.frame2, text='확인', command=self.on_btn2)
        self.btn2.grid(column=0, row=5, columnspan=2)

    # 날짜 선택 창 확인 버튼
    def on_btn2(self):
        try:
            year = int(self.entry1.get())
            month = int(self.entry2.get())
            day = int(self.entry3.get())
        except:
            # 숫자를 입력하지 않으면 오류 발생
            messagebox.showerror('오류', '연, 월, 일에 올바른 숫자를 입력하십시오')
            return

        try:
            date_obj = datetime.date(year, month, day)
        except:
            # 날짜가 성립하지 않으면 오류 발생
            messagebox.showerror('오류', '올바른 날짜를 입력하십시오')
            return

        # 아무 오류도 없으면 메뉴 출력 창으로 넘어간다.
        self.date = date_obj
        self.show_menu()
        self.frame2.pack_forget()
        self.frame3.pack()

    # 메뉴 출력 창
    def show_menu(self):
        self.frame3 = Frame(self.master)

        self.menu = get_menu(self.school[2], self.school[1], self.date.year, self.date.month, self.date.day)

        text = '{} {}년 {}월 {}일 급식'.format(
            school2str(self.school),
            self.date.year, self.date.month, self.date.day)

        # 급식이 없으면 없다고 알려준다.
        if self.menu:
            text += '입니다'
        else:
            text += '이 없습니다'
        self.label4 = Label(self.frame3, text=text)
        self.label4.grid(row=0, column=0, columnspan=2)

        # 메뉴를 조식, 중식, 석식 순으로 정렬한다.
        menuli = [(k, v) for k, v in self.menu.items()]
        menuli.sort(key=lambda x: {'조식': 0, '중식': 1, '석식': 2}.get(x[0], 4))

        self.canvas = Canvas(self.frame3)
        h = 0

        # 왼쪽부터 조식, 중식, 석식, ..기타 순으로 출력한다.
        for i in range(len(menuli)):
            title, menu = menuli[i]
            h = max(h, draw_menu(self.canvas, i*200, 200, title, menu))

        # canvas에 그린 그림이 너무 길면 최대 600으로 길이를 제한하고
        # 스크롤바를 붙인다.
        if h < 600:
            self.canvas.configure(height=h)
            self.canvas.grid(row=1, column=0, columnspan=2)
        else:
            self.canvas.configure(height=600, width=200*len(menuli))
            self.canvas.grid(row=1, column=0, sticky=N+S+E+W)

            self.yscrollbar = Scrollbar(self.frame3, orient=VERTICAL, command=self.canvas.yview)
            self.yscrollbar.grid(row=1, column=1, stick=N+S+E)

            self.canvas.config(scrollregion=self.canvas.bbox(ALL))
            self.canvas.config(yscrollcommand=self.yscrollbar.set)

        self.btn4 = Button(self.frame3, text='처음 화면으로', command=self.on_btn4)
        self.btn4.grid(row=2, column=0, columnspan=2)

    # 메뉴 출력 창 '처음 화면으로' 버튼
    def on_btn4(self):
        # 처음 화면으로 넘어간다.
        self.frame3.pack_forget()
        self.frame1.pack()


m = Tk()
m.title('전국 고등학교 급식')
bigfont = tkinter.font.Font(family='맑은 고딕', size=20, weight='bold')
midfont = tkinter.font.Font(family='맑은 고딕', size=15)
smallfont = tkinter.font.Font(family='맑은 고딕', size=8)
app = TheApp(m)
m.mainloop()
