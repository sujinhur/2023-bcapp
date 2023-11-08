
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt

import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from pandas import date_range


from .models import StepCount_Data

import json

# Create your views here.

def home(request):
    # 이번주 날짜
    current = datetime.date.today()
    weekday = datetime.datetime.today().weekday()
    startday = current - timedelta(days=weekday)
    # 이번주 DB id
    current_index = StepCount_Data.objects.get(date = current).id
    startday_index = StepCount_Data.objects.get(date = startday).id
    model_index = StepCount_Data.objects.latest('id').id

    # pagination
    page = request.GET.get("page", 1)
    # 이번주 데이터만 보여주기 위함
    if page == 1:
        datalist = StepCount_Data.objects.order_by('-date')[model_index - current_index:model_index - startday_index +1]
        paginator = Paginator(datalist, current_index - startday_index + 1)
    # 저번주 부터 1주일씩 데이터 보여줌  
    else:
        datalist = StepCount_Data.objects.order_by('-date')[model_index - startday_index - 6:]
        paginator = Paginator(datalist, 7)
    # url에 있는 현재 page값 get_page로 전달
    data = paginator.page(page)  
 
    # 날짜 범위 
    month = []
    day = []
    for i in reversed(data.object_list):
        month.append(i.date.month)
        day.append(i.date.day)

        date_range = str(month[0]) + "월 " + str(day[0]) + "일 ~" + str(month[-1]) + "월 " + str(day[-1]) + "일"

    stepcount = []
    for i in reversed(data.object_list):
        stepcount.append(i.stepCount)

    context = {
        "page" : data,
        "date_range" : date_range,
        "stepcount" : stepcount,
    }
    return render(request, 'visstep/home.html', context)


def month(request, num = 1):
    # 이번달 날짜
    current = datetime.date.today()
    current_day = current.day
    startday = current - timedelta(days=current_day -1)

    # next, prev page 번호 및 이에 따른 데이터 불러오기
    next_page_index = num + 1
    if num <= 1:
        prev_page_index = 1
        date = StepCount_Data.objects.filter(date__range=[startday, current])
  
    else:
        prev_page_index = num - 1
        if current.month - num + 1 <= 0:
            year_num = (current.month - num + 1)//(-12)
            month_num = -((current.month - num + 1)%(-12))
            date = StepCount_Data.objects.filter(date__year = str(current.year - year_num - 1), date__month = str(12 - month_num))
            if StepCount_Data.objects.get(date = str(date[0])).id == 1:
                next_page_index = num
        else:
            date = StepCount_Data.objects.filter(date__year = str(current.year), date__month = str(current.month - num + 1))

    days =[]
    stepcount = []
    for i in date:
        days.append(i.date.day)
        stepcount.append(i.stepCount)

    # 날짜 범위
    first_date = StepCount_Data.objects.get(date = str(date[0])).date
    date_range = str(first_date.year) + "년 " + str(first_date.month) + "월" 

    context = {
        "days" : days,
        "stepcount" : stepcount,
        "next_page_index" : next_page_index,
        "prev_page_index" : prev_page_index,
        "date_range" : date_range,
    }
    return render(request, 'visstep/month.html', context)


