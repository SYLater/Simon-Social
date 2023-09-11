from django.shortcuts import render

# Create your views here.
def tasks(request):
    userclasses = {
        "data": ['English','Math', 'Software Development', 'Systems', 'Business Management', 'Peace & Justice']}
    return render(request, "tasks/tasks.html", context=userclasses) #dir to html