def year(request, num = 1):
    # 올해 날짜
    current = datetime.date.today()
    current_month = current.month
    current_day = current.day
    startday = current - relativedelta(months=current_month -1) - timedelta(days=current_day -1)

    # next, prev page 번호 및 이에 따른 데이터 불러오기
    next_page_index = num + 1
    if num <= 1:
        prev_page_index = 1
        date = StepCount_Data.objects.filter(date__range=[startday, current])
    else:
        prev_page_index = num - 1
        new_day = startday - relativedelta(years=num -1)
        date = StepCount_Data.objects.filter(date__range=[new_day, new_day + relativedelta(years=1) - timedelta(days=1)])
        if StepCount_Data.objects.get(date = str(date[0])).id == 1:
            next_page_index = num

    month = []
    stepcount = []
    num = 0
    count = 0
    for i in range(1,13):
        for j in date:
            if i == j.date.month:
                num = num + j.stepCount
                count = count + 1
            else:
                if num == 0:
                    break
                stepcount.append(num//count)
                num = 0
                count = 0
                i = i+1


    # 날짜 범위
    first_date = StepCount_Data.objects.get(date = str(date[0])).date
    date_range = str(first_date.year) + "년"


    context = {
        "stepcount" : stepcount,
        "next_page_index" : next_page_index,
        "prev_page_index" : prev_page_index,
        "date_range" : date_range,
    }
    return render(request, 'visstep/year.html', context)

def specify(request):
    current = datetime.date.today()
    weekday = datetime.datetime.today().weekday()
    startday = current - timedelta(days=weekday)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        date = StepCount_Data.objects.filter(date__range = [startday, current])
        date_range = str(startday.month) + "월 " + str(startday.day) + "일 ~ " + str(current.month) + "월 " + str(current.day) + "일"
        
        stepcount = []
        for i in date:
            stepcount.append(i.stepCount)

        context = {
        "date_range" :date_range,
        "stepcount" : stepcount, 

        }
        return render(request, 'visstep/specify.html', context)
    else:
        date = StepCount_Data.objects.filter(date__range = [start_date, end_date])

        first_date = StepCount_Data.objects.get(date = str(date[0])).date
        final_date = StepCount_Data.objects.get(date = str(date[len(date)-1])).date
        date_range = str(first_date.month) + "월 " + str(first_date.day) + "일 ~ " + str(final_date.month) + "월 " + str(final_date.day) + "일"
        
        context = {
        "date_range" :date_range,
        "date" : list(date.values()), 

        }   
        return JsonResponse(context)
    


def compare(request):
    current = datetime.date.today()
    weekday = datetime.datetime.today().weekday()
    startday = current - timedelta(days=weekday)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # print(start_date)

    if not start_date:

        data_1 = StepCount_Data.objects.filter(date__range = [startday, current])
        data_2 = StepCount_Data.objects.filter(date__range = [startday - timedelta(days= 7), startday - timedelta(days= 1)])

        stepcount_1 = []
        stepcount_2 = []
        for i in data_1:
            stepcount_1.append(i.stepCount)
        
        for i in data_2:
            stepcount_2.append(i.stepCount)

        date_range_1 = str(startday.month) + "월 " + str(startday.day) + "일 ~ " + str(current.month) + "월 " + str(current.day) + "일"
        date_range_2 = str(data_2[0].date.month) + "월 " + str(data_2[0].date.day) + "일 ~ " + str(data_2[6].date.month) + "월 " + str(data_2[6].date.day) + "일"

        context = {
            "date_range_1" :date_range_1,
            "date_range_2" :date_range_2,
            "stepcount_1" : stepcount_1,
            "stepcount_2" : stepcount_2,
        }
        return render(request, 'visstep/compare.html', context)
    
    else:
        date = StepCount_Data.objects.filter(date__range = [start_date, end_date])
        # print(date)
        first_date = StepCount_Data.objects.get(date = str(date[0])).date
        final_date = StepCount_Data.objects.get(date = str(date[len(date)-1])).date
        date_range = str(first_date.month) + "월 " + str(first_date.day) + "일 ~ " + str(final_date.month) + "월 " + str(final_date.day) + "일"
        context = {
        "date_range" :date_range,
        "date" : list(date.values()), 

        }   
        return JsonResponse(context)
    
## chatbot
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        input1 = request.POST['input1'].replace(" ","")

        date_1 = []
        date_2 = []
        stepcount_1 = []
        stepcount_2 = []
        legend_value = []
        answer = ""
        label = ""

        if "비교" in input1:
            label, date_1, date_2, stepcount_1, stepcount_2, legend_value, answer = chat_compare(input1)

        else:
            label, date_1, stepcount_1, answer = chat_specify(input1)


        output = dict()
        output['response'] = answer
        output['date_1'] = date_1
        output['date_2'] = date_2
        output['stepcount_1'] = stepcount_1
        output['stepcount_2'] = stepcount_2
        output['label'] = label 
        output['legend_value'] = legend_value
        return HttpResponse(json.dumps(output), status=200)


    
    else:
        return render(request, 'visstep/chat.html')


def chat_compare(input1):
    label = "Compare"
    date_1 = []
    date_2 = []
    stepcount_1 = []
    stepcount_2 = []

    # 23년 3월과 4월 비교
    if "3" in input1:
        legend_value = ["23년 4월", "23년 3월"]
        answer = "올해 3월과 4월 데이터 비교 결과입니다."
        for i in StepCount_Data.objects.raw("select * from stepcountData where date between '2023-04-01' and date('2023-04-01','+1 month','-1 days') ORDER BY (date) ASC"):
            date_1.append(str(int(str(i.date)[8:])))
            stepcount_1.append(i.stepCount)
        for i in StepCount_Data.objects.raw("select * from stepcountData where date between '2022-04-01' and date('2022-04-01','+1 month','-1 days') ORDER BY (date) ASC"):
            date_2.append(str(int(str(i.date)[8:])))
            stepcount_2.append(i.stepCount)   
    
    # 22년 4월과 23년 4월 비교
    else:
        legend_value = ["23년 4월", "22년 4월"]
        answer = "2022과 2023년 4월 데이터 비교 결과입니다."
        for i in StepCount_Data.objects.raw("select * from stepcountData where date between '2023-04-01' and date('2023-04-01','+1 month','-1 days') ORDER BY (date) ASC"):
            date_1.append(str(int(str(i.date)[8:])))
            stepcount_1.append(i.stepCount)
        for i in StepCount_Data.objects.raw("select * from stepcountData where date between '2023-03-01' and date('2023-03-01','+1 month','-1 days') ORDER BY (date) ASC"):
            date_2.append(str(int(str(i.date)[8:])))
            stepcount_2.append(i.stepCount) 
        

    return label, date_1, date_2, stepcount_1, stepcount_2, legend_value, answer


def chat_specify(input1):
    date_1 = []
    stepcount_1 = []

    if "이번주" in input1:
        label = "weeks"
        answer = "이번주 걸음 수 입니다."
        date_1, stepcount_1 = query_data("select * from stepcountData where date between date('now','-7 days','weekday 1') and date('now') ORDER BY (date) ASC")
        
    elif "이번달" in input1:
        label = "month"
        answer = "이번달 걸음 수 입니다."
        date_1, stepcount_1 = query_data("select * from stepcountData where date between date('now','start of month') and date('now') ORDER BY (date) ASC")

    elif "저번주" in input1:
        label = "weeks"
        answer = "저번주 걸음 수입니다."
        date_1, stepcount_1 = query_data("select * from stepcountData where date between date('now','-14 days','weekday 1') and date('now','-7 days','weekday 0') ORDER BY (date) ASC")
 
    elif "저번달" in input1:
        label = "month"
        answer = "저번달 걸음 수 입니다."
        date_1, stepcount_1 = query_data("select * from stepcountData where date between date('now','-1 month','start of month') and date('now','start of month','-1 days') ORDER BY (date) ASC")


    elif "올해" in input1:
        label = "avg_months"
        answer = "올해 걸음 수 입니다."
        date_1, stepcount_1 = query_month_data("select * from stepcountData where date between '2023-01-01' and date('now') ORDER BY (date) ASC")

    elif "3" in input1:
        label = "month"
        answer = "올해 3월 걸음 수 입니다."
        date_1, stepcount_1 = query_data("select * from stepcountData where date between '2023-03-01' and date('2023-03-01','+1 month','-1 days') ORDER BY (date) ASC")

    elif "4" in input1:
        label = "month"
        answer = "올해 4월 걸음 수 입니다."
        date_1, stepcount_1 = query_data("select * from stepcountData where date between '2023-04-01' and date('2023-04-01','+1 month','-1 days') ORDER BY (date) ASC")

    return label, date_1, stepcount_1, answer

def query_data(query):
    date_1 = []
    stepcount_1 = []
    for i in StepCount_Data.objects.raw(query):
            date_1.append(str(int(str(i.date)[8:])))
            stepcount_1.append(i.stepCount)

    return date_1, stepcount_1

def query_month_data(query):
    date_1 = []
    stepcount_1 = []
    tmp_stepcount = 0
    tmp = 0
    last_data = StepCount_Data.objects.raw(query)[-1].date

    for i in StepCount_Data.objects.raw(query):
        if i.date.day != 1:
            if len(date_1) == 0:
                date_1.append(str(int(str(i.date)[5:7])) + "월")
            elif date_1[-1] != str(int(str(i.date)[5:7])) + "월":
                date_1.append(str(int(str(i.date)[5:7])) + "월")
            tmp_stepcount = tmp_stepcount + int(i.stepCount)
            tmp = tmp + 1
            if i.date == last_data:
                stepcount_1.append(tmp_stepcount/tmp)

        else:
            if tmp_stepcount != 0:
                stepcount_1.append(tmp_stepcount/tmp)
                tmp_stepcount = 0
                tmp = 0
                tmp_stepcount = tmp_stepcount + int(i.stepCount)
                tmp = tmp + 1
            else:
                date_1.append(str(int(str(i.date)[5:7])) + "월")
                stepcount_1.append(i.stepCount)

    return date_1, stepcount_